from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Vehicle(models.Model):

    FUEL_CHOICES = [
        ("Petrol", "Petrol"),
        ("Diesel", "Diesel"),
        ("CNG", "CNG"),
        ("Electric", "Electric"),
        ("Hybrid", "Hybrid"),
    ]

    TRANSMISSION_CHOICES = [
        ("Manual", "Manual"),
        ("Automatic", "Automatic"),
        ("AMT", "AMT"),
        ("DCT", "DCT"),
        ("CVT", "CVT"),
    ]

    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="vehicles"
    )

    make = models.CharField(max_length=100)

    model = models.CharField(max_length=100)

    year = models.PositiveIntegerField()

    price = models.PositiveIntegerField(
        validators=[MinValueValidator(50000)]
    )

    mileage = models.PositiveIntegerField()

    engine_specs = models.CharField(max_length=200)

    fuel_type = models.CharField(
        max_length=20,
        choices=FUEL_CHOICES,
        default="Petrol"
    )

    transmission = models.CharField(
        max_length=20,
        choices=TRANSMISSION_CHOICES,
        default="Manual"
    )

    location = models.CharField(
        max_length=150,
        blank=True
    )

    seller_phone = models.CharField(
        max_length=15,
        blank=True
    )

    seller_email = models.EmailField(
        max_length=254,
        blank=True
    )

    short_description = models.TextField()

    image = models.ImageField(
        upload_to="vehicles/",
        blank=True,
        null=True
    )

    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.make} {self.model} ({self.year})"

    class Meta:
        ordering = ["-created_at"]

class VehiclePhoto(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="photos",
    )

    image = models.ImageField(
        upload_to="vehicles/gallery/",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.vehicle} - Photo {self.pk}"


class Enquiry(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="enquiries",
    )

    buyer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="car_enquiries",
    )

    buyer_name = models.CharField(max_length=100)

    buyer_phone = models.CharField(max_length=15)

    message = models.TextField(max_length=1000)

    created_at = models.DateTimeField(auto_now_add=True)

    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Enquiry from {self.buyer_name} - {self.vehicle}"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite_cars",
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="favorited_by",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "vehicle"],
                name="unique_user_vehicle_favorite",
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.vehicle}"
