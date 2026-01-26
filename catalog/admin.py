from django.contrib import admin
from .models import Feed, FeedVersion

# Register your models here.

admin.site.register(Feed)
admin.site.register(FeedVersion)
