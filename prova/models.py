from django.db import models


class Feed(models.Model):
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=100)


class FeedVersion(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="versions")
    imported_at = models.DateTimeField(auto_now_add=True)


class Agency(models.Model):
    feed_version = models.ForeignKey(FeedVersion, on_delete=models.CASCADE, related_name="agencies")
    agency_gtfs_id = models.CharField(max_length=128)
    name = models.CharField(max_length=255, blank=True)


class Stop(models.Model):
    feed_version = models.ForeignKey(FeedVersion, on_delete=models.CASCADE, related_name="stops")
    stop_gtfs_id = models.CharField(max_length=128)
    name = models.CharField(max_length=255, blank=True)


class Route(models.Model):
    feed_version = models.ForeignKey(FeedVersion, on_delete=models.CASCADE, related_name="routes")
    route_gtfs_id = models.CharField(max_length=128)


class Trip(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="trips")
    trip_gtfs_id = models.CharField(max_length=128)


class StopTime(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="stop_times")
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name="stop_times")
    stop_sequence = models.PositiveIntegerField()

