import csv
import hashlib
import io
import zipfile
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Feed, FeedVersion
from gtfs.models import Agency, Stop, Route, Trip, StopTime


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_txt_from_zip(zf: zipfile.ZipFile, name: str):
    """Return an iterator of dict rows for a GTFS txt file, or None if missing."""
    try:
        raw = zf.read(name)
    except KeyError:
        return None
    # GTFS is usually UTF-8; fallback to latin-1 if needed
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    return csv.DictReader(io.StringIO(text))


class Command(BaseCommand):
    help = "Import a GTFS zip into the database (core tables)."

    def add_arguments(self, parser):
        parser.add_argument("zip_path", type=str, help="Path to GTFS zip (e.g. data/raw/milan_gtfs.zip)")
        parser.add_argument("--feed", required=True, type=str, help="Feed name (e.g. Milano, Roma)")
        parser.add_argument("--source-url", default="", type=str, help="Optional source URL for the feed")
        parser.add_argument("--limit-stop-times", default=0, type=int,
                            help="Optional limit for stop_times rows (0 = no limit). Useful for demo.")

    @transaction.atomic
    def handle(self, *args, **opts):
        zip_path = Path(opts["zip_path"]).resolve()
        if not zip_path.exists():
            raise CommandError(f"Zip not found: {zip_path}")

        feed_name = opts["feed"].strip()
        source_url = opts["source_url"].strip()
        limit_stop_times = int(opts["limit_stop_times"])

        feed, created = Feed.objects.get_or_create(
            name=feed_name,
            defaults={"source_url": source_url},
        )
        if (not created) and source_url and feed.source_url != source_url:
            feed.source_url = source_url
            feed.save(update_fields=["source_url"])

        fv = FeedVersion.objects.create(
            feed=feed,
            gtfs_zip_name=zip_path.name,
            sha256=_sha256(zip_path),
        )
        self.stdout.write(self.style.SUCCESS(f"FeedVersion created: {fv}"))

        with zipfile.ZipFile(zip_path, "r") as zf:
            # ---------- agency ----------
            rows = _read_txt_from_zip(zf, "agency.txt")
            if rows is None:
                self.stdout.write(self.style.WARNING("agency.txt not found (skipping)"))
            else:
                n = 0
                for r in rows:
                    gtfs_id = (r.get("agency_id") or "").strip() or "default"
                    Agency.objects.update_or_create(
                        feed=feed,
                        agency_gtfs_id=gtfs_id,
                        defaults={
                            "name": (r.get("agency_name") or "").strip(),
                            "url": (r.get("agency_url") or "").strip(),
                            "timezone": (r.get("agency_timezone") or "").strip(),
                        },
                    )
                    n += 1
                self.stdout.write(self.style.SUCCESS(f"Imported agencies: {n}"))

            # ---------- stops ----------
            rows = _read_txt_from_zip(zf, "stops.txt")
            if rows is None:
                raise CommandError("stops.txt not found (required)")
            else:
                n = 0
                for r in rows:
                    stop_id = (r.get("stop_id") or "").strip()
                    if not stop_id:
                        continue
                    lat = r.get("stop_lat")
                    lon = r.get("stop_lon")
                    Stop.objects.update_or_create(
                        feed=feed,
                        stop_gtfs_id=stop_id,
                        defaults={
                            "name": (r.get("stop_name") or "").strip(),
                            "lat": float(lat) if lat not in (None, "",) else None,
                            "lon": float(lon) if lon not in (None, "",) else None,
                        },
                    )
                    n += 1
                self.stdout.write(self.style.SUCCESS(f"Imported stops: {n}"))

            # ---------- routes ----------
            rows = _read_txt_from_zip(zf, "routes.txt")
            if rows is None:
                raise CommandError("routes.txt not found (required)")
            else:
                # Build agency map
                agencies = {a.agency_gtfs_id: a for a in Agency.objects.filter(feed=feed)}
                n = 0
                for r in rows:
                    route_id = (r.get("route_id") or "").strip()
                    if not route_id:
                        continue
                    agency_id = (r.get("agency_id") or "").strip() or None
                    agency = agencies.get(agency_id) if agency_id else None
                    Route.objects.update_or_create(
                        feed=feed,
                        route_gtfs_id=route_id,
                        defaults={
                            "short_name": (r.get("route_short_name") or "").strip(),
                            "long_name": (r.get("route_long_name") or "").strip(),
                            "agency": agency,
                        },
                    )
                    n += 1
                self.stdout.write(self.style.SUCCESS(f"Imported routes: {n}"))

            # ---------- trips ----------
            rows = _read_txt_from_zip(zf, "trips.txt")
            if rows is None:
                raise CommandError("trips.txt not found (required)")
            else:
                routes = {rt.route_gtfs_id: rt for rt in Route.objects.filter(feed=feed)}
                n = 0
                for r in rows:
                    trip_id = (r.get("trip_id") or "").strip()
                    route_id = (r.get("route_id") or "").strip()
                    if not trip_id or not route_id:
                        continue
                    route = routes.get(route_id)
                    if route is None:
                        continue
                    Trip.objects.update_or_create(
                        feed=feed,
                        trip_gtfs_id=trip_id,
                        defaults={
                            "route": route,
                            "service_id": (r.get("service_id") or "").strip(),
                            "headsign": (r.get("trip_headsign") or "").strip(),
                        },
                    )
                    n += 1
                self.stdout.write(self.style.SUCCESS(f"Imported trips: {n}"))

            # ---------- stop_times ----------
            rows = _read_txt_from_zip(zf, "stop_times.txt")
            if rows is None:
                raise CommandError("stop_times.txt not found (required)")
            else:
                # Build maps for FK resolution
                trips = {t.trip_gtfs_id: t for t in Trip.objects.filter(feed=feed)}
                stops = {s.stop_gtfs_id: s for s in Stop.objects.filter(feed=feed)}
                n = 0
                for r in rows:
                    if limit_stop_times and n >= limit_stop_times:
                        break
                    trip_id = (r.get("trip_id") or "").strip()
                    stop_id = (r.get("stop_id") or "").strip()
                    seq = (r.get("stop_sequence") or "").strip()
                    if not trip_id or not stop_id or not seq:
                        continue
                    trip = trips.get(trip_id)
                    stop = stops.get(stop_id)
                    if trip is None or stop is None:
                        continue
                    StopTime.objects.update_or_create(
                        trip=trip,
                        stop_sequence=int(seq),
                        defaults={
                            "stop": stop,
                            "arrival_time": (r.get("arrival_time") or "").strip(),
                            "departure_time": (r.get("departure_time") or "").strip(),
                        },
                    )
                    n += 1
                self.stdout.write(self.style.SUCCESS(f"Imported stop_times: {n}"))

        self.stdout.write(self.style.SUCCESS("Done."))
