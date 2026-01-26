from django.http import JsonResponse
from catalog.models import Feed
from .models import Stop, Route

def stop_search(request):
    feed_slug = (request.GET.get("feed") or "").strip()
    q = (request.GET.get("q") or "").strip()

    if not feed_slug or not q:
        return JsonResponse(
            {"error": "Missing required parameters: feed, q"},
            status=400
        )

    feed = Feed.objects.filter(slug=feed_slug).first()
    if not feed:
        return JsonResponse({"error": "Feed not found"}, status=404)

    qs = Stop.objects.filter(feed=feed, name__icontains=q).order_by("name")[:200]
    results = [{
        "id": s.id,
        "stop_gtfs_id": s.stop_gtfs_id,
        "name": s.name,
        "lat": s.lat,
        "lon": s.lon,
        "external_id": f"{feed.slug}:{s.stop_gtfs_id}",
    } for s in qs]

    return JsonResponse({
        "feed": {"name": feed.name, "slug": feed.slug},
        "query": q,
        "count": len(results),
        "results": results,
    })

def route_list(request):
    feed_slug = (request.GET.get("feed") or "").strip()

    if not feed_slug:
        return JsonResponse(
            {"error": "Missing required parameter: feed"},
            status=400
        )

    feed = Feed.objects.filter(slug=feed_slug).first()
    if not feed:
        return JsonResponse({"error": "Feed not found"}, status=404)

    qs = Route.objects.filter(feed=feed).order_by("short_name", "long_name")[:500]
    routes = [{
        "id": r.id,
        "route_gtfs_id": r.route_gtfs_id,
        "short_name": r.short_name,
        "long_name": r.long_name,
        "external_id": f"{feed.slug}:{r.route_gtfs_id}",
    } for r in qs]

    return JsonResponse({
        "feed": {"name": feed.name, "slug": feed.slug},
        "count": len(routes),
        "routes": routes,
    })
