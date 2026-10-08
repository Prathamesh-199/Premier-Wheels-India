from django.db import migrations, models


def copy_seller_emails(apps, schema_editor):
    Vehicle = apps.get_model("vehicles", "Vehicle")

    for vehicle in Vehicle.objects.select_related("seller").all():
        email = getattr(vehicle.seller, "email", "") or ""
        if email:
            vehicle.seller_email = email
            vehicle.save(update_fields=["seller_email"])


class Migration(migrations.Migration):

    dependencies = [
        ("vehicles", "0005_favorite"),
    ]

    operations = [
        migrations.AddField(
            model_name="vehicle",
            name="seller_email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.RunPython(copy_seller_emails, migrations.RunPython.noop),
    ]
