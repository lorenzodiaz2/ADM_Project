from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Feed
from gtfs.models import Stop, Route, Agency
from django.conf import settings


def _api_base_url(request) -> str:
    base = getattr(settings, "PUBLIC_API_BASE_URL", "").strip().rstrip("/")
    if base:
        return base
    # Usa lo stesso host della request corrente (dev: 127.0.0.1, prod: il tuo dominio)
    return request.build_absolute_uri("/").rstrip("/")


def _api_url(request, path: str) -> str:
    # path deve iniziare con "/" (es: "/api/catalog/roma/")
    return _api_base_url(request) + path


def catalog_list(request):
    feeds = Feed.objects.order_by("name")
    data = []
    for f in feeds:
        data.append({
            "name": f.name,
            "slug": f.slug,
            "provider": f.provider,
            "source_url": f.source_url,
        })
    return JsonResponse({"feeds": data})

def feed_detail(request, slug):
    feed = get_object_or_404(Feed, slug=slug)
    identifier = f"{settings.PUBLIC_BASE_URL}/dataset/{feed.slug}/"
    counts = {
        "agencies": Agency.objects.filter(feed=feed).count(),
        "stops": Stop.objects.filter(feed=feed).count(),
        "routes": Route.objects.filter(feed=feed).count(),
    }
    return JsonResponse({
        "feed": {
            "name": feed.name,
            "slug": feed.slug,
            "provider": feed.provider,
            "source_url": feed.source_url,
            "identifier": identifier,
        },
        "counts": counts,
    })

def _jsonld_context():
    # Prefissi e termini minimi per DCAT + DCTERMS + PROV + FOAF
    return {
        "dcat": "http://www.w3.org/ns/dcat#",
        "dct": "http://purl.org/dc/terms/",
        "prov": "http://www.w3.org/ns/prov#",
        "foaf": "http://xmlns.com/foaf/0.1/",
        "xsd": "http://www.w3.org/2001/XMLSchema#",

        "Catalog": "dcat:Catalog",
        "Dataset": "dcat:Dataset",
        "Distribution": "dcat:Distribution",

        "title": "dct:title",
        "description": "dct:description",
        "identifier": "dct:identifier",
        "conformsTo": {"@id": "dct:conformsTo", "@type": "@id"},

        "publisher": "dct:publisher",
        "license": "dct:license",
        "issued": {"@id": "dct:issued", "@type": "xsd:dateTime"},
        "modified": {"@id": "dct:modified", "@type": "xsd:dateTime"},

        "landingPage": {"@id": "dcat:landingPage", "@type": "@id"},
        "dataset": {"@id": "dcat:dataset", "@type": "@id"},
        "distribution": {"@id": "dcat:distribution", "@type": "@id"},
        "accessURL": {"@id": "dcat:accessURL", "@type": "@id"},
        "downloadURL": {"@id": "dcat:downloadURL", "@type": "@id"},

        "derivedFrom": {"@id": "prov:wasDerivedFrom", "@type": "@id"},

        "name": "foaf:name",

        "spatial": {"@id": "dct:spatial", "@type": "@id"},
        "homepage": {"@id": "foaf:homepage", "@type": "@id"},
        "Agent": "foaf:Agent",

        "keyword": "dcat:keyword",
        "language": "dct:language",
        "mediaType": "dcat:mediaType",
        "format": "dct:format",
    }


def _pages_dataset_id(slug: str) -> str:
    base = getattr(settings, "PUBLIC_BASE_URL", "").rstrip("/")
    return f"{base}/dataset/{slug}/"


def _spatial_uri_for_feed(feed):
    mapping = getattr(settings, "FEED_SPATIAL_URIS", {})
    return mapping.get(getattr(feed, "slug", ""), None)


def _publisher_homepage_for_feed(feed):
    mapping = getattr(settings, "FEED_PUBLISHER_HOMEPAGES", {})
    return mapping.get(getattr(feed, "slug", ""), None)


def _publisher_id_for_feed(feed):
    mapping = getattr(settings, "FEED_PUBLISHER_IDS", {})
    return mapping.get(getattr(feed, "slug", ""), None)



def _publisher_object(feed):
    provider = (getattr(feed, "provider", "") or "").strip()
    if not provider:
        return None

    homepage = _publisher_homepage_for_feed(feed)
    pub_id = _publisher_id_for_feed(feed)

    obj = {
        "@type": "foaf:Agent",
        "name": provider,
    }

    # Se abbiamo un identificatore pubblico per il publisher, lo usiamo come @id
    if pub_id:
        obj["@id"] = pub_id

    # Homepage qualificata (foaf:homepage) se disponibile
    if homepage:
        obj["homepage"] = homepage

    return obj



def _license_url_for_feed(feed):
    # Mettiamo CC BY 4.0 come default: cambialo in settings se vuoi precisione per dataset
    default_license = "https://creativecommons.org/licenses/by/4.0/"
    mapping = getattr(settings, "FEED_LICENSE_URLS", {})
    slug = getattr(feed, "slug", "")
    return mapping.get(slug, default_license)


