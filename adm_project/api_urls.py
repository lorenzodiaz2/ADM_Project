from django.urls import path
from catalog import api_views as catalog_api
from gtfs import api_views as gtfs_api

urlpatterns = [
    path("catalog/", catalog_api.catalog_list, name="api_catalog"),
    path("catalog/<slug:slug>/", catalog_api.feed_detail, name="api_feed_detail"),
    path("stops/search/", gtfs_api.stop_search, name="api_stop_search"),
    path("routes/", gtfs_api.route_list, name="api_route_list"),
    path("catalog.jsonld", catalog_api.catalog_list_jsonld, name="api_catalog_jsonld"),
    path("catalog/<slug:slug>.jsonld", catalog_api.feed_detail_jsonld, name="api_feed_detail_jsonld"),
]
