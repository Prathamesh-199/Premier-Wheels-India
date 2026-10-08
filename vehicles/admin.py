from django.contrib import admin

from .models import Enquiry, Vehicle, VehiclePhoto


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):

    list_display = (
        "make",
        "model",
        "year",
        "price",
        "mileage",
        "fuel_type",
        "transmission",
        "location",
        "seller_phone",
        "seller_email",
        "seller",
        "is_available",
        "created_at",
    )

    list_filter = (
        "fuel_type",
        "transmission",
        "year",
        "is_available",
    )

    search_fields = (
        "make",
        "model",
        "location",
        "seller_email",
        "seller__username",
    )


@admin.register(VehiclePhoto)
class VehiclePhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "vehicle", "created_at")
    list_filter = ("created_at",)
    search_fields = ("vehicle__make", "vehicle__model")


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = (
        "buyer_name",
        "buyer_phone",
        "vehicle",
        "created_at",
        "is_read",
    )
    list_filter = ("is_read", "created_at")
    search_fields = (
        "buyer_name",
        "buyer_phone",
        "vehicle__make",
        "vehicle__model",
    )