def _latest_feed_version_info(feed):
    # Best-effort: se esiste FeedVersion, includiamo issued/modified e sha256
    try:
        from catalog.models import FeedVersion
    except Exception:
        return {}

    fv = FeedVersion.objects.filter(feed=feed).order_by("-imported_at").first()
    if not fv:
        return {}

    out = {}
    imported_at = getattr(fv, "imported_at", None)
    if imported_at is not None:
        # ISO 8601
        out["modified"] = imported_at.isoformat()

    sha256 = getattr(fv, "sha256", None)
    if sha256:
        # dct:identifier è già usato per l'ID globale del dataset, quindi mettiamo sha in description estesa
        out["_sha256"] = sha256

    return out


def _dataset_jsonld(request, feed):
    slug = feed.slug
    dataset_id = _pages_dataset_id(slug)

    # Link di accesso: API JSON “normale” già esistente
    api_detail = _api_url(request, f"/api/catalog/{slug}/")
    api_routes = _api_url(request, f"/api/routes/?feed={slug}")
    api_stop_search = _api_url(request, f"/api/stops/search/?feed={slug}&q=TERM")
    api_ld = _api_url(request, f"/api/catalog/{slug}.jsonld")


    version_info = _latest_feed_version_info(feed)
    sha256 = version_info.pop("_sha256", None)

    desc = (getattr(feed, "name", "") or "").strip()
    # Descrizione più utile (puoi personalizzarla dopo)
    long_desc = (
        f"GTFS static dataset for {feed.name}. "
        f"Includes agency, stops, routes. "
        f"Local API endpoints provide JSON access."
    )
    if sha256:
        long_desc += f" Latest import SHA256: {sha256}."

    profile_url = getattr(settings, "PUBLIC_METADATA_PROFILE_URL", None)
    gtfs_url = getattr(settings, "GTFS_SCHEDULE_REFERENCE_URL", None)

    conforms = []
    if profile_url:
        conforms.append(profile_url)
    if gtfs_url:
        conforms.append(gtfs_url)

    obj = {
        "@id": dataset_id,
        "@type": "Dataset",
        "identifier": dataset_id,
        "title": f"GTFS {feed.name}",
        "description": long_desc,
        "landingPage": dataset_id,
        "conformsTo": conforms,
    }

    spatial_uri = _spatial_uri_for_feed(feed)
    if spatial_uri:
        obj["spatial"] = spatial_uri

    pub = _publisher_object(feed)
    if pub:
        obj["publisher"] = pub

    src = (getattr(feed, "source_url", "") or "").strip()
    if src:
        obj["derivedFrom"] = src

    obj["license"] = _license_url_for_feed(feed)

    # Aggiungiamo modified (se disponibile) da FeedVersion
    obj.update(version_info)

    # Distributions: API JSON
    distributions = [
        {
            "@type": "Distribution",
            "accessURL": api_detail,
            "title": "Dataset metadata (JSON API)",
        },
        {
            "@type": "Distribution",
            "accessURL": api_ld,
            "title": "Dataset metadata (JSON-LD)",
        },
        {
            "@type": "Distribution",
            "accessURL": api_routes,
            "title": "Routes list (JSON API)",
        },
        {
            "@type": "Distribution",
            "accessURL": api_stop_search,
            "title": "Stop search (JSON API) - replace TERM",
        },
    ]

    # Aggiungi anche una distribution “globale” basata sulla fonte ufficiale (fortissima contro contestazioni)
    if src:
        distributions.append(
            {
                "@type": "Distribution",
                "accessURL": src,
                "title": "Official source page (GTFS provider)",
                "mediaType": "text/html",
            }
        )

    obj["distribution"] = distributions
    obj["language"] = "it"
    obj["keyword"] = ["gtfs", "public transport", feed.name.lower(), "open data", "schedule"]

    return obj


def catalog_list_jsonld(request):
    from .models import Feed

    feeds = Feed.objects.order_by("name")
    catalog_id = _api_url(request, "/api/catalog.jsonld")

    datasets = []
    for f in feeds:
        datasets.append(_dataset_jsonld(request, f))

    payload = {
        "@context": _jsonld_context(),
        "@id": catalog_id,
        "@type": "Catalog",
        "title": "ADM_Project - FAIRTransit Hub Catalog",
        "description": "Public catalog of GTFS datasets (Roma, Milano) with JSON-LD metadata.",
        "dataset": datasets,
        "conformsTo": settings.PUBLIC_METADATA_PROFILE_URL,
    }
    return JsonResponse(payload, content_type="application/ld+json")


def feed_detail_jsonld(request, slug):
    from .models import Feed
    feed = Feed.objects.filter(slug=slug).first()
    if not feed:
        return JsonResponse({"error": "Feed not found"}, status=404, content_type="application/ld+json")

    payload = {
        "@context": _jsonld_context(),
    }
    payload.update(_dataset_jsonld(request, feed))
    return JsonResponse(payload, content_type="application/ld+json")
