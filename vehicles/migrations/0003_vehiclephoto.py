# Generated manually for Premier Wheels India.
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("vehicles", "0002_vehicle_location_vehicle_seller_phone_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="VehiclePhoto",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        upload_to="vehicles/gallery/",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                    ),
                ),
                (
                    "vehicle",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="photos",
                        to="vehicles.vehicle",
                    ),
                ),
            ],
            options={
                "ordering": ["created_at"],
            },
        ),
    ]
