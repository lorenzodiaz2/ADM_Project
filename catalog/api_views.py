from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Feed
from gtfs.models import Stop, Route, Agency

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
        },
        "counts": counts,
    })
