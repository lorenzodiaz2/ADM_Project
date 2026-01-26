from django.shortcuts import render
from catalog.models import Feed
from .models import Stop, Route

# Create your views here.

def stop_search_view(request):
    feeds = Feed.objects.order_by("name")
    feed_slug = request.GET.get("feed", "").strip()
    q = request.GET.get("q", "").strip()

    selected_feed = None
    results = []

    if feed_slug:
        selected_feed = Feed.objects.filter(slug=feed_slug).first()
        if selected_feed and q:
            results = Stop.objects.filter(feed=selected_feed, name__icontains=q).order_by("name")[:200]

    return render(request, "gtfs/stop_search.html", {
        "feeds": feeds,
        "selected_feed": selected_feed,
        "feed_slug": feed_slug,
        "q": q,
        "results": results,
    })

def route_list_view(request):
    feeds = Feed.objects.order_by("name")
    feed_slug = request.GET.get("feed", "").strip()

    selected_feed = None
    routes = []

    if feed_slug:
        selected_feed = Feed.objects.filter(slug=feed_slug).first()
        if selected_feed:
            routes = Route.objects.filter(feed=selected_feed).order_by("short_name", "long_name")[:500]

    return render(request, "gtfs/route_list.html", {
        "feeds": feeds,
        "selected_feed": selected_feed,
        "feed_slug": feed_slug,
        "routes": routes,
    })
