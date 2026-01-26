from django.shortcuts import get_object_or_404, render
from .models import Feed
from gtfs.models import Stop, Route, Agency

# Create your views here.

def catalog_view(request):
    feeds = Feed.objects.order_by("name")
    return render(request, "catalog/catalog.html", {"feeds": feeds})

def feed_detail_view(request, slug):
    feed = get_object_or_404(Feed, slug=slug)

    counts = {
        "agencies": Agency.objects.filter(feed=feed).count(),
        "stops": Stop.objects.filter(feed=feed).count(),
        "routes": Route.objects.filter(feed=feed).count(),
    }

    return render(request, "catalog/feed_detail.html", {"feed": feed, "counts": counts})
