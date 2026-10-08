import re

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Enquiry, Vehicle


class IndianNumberField(forms.IntegerField):
    """Accept numbers written with Indian-style commas or symbols."""

    def to_python(self, value):
        if value in (None, ""):
            return None

        value = re.sub(r"[^\d]", "", str(value))

        if not value:
            return None

        return super().to_python(value)


class IndianPriceField(IndianNumberField):
    """Integer price field that accepts ₹ and commas."""

    pass


class RegisterForm(UserCreationForm):

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "input",
                "placeholder": "you@example.com",
            }
        ),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]

        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "Choose a username",
                }
            ),
        }


class VehicleForm(forms.ModelForm):

    price = IndianPriceField(
        min_value=50000,
        widget=forms.TextInput(
            attrs={
                "class": "input price-input",
                "placeholder": "₹50,000",
                "inputmode": "numeric",
                "autocomplete": "off",
            }
        ),
    )

    mileage = IndianNumberField(
        min_value=0,
        widget=forms.TextInput(
            attrs={
                "class": "input mileage-input",
                "placeholder": "e.g. 35,000",
                "inputmode": "numeric",
                "autocomplete": "off",
            }
        ),
    )

    class Meta:
        model = Vehicle

        fields = [
            "make",
            "model",
            "year",
            "price",
            "mileage",
            "engine_specs",
            "fuel_type",
            "transmission",
            "location",
            "seller_phone",
            "seller_email",
            "short_description",
            "image",
        ]

        widgets = {
            "make": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "e.g. Toyota",
                }
            ),
            "model": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "e.g. Fortuner",
                }
            ),
            "year": forms.NumberInput(
                attrs={
                    "class": "input",
                    "placeholder": "e.g. 2022",
                    "min": 1950,
                    "max": 2100,
                }
            ),
            "engine_specs": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "e.g. 2.8L Turbo Diesel",
                }
            ),
            "fuel_type": forms.Select(
                attrs={
                    "class": "input",
                }
            ),
            "transmission": forms.Select(
                attrs={
                    "class": "input",
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "e.g. Nashik, Maharashtra",
                }
            ),
            "seller_phone": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "e.g. 9876543210",
                    "inputmode": "tel",
                }
            ),
            "seller_email": forms.EmailInput(
                attrs={
                    "class": "input",
                    "placeholder": "e.g. seller@example.com",
                    "autocomplete": "email",
                }
            ),
            "short_description": forms.Textarea(
                attrs={
                    "class": "input",
                    "placeholder": "Describe the vehicle, condition, ownership, service history, etc.",
                    "rows": 5,
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "input image-input",
                    "accept": "image/*",
                }
            ),
        }

    def clean_seller_phone(self):
        phone = self.cleaned_data.get("seller_phone", "")
        phone = re.sub(r"\D", "", phone)

        if phone and len(phone) != 10:
            raise forms.ValidationError(
                "Please enter a valid 10-digit phone number."
            )

        return phone

    def clean_year(self):
        from datetime import date

        year = self.cleaned_data.get("year")
        current_year = date.today().year

        if year is None:
            raise forms.ValidationError("Please enter the vehicle year.")

        if year < 1950 or year > current_year:
            raise forms.ValidationError(
                f"Enter a vehicle year between 1950 and {current_year}."
            )

        return year


class EnquiryForm(forms.ModelForm):

    class Meta:
        model = Enquiry
        fields = [
            "buyer_name",
            "buyer_phone",
            "message",
        ]
        widgets = {
            "buyer_name": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "Your name",
                    "autocomplete": "name",
                }
            ),
            "buyer_phone": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "e.g. 9876543210",
                    "inputmode": "tel",
                    "autocomplete": "tel",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "input",
                    "rows": 5,
                    "placeholder": "Hi, I am interested in this car. Is it still available?",
                }
            ),
        }

    def clean_buyer_phone(self):
        phone = re.sub(r"\D", "", self.cleaned_data.get("buyer_phone", ""))
        if len(phone) != 10:
            raise forms.ValidationError(
                "Please enter a valid 10-digit phone number."
            )
        return phone


class PremierMatchForm(forms.Form):

    budget_min = IndianPriceField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "input price-input",
                "placeholder": "₹10,00,000",
                "inputmode": "numeric",
                "autocomplete": "off",
            }
        ),
    )

    budget_max = IndianPriceField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "input price-input",
                "placeholder": "₹25,00,000",
                "inputmode": "numeric",
                "autocomplete": "off",
            }
        ),
    )

    fuel_type = forms.ChoiceField(
        required=False,
        choices=[("", "Any Fuel")] + Vehicle.FUEL_CHOICES,
        widget=forms.Select(attrs={"class": "input"}),
    )

    transmission = forms.ChoiceField(
        required=False,
        choices=[("", "Any Transmission")] + Vehicle.TRANSMISSION_CHOICES,
        widget=forms.Select(attrs={"class": "input"}),
    )

    min_year = forms.IntegerField(
        required=False,
        min_value=1950,
        max_value=2100,
        widget=forms.NumberInput(
            attrs={
                "class": "input",
                "placeholder": "e.g. 2020",
            }
        ),
    )

    max_mileage = IndianNumberField(
        required=False,
        min_value=0,
        widget=forms.TextInput(
            attrs={
                "class": "input mileage-input",
                "placeholder": "e.g. 60,000",
                "inputmode": "numeric",
                "autocomplete": "off",
            }
        ),
    )

    location = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "placeholder": "e.g. Nashik",
            }
        ),
    )

    priority = forms.ChoiceField(
        required=False,
        initial="quality",
        choices=[
            ("quality", "Overall listing quality"),
            ("price", "Lower price"),
            ("mileage", "Lower mileage"),
            ("newest", "Newer vehicle"),
        ],
        widget=forms.Select(attrs={"class": "input"}),
    )

    def clean(self):
        cleaned = super().clean()

        minimum = cleaned.get("budget_min")
        maximum = cleaned.get("budget_max")

        if minimum is not None and maximum is not None:
            if minimum > maximum:
                raise forms.ValidationError(
                    "Minimum budget cannot be greater than maximum budget."
                )

        return cleaned
