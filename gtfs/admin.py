from django.contrib import admin
from .models import Agency, Stop, Route, Trip, StopTime

# Register your models here.

admin.site.register(Agency)
admin.site.register(Stop)
admin.site.register(Route)
admin.site.register(Trip)
admin.site.register(StopTime)
