from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from .forms import EnquiryForm, PremierMatchForm, VehicleForm
from .models import Vehicle
from .scoring import calculate_premier_match, calculate_premier_score


class VehicleFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="seller",
            password="StrongPass123!",
            email="seller@example.com",
        )

    def base_vehicle_data(self):
        return {
            "make": "Kia",
            "model": "Seltos",
            "year": date.today().year - 2,
            "price": "17,30,000",
            "mileage": "48,560",
            "engine_specs": "1.5L Turbo Petrol",
            "fuel_type": "Petrol",
            "transmission": "DCT",
            "location": "Nashik, Maharashtra",
            "seller_phone": "9876543210",
            "seller_email": "seller@example.com",
            "short_description": (
                "Well maintained vehicle with detailed service history."
            ),
        }

    def test_valid_vehicle_form_accepts_indian_number_format(self):
        form = VehicleForm(data=self.base_vehicle_data())
        self.assertTrue(form.is_valid(), form.errors.as_text())
        self.assertEqual(form.cleaned_data["price"], 1730000)
        self.assertEqual(form.cleaned_data["mileage"], 48560)

    def test_invalid_phone_length_is_rejected(self):
        data = self.base_vehicle_data()
        data["seller_phone"] = "12345"
        form = VehicleForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("seller_phone", form.errors)

    def test_future_year_is_rejected(self):
        data = self.base_vehicle_data()
        data["year"] = date.today().year + 1
        form = VehicleForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("year", form.errors)


class EnquiryFormTests(TestCase):

    def test_enquiry_requires_ten_digit_phone(self):
        form = EnquiryForm(
            data={
                "buyer_name": "Buyer",
                "buyer_phone": "987654321",
                "message": "Is the car still available?",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("buyer_phone", form.errors)


class PremierMatchFormTests(TestCase):

    def test_minimum_budget_cannot_exceed_maximum(self):
        form = PremierMatchForm(
            data={
                "budget_min": "20,00,000",
                "budget_max": "10,00,000",
                "fuel_type": "",
                "transmission": "",
                "min_year": "",
                "max_mileage": "",
                "location": "",
                "priority": "quality",
            }
        )
        self.assertFalse(form.is_valid())


class PremierScoringTests(TestCase):

    def setUp(self):
        self.seller = User.objects.create_user(
            username="seller",
            password="StrongPass123!",
            email="seller@example.com",
        )

    def create_vehicle(self, **overrides):
        data = {
            "seller": self.seller,
            "make": "Kia",
            "model": "Seltos",
            "year": date.today().year - 2,
            "price": 1730000,
            "mileage": 48560,
            "engine_specs": "1.5L Turbo Petrol",
            "fuel_type": "Petrol",
            "transmission": "DCT",
            "location": "Nashik",
            "seller_phone": "9876543210",
            "seller_email": "seller@example.com",
            "short_description": "A complete listing with useful details.",
        }
        data.update(overrides)
        return Vehicle.objects.create(**data)

    def test_premier_score_stays_between_zero_and_hundred(self):
        vehicle = self.create_vehicle()
        data = calculate_premier_score(
            vehicle,
            [vehicle],
            date.today().year,
        )
        self.assertGreaterEqual(data["score"], 0)
        self.assertLessEqual(data["score"], 100)
        self.assertIn("notice", data)

    def test_premier_match_stays_between_zero_and_hundred(self):
        vehicle = self.create_vehicle()
        preferences = {
            "budget_min": 1000000,
            "budget_max": 2000000,
            "fuel_type": "Petrol",
            "transmission": "DCT",
            "min_year": date.today().year - 5,
            "max_mileage": 60000,
            "location": "Nashik",
            "priority": "quality",
        }

        data = calculate_premier_match(
            vehicle,
            preferences,
            [vehicle],
            date.today().year,
        )

        self.assertGreaterEqual(data["score"], 0)
        self.assertLessEqual(data["score"], 100)
