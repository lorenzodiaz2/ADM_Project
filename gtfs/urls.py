from django.urls import path
from . import views

urlpatterns = [
    path("stops/search/", views.stop_search_view, name="stop_search"),
    path("routes/", views.route_list_view, name="route_list"),
]
