from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render

from catalog.models import Feed
from gtfs.models import Stop, Route


def _split_key(key: str):
    # key è del tipo "roma:1234"
    if ":" not in key:
        return None, None
    feed_slug, gtfs_id = key.split(":", 1)
    feed_slug = (feed_slug or "").strip()
    gtfs_id = (gtfs_id or "").strip()
    if not feed_slug or not gtfs_id:
        return None, None
    return feed_slug, gtfs_id


def _public_id_url(kind: str, feed_slug: str, gtfs_id: str) -> str:
    base = getattr(settings, "PUBLIC_BASE_URL", "").rstrip("/")
    return f"{base}/id/{kind}/{feed_slug}:{gtfs_id}"


def stop_id_resolver(request, key: str):
    feed_slug, stop_gtfs_id = _split_key(key)
    if not feed_slug:
        return HttpResponseBadRequest("Invalid stop key. Expected: feed:stop_gtfs_id")

    feed = get_object_or_404(Feed, slug=feed_slug)

    # Se il tuo campo non si chiama stop_gtfs_id, cambia qui
    stop = get_object_or_404(Stop, feed=feed, stop_gtfs_id=stop_gtfs_id)

    identifier = _public_id_url("stop", feed_slug, stop_gtfs_id)
    dataset_landing = f"{settings.PUBLIC_BASE_URL.rstrip('/')}/dataset/{feed_slug}/"

    fmt = (request.GET.get("format") or "").lower()

    if fmt == "json":
        return JsonResponse(
            {
                "id": identifier,
                "type": "Stop",
                "feed": feed_slug,
                "stop_gtfs_id": stop_gtfs_id,
                "name": getattr(stop, "stop_name", ""),
                "lat": getattr(stop, "stop_lat", None),
                "lon": getattr(stop, "stop_lon", None),
                "dataset": dataset_landing,
            }
        )

    if fmt == "jsonld":
        payload = {
            "@context": {
                "schema": "https://schema.org/",
                "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#",
                "dct": "http://purl.org/dc/terms/",
                "name": "schema:name",
                "identifier": "dct:identifier",
                "isPartOf": {"@id": "dct:isPartOf", "@type": "@id"},
                "lat": "geo:lat",
                "lon": "geo:long",
            },
            "@id": identifier,
            "@type": "schema:BusStop",
            "identifier": identifier,
            "name": getattr(stop, "stop_name", ""),
            "lat": getattr(stop, "stop_lat", None),
            "lon": getattr(stop, "stop_lon", None),
            "isPartOf": dataset_landing,
        }
        return JsonResponse(payload, content_type="application/ld+json")

    # Default: HTML
    return render(
        request,
        "gtfs/stop_id_detail.html",
        {
            "feed": feed,
            "stop": stop,
            "identifier": identifier,
            "dataset_landing": dataset_landing,
        },
    )


def route_id_resolver(request, key: str):
    feed_slug, route_gtfs_id = _split_key(key)
    if not feed_slug:
        return HttpResponseBadRequest("Invalid route key. Expected: feed:route_gtfs_id")

    feed = get_object_or_404(Feed, slug=feed_slug)

    # Se il tuo campo non si chiama route_gtfs_id, cambia qui
    route = get_object_or_404(Route, feed=feed, route_gtfs_id=route_gtfs_id)

    identifier = _public_id_url("route", feed_slug, route_gtfs_id)
    dataset_landing = f"{settings.PUBLIC_BASE_URL.rstrip('/')}/dataset/{feed_slug}/"

    fmt = (request.GET.get("format") or "").lower()

    if fmt == "json":
        return JsonResponse(
            {
                "id": identifier,
                "type": "Route",
                "feed": feed_slug,
                "route_gtfs_id": route_gtfs_id,
                "short_name": getattr(route, "route_short_name", ""),
                "long_name": getattr(route, "route_long_name", ""),
                "route_type": getattr(route, "route_type", None),
                "dataset": dataset_landing,
            }
        )

    if fmt == "jsonld":
        payload = {
            "@context": {
                "schema": "https://schema.org/",
                "dct": "http://purl.org/dc/terms/",
                "name": "schema:name",
                "identifier": "dct:identifier",
                "isPartOf": {"@id": "dct:isPartOf", "@type": "@id"},
            },
            "@id": identifier,
            "@type": "schema:Trip",
            "identifier": identifier,
            "name": (getattr(route, "route_long_name", "") or getattr(route, "route_short_name", "")),
            "isPartOf": dataset_landing,
        }
        return JsonResponse(payload, content_type="application/ld+json")

    return render(
        request,
        "gtfs/route_id_detail.html",
        {
            "feed": feed,
            "route": route,
            "identifier": identifier,
            "dataset_landing": dataset_landing,
        },
    )
