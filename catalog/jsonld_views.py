import json
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from catalog.models import Feed
from catalog.dataset_metadata import DATASET_METADATA

DCAT = "https://www.w3.org/ns/dcat#"
DCT = "http://purl.org/dc/terms/"
PROV = "http://www.w3.org/ns/prov#"
FOAF = "http://xmlns.com/foaf/0.1/"
XSD = "http://www.w3.org/2001/XMLSchema#"


def _jsonld_response(payload: dict) -> HttpResponse:
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    return HttpResponse(body, content_type="application/ld+json; charset=utf-8")


def _dataset_identifier(slug: str) -> str:
    base = getattr(settings, "PUBLIC_BASE_URL", "").rstrip("/")
    return f"{base}/dataset/{slug}/"


def _latest_import_info(feed: Feed) -> dict:
    """
    Best-effort: if FeedVersion exists, include modified date and sha256.
    If fields/models differ, it simply returns empty info (no crash).
    """
    info = {}
    try:
        from catalog.models import FeedVersion  # imported here to avoid hard dependency if renamed

        fv = FeedVersion.objects.filter(feed=feed).order_by("-imported_at").first()
        if fv is None:
            return info

        imported_at = getattr(fv, "imported_at", None)
        sha256 = getattr(fv, "sha256", None)

        if imported_at is not None:
            # ISO format for JSON-LD (xsd:dateTime)
            info["modified"] = imported_at.isoformat()
        if sha256:
            info["sha256"] = str(sha256)
    except Exception:
        return info
    return info


def catalog_jsonld(request):

    """
    DCAT Catalog listing the datasets.
    URL: /api/catalog.jsonld
    """
    catalog_id = request.build_absolute_uri("/api/catalog.jsonld")
    datasets = []
    for feed in Feed.objects.order_by("name"):
        slug = feed.slug
        ds_id = _dataset_identifier(slug)

        meta = DATASET_METADATA.get(slug, {})
        title = meta.get("title") or feed.name

        datasets.append({
            "@id": ds_id,
            "@type": "dcat:Dataset",
            "dct:title": title,
            "dcat:landingPage": {"@id": ds_id},
        })

    payload = {
        "@context": {
            "dcat": DCAT,
            "dct": DCT,
            "prov": PROV,
            "foaf": FOAF,
            "xsd": XSD,
        },
        "@id": catalog_id,
        "@type": "dcat:Catalog",
        "dct:title": "FAIRTransit Hub - Dataset Catalog",
        "dct:description": "Public catalog of GTFS datasets (Roma and Milano) with persistent identifiers.",
        "dcat:dataset": datasets,
    }
    return _jsonld_response(payload)


def feed_metadata_jsonld(request, slug: str):
    """
    DCAT Dataset metadata for a specific feed.
    URL: /api/catalog/<slug>/metadata.jsonld
    """
    feed = get_object_or_404(Feed, slug=slug)
    ds_id = _dataset_identifier(feed.slug)
    meta = DATASET_METADATA.get(feed.slug, {})

    title = meta.get("title") or feed.name
    description = meta.get("description") or ""
    source_url = meta.get("source_url") or getattr(feed, "source_url", "") or ""
    license_url = meta.get("license_url") or ""
    spatial_name = meta.get("spatial_name") or feed.name
    publisher_name = meta.get("publisher_name") or getattr(feed, "provider", "") or ""
    publisher_url = meta.get("publisher_url")

    # Build absolute URLs for the API distributions (works in dev; in prod it becomes your real host)
    api_detail = request.build_absolute_uri(f"/api/catalog/{feed.slug}/")
    api_routes = request.build_absolute_uri(f"/api/routes/?feed={feed.slug}")
    api_stops_example = request.build_absolute_uri(f"/api/stops/search/?feed={feed.slug}&q=termini")

    import_info = _latest_import_info(feed)

    dataset = {
        "@context": {
            "dcat": DCAT,
            "dct": DCT,
            "prov": PROV,
            "foaf": FOAF,
            "xsd": XSD,
        },
        "@id": ds_id,
        "@type": "dcat:Dataset",
        "dct:title": title,
        "dct:description": description,
        "dcat:landingPage": {"@id": ds_id},
    }

    if publisher_name:
        publisher_obj = {
            "@type": "foaf:Organization",
            "foaf:name": publisher_name,
        }
        if publisher_url:
            publisher_obj["foaf:homepage"] = {"@id": publisher_url}
        dataset["dct:publisher"] = publisher_obj

    if license_url:
        dataset["dct:license"] = {"@id": license_url}

    if spatial_name:
        dataset["dct:spatial"] = spatial_name

    if source_url:
        dataset["prov:wasDerivedFrom"] = {"@id": source_url}

    if import_info.get("modified"):
        dataset["dct:modified"] = {"@value": import_info["modified"], "@type": "xsd:dateTime"}

    if import_info.get("sha256"):
        dataset["dct:identifier"] = f"sha256:{import_info['sha256']}"

    # Distributions: API endpoints + source page
    distributions = [
        {
            "@type": "dcat:Distribution",
            "dct:title": "Feed detail (JSON API)",
            "dcat:accessURL": {"@id": api_detail},
            "dct:format": "application/json",
        },
        {
            "@type": "dcat:Distribution",
            "dct:title": "Routes list (JSON API)",
            "dcat:accessURL": {"@id": api_routes},
            "dct:format": "application/json",
        },
        {
            "@type": "dcat:Distribution",
            "dct:title": "Stops search example (JSON API)",
            "dcat:accessURL": {"@id": api_stops_example},
            "dct:format": "application/json",
        },
    ]

    if source_url:
        distributions.append({
            "@type": "dcat:Distribution",
            "dct:title": "Source page",
            "dcat:accessURL": {"@id": source_url},
            "dct:format": "text/html",
        })

    dataset["dcat:distribution"] = distributions

    return _jsonld_response(dataset)
