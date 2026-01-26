from django.urls import path
from . import views

urlpatterns = [
    path("", views.catalog_view, name="catalog"),
    path("<slug:slug>/", views.feed_detail_view, name="feed_detail"),
]
