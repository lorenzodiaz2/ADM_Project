from django.urls import path
from . import views
from . import id_views
urlpatterns = [
    path("stops/search/", views.stop_search_view, name="stop_search"),
    path("routes/", views.route_list_view, name="route_list"),
    path("id/stop/<str:key>/", id_views.stop_id_resolver, name="id_stop_resolver"),
    path("id/route/<str:key>/", id_views.route_id_resolver, name="id_route_resolver"),
]
