from django.urls import path

from . import views


app_name = "vehicles"


urlpatterns = [
    path(
        "",
        views.home,
        name="home",
    ),
    path(
        "vehicle/<int:pk>/",
        views.vehicle_detail,
        name="vehicle_detail",
    ),
    path(
        "premier-match/",
        views.premier_match,
        name="premier_match",
    ),
    path(
        "vehicle/<int:pk>/contact/",
        views.contact_seller,
        name="contact_seller",
    ),
    path(
        "favorites/",
        views.favorites,
        name="favorites",
    ),
    path(
        "vehicle/<int:pk>/favorite/",
        views.toggle_favorite,
        name="toggle_favorite",
    ),
    path(
        "login/",
        views.login_view,
        name="login",
    ),
    path(
        "register/",
        views.register_view,
        name="register",
    ),
    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),
    path(
        "add-vehicle/",
        views.add_vehicle,
        name="add_vehicle",
    ),
    path(
        "dashboard/",
        views.dashboard,
        name="dashboard",
    ),
    path(
        "edit-vehicle/<int:pk>/",
        views.edit_vehicle,
        name="edit_vehicle",
    ),
    path(
        "delete-vehicle/<int:pk>/",
        views.delete_vehicle,
        name="delete_vehicle",
    ),
]
