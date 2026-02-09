from django.conf import settings


def _publisher_qid(slug: str) -> str:
    return settings.FEED_PUBLISHER_QIDS[slug]


def _area_qid(slug: str) -> str:
    return settings.FEED_AREA_QIDS[slug]


def dataset_path(slug: str) -> str:
    pub = _publisher_qid(slug)
    area = _area_qid(slug)
    return f"/dataset/wd/{pub}/wd/{area}/"


def dataset_uri(slug: str) -> str:
    base = settings.PUBLIC_BASE_URL.rstrip("/")
    return base + dataset_path(slug)


def stop_uri(slug: str, stop_gtfs_id: str) -> str:
    base = settings.PUBLIC_BASE_URL.rstrip("/")
    pub = _publisher_qid(slug)
    area = _area_qid(slug)
    return f"{base}/resources/stop/wd/{pub}/wd/{area}/{stop_gtfs_id}"


def route_uri(slug: str, route_gtfs_id: str) -> str:
    base = settings.PUBLIC_BASE_URL.rstrip("/")
    pub = _publisher_qid(slug)
    area = _area_qid(slug)
    return f"{base}/resources/route/wd/{pub}/wd/{area}/{route_gtfs_id}"
