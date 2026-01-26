from django.db import models

# Create your models here.

class Feed(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50, unique=True, null=True, blank=True)
    provider = models.CharField(max_length=200, blank=True)
    source_url = models.URLField(blank=True)

    def __str__(self):
        return self.name

class FeedVersion(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="versions")
    imported_at = models.DateTimeField(auto_now_add=True)
    gtfs_zip_name = models.CharField(max_length=255)  # nome file zip
    sha256 = models.CharField(max_length=64, blank=True)  # opzionale
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.feed.name} @ {self.imported_at:%Y-%m-%d %H:%M}"
