from django.db import models
from catalog.models import Feed

# Create your models here.

class Agency(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="agencies")
    agency_gtfs_id = models.CharField(max_length=128)
    name = models.CharField(max_length=255)
    url = models.URLField(blank=True)
    timezone = models.CharField(max_length=64, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["feed", "agency_gtfs_id"], name="uniq_agency_per_feed")
        ]

    def __str__(self):
        return self.name

    @property
    def external_id(self) -> str:
        return f"{self.feed.name}:{self.agency_gtfs_id}"


class Stop(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="stops")
    stop_gtfs_id = models.CharField(max_length=128)
    name = models.CharField(max_length=255)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["feed", "stop_gtfs_id"], name="uniq_stop_per_feed")
        ]

    def __str__(self):
        return self.name

    @property
    def external_id(self) -> str:
        return f"{self.feed.name}:{self.stop_gtfs_id}"


class Route(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="routes")
    route_gtfs_id = models.CharField(max_length=128)
    short_name = models.CharField(max_length=64, blank=True)
    long_name = models.CharField(max_length=255, blank=True)
    agency = models.ForeignKey(Agency, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["feed", "route_gtfs_id"], name="uniq_route_per_feed")
        ]

    def __str__(self):
        return self.short_name or self.long_name or self.route_gtfs_id

    @property
    def external_id(self) -> str:
        return f"{self.feed.name}:{self.route_gtfs_id}"


class Trip(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="trips")
    trip_gtfs_id = models.CharField(max_length=128)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="trips")
    service_id = models.CharField(max_length=128, blank=True)
    headsign = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["feed", "trip_gtfs_id"], name="uniq_trip_per_feed")
        ]

    @property
    def external_id(self) -> str:
        return f"{self.feed.name}:{self.trip_gtfs_id}"


class StopTime(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="stop_times")
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name="stop_times")
    stop_sequence = models.PositiveIntegerField()
    arrival_time = models.CharField(max_length=16, blank=True)    # GTFS può avere 25:10:00
    departure_time = models.CharField(max_length=16, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["trip", "stop_sequence"], name="uniq_stopseq_per_trip")
        ]
        ordering = ["trip_id", "stop_sequence"]
