from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import EnquiryForm, PremierMatchForm, RegisterForm, VehicleForm
from .models import Enquiry, Favorite, Vehicle, VehiclePhoto
from .scoring import calculate_premier_match, calculate_premier_score


def home(request):
    from datetime import date

    available_pool = list(
        Vehicle.objects.filter(is_available=True)
        .select_related("seller")
        .prefetch_related("photos")
    )

    vehicles = Vehicle.objects.filter(
        is_available=True
    ).select_related("seller").prefetch_related("photos")

    search_query = request.GET.get("q", "").strip()
    if search_query:
        from django.db.models import Q
        vehicles = vehicles.filter(
            Q(make__icontains=search_query)
            | Q(model__icontains=search_query)
            | Q(location__icontains=search_query)
            | Q(engine_specs__icontains=search_query)
        )

    make = request.GET.get("make", "").strip()
    fuel = request.GET.get("fuel", "").strip()
    transmission = request.GET.get("transmission", "").strip()
    year = request.GET.get("year", "").strip()
    location = request.GET.get("location", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    sort = request.GET.get("sort", "newest").strip()

    if make:
        vehicles = vehicles.filter(make__iexact=make)
    if fuel:
        vehicles = vehicles.filter(fuel_type=fuel)
    if transmission:
        vehicles = vehicles.filter(transmission=transmission)
    if year.isdigit():
        vehicles = vehicles.filter(year=int(year))
    if location:
        vehicles = vehicles.filter(location__icontains=location)

    min_price_digits = "".join(ch for ch in min_price if ch.isdigit())
    max_price_digits = "".join(ch for ch in max_price if ch.isdigit())

    if min_price_digits:
        vehicles = vehicles.filter(price__gte=int(min_price_digits))
    if max_price_digits:
        vehicles = vehicles.filter(price__lte=int(max_price_digits))

    min_price = min_price_digits
    max_price = max_price_digits

    sort_options = {
        "newest": "-created_at",
        "price_low": "price",
        "price_high": "-price",
        "mileage_low": "mileage",
        "mileage_high": "-mileage",
        "year_new": "-year",
        "year_old": "year",
    }

    vehicles = list(
        vehicles.order_by(sort_options.get(sort, "-created_at"))
    )

    current_year = date.today().year
    for vehicle in vehicles:
        vehicle.premier_score_data = calculate_premier_score(
            vehicle, available_pool, current_year
        )

    form = VehicleForm(
        initial={"seller_email": request.user.email}
        if request.user.is_authenticated
        else None
    )

    makes = (
        Vehicle.objects.filter(is_available=True)
        .exclude(make="")
        .values_list("make", flat=True)
        .distinct()
        .order_by("make")
    )

    years = (
        Vehicle.objects.filter(is_available=True)
        .values_list("year", flat=True)
        .distinct()
        .order_by("-year")
    )

    if request.user.is_authenticated:
        favorite_vehicle_ids = set(
            Favorite.objects.filter(
                user=request.user,
                vehicle_id__in=[vehicle.pk for vehicle in vehicles],
            ).values_list("vehicle_id", flat=True)
        )
    else:
        favorite_vehicle_ids = set()

    return render(
        request,
        "vehicles/home.html",
        {
            "vehicles": vehicles,
            "form": form,
            "makes": makes,
            "years": years,
            "fuel_choices": Vehicle.FUEL_CHOICES,
            "transmission_choices": Vehicle.TRANSMISSION_CHOICES,
            "search_query": search_query,
            "selected_make": make,
            "selected_fuel": fuel,
            "selected_transmission": transmission,
            "selected_year": year,
            "selected_location": location,
            "min_price": min_price,
            "max_price": max_price,
            "selected_sort": sort,
            "favorite_vehicle_ids": favorite_vehicle_ids,
        },
    )


def vehicle_detail(request, pk):
    from datetime import date

    vehicle = get_object_or_404(
        Vehicle.objects.select_related("seller").prefetch_related("photos"),
        pk=pk,
        is_available=True,
    )

    similar_vehicles = (
        Vehicle.objects.filter(
            is_available=True,
            make__iexact=vehicle.make,
        )
        .exclude(pk=vehicle.pk)
        .select_related("seller")
        .prefetch_related("photos")[:3]
    )

    comparison_pool = list(
        Vehicle.objects.filter(is_available=True)
        .exclude(pk=vehicle.pk)
        .select_related("seller")
        .prefetch_related("photos")
    )

    premier_score_data = calculate_premier_score(
        vehicle,
        comparison_pool,
        date.today().year,
    )

    return render(
        request,
        "vehicles/detail.html",
        {
            "vehicle": vehicle,
            "similar_vehicles": similar_vehicles,
            "vehicle_photos": vehicle.photos.all(),
            "premier_score_data": premier_score_data,
            "is_favorited": (
                request.user.is_authenticated
                and Favorite.objects.filter(
                    user=request.user,
                    vehicle=vehicle,
                ).exists()
            ),
        },
    )



def premier_match(request):
    from datetime import date

    available_pool = list(
        Vehicle.objects.filter(is_available=True)
        .select_related("seller")
        .prefetch_related("photos")
    )

    form = PremierMatchForm(request.GET or None)
    results = []

    if request.GET and form.is_valid():
        preferences = form.cleaned_data

        for vehicle in available_pool:
            vehicle.premier_match_data = calculate_premier_match(
                vehicle,
                preferences,
                available_pool,
                date.today().year,
            )
            results.append(vehicle)

        results.sort(
            key=lambda vehicle: (
                vehicle.premier_match_data["score"],
                vehicle.premier_match_data["premier_score"]["score"],
            ),
            reverse=True,
        )
        results = results[:12]

    return render(
        request,
        "vehicles/premier_match.html",
        {
            "form": form,
            "results": results,
            "has_results": bool(results),
        },
    )


def contact_seller(request, pk):
    vehicle = get_object_or_404(
        Vehicle.objects.select_related("seller"),
        pk=pk,
        is_available=True,
    )

    if request.user.is_authenticated and request.user == vehicle.seller:
        messages.info(
            request,
            "You cannot send a buyer enquiry for your own vehicle.",
        )
        return redirect("vehicles:vehicle_detail", pk=vehicle.pk)

    if request.method == "POST":
        form = EnquiryForm(request.POST)

        if form.is_valid():
            enquiry = form.save(commit=False)
            enquiry.vehicle = vehicle

            if request.user.is_authenticated:
                enquiry.buyer = request.user

            enquiry.save()

            messages.success(
                request,
                "Your enquiry was sent to the seller successfully.",
            )

            return redirect("vehicles:vehicle_detail", pk=vehicle.pk)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial["buyer_name"] = request.user.get_full_name() or request.user.username
            if request.user.email:
                pass
        form = EnquiryForm(initial=initial)

    return render(
        request,
        "vehicles/contact_seller.html",
        {
            "vehicle": vehicle,
            "form": form,
        },
    )


@login_required
@require_POST
def toggle_favorite(request, pk):
    vehicle = get_object_or_404(
        Vehicle,
        pk=pk,
        is_available=True,
    )

    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        vehicle=vehicle,
    )

    if not created:
        favorite.delete()
        messages.success(
            request,
            f"{vehicle.make} {vehicle.model} was removed from your saved cars.",
        )
    else:
        messages.success(
            request,
            f"{vehicle.make} {vehicle.model} was added to your saved cars.",
        )

    next_url = request.POST.get("next", "")
    if next_url.startswith("/") and not next_url.startswith("//"):
        return redirect(next_url)

    return redirect("vehicles:vehicle_detail", pk=vehicle.pk)


@login_required
def favorites(request):
    favorite_items = (
        Favorite.objects.filter(
            user=request.user,
            vehicle__is_available=True,
        )
        .select_related("vehicle", "vehicle__seller")
    )

    return render(
        request,
        "vehicles/favorites.html",
        {
            "favorite_items": favorite_items,
        },
    )


def register_view(request):
    if request.user.is_authenticated:
        return redirect("vehicles:home")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(
                request,
                "Your account has been created successfully.",
            )

            return redirect("vehicles:home")
    else:
        form = RegisterForm()

    return render(
        request,
        "vehicles/register.html",
        {"form": form},
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("vehicles:home")

    if request.method == "POST":
        form = AuthenticationForm(
            request,
            data=request.POST,
        )

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(
                username=username,
                password=password,
            )

            if user is not None:
                login(request, user)

                messages.success(
                    request,
                    f"Welcome back, {user.username}!",
                )

                next_url = request.GET.get("next")
                if next_url:
                    return redirect(next_url)

                return redirect("vehicles:home")
    else:
        form = AuthenticationForm()

    return render(
        request,
        "vehicles/login.html",
        {"form": form},
    )


def logout_view(request):
    logout(request)

    messages.success(
        request,
        "You have been logged out.",
    )

    return redirect("vehicles:home")


@login_required
def add_vehicle(request):
    if request.method == "POST":
        form = VehicleForm(
            request.POST,
            request.FILES,
        )

        gallery_photos = request.FILES.getlist("photos")

        if len(gallery_photos) > 8:
            form.add_error(
                None,
                "You can upload a maximum of 8 additional photos.",
            )

        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.seller = request.user
            vehicle.save()

            for photo in gallery_photos[:8]:
                VehiclePhoto.objects.create(
                    vehicle=vehicle,
                    image=photo,
                )

            messages.success(
                request,
                "Your vehicle has been listed successfully.",
            )

            return redirect("vehicles:home")
    else:
        form = VehicleForm(
            initial={"seller_email": request.user.email}
        )

    vehicles = (
        Vehicle.objects.filter(is_available=True)
        .select_related("seller")
    )

    return render(
        request,
        "vehicles/home.html",
        {
            "vehicles": vehicles,
            "form": form,
        },
    )


@login_required
def dashboard(request):
    vehicles = (
        Vehicle.objects.filter(seller=request.user)
        .select_related("seller")
    )

    enquiries = (
        Enquiry.objects.filter(vehicle__seller=request.user)
        .select_related("vehicle", "buyer")
    )

    from datetime import date

    comparison_pool = list(
        Vehicle.objects.filter(is_available=True)
        .select_related("seller")
        .prefetch_related("photos")
    )

    for vehicle in vehicles:
        vehicle.premier_score_data = calculate_premier_score(
            vehicle,
            comparison_pool,
            date.today().year,
        )

    return render(
        request,
        "vehicles/dashboard.html",
        {
            "vehicles": vehicles,
            "enquiries": enquiries,
            "favorite_count": Favorite.objects.filter(
                user=request.user,
                vehicle__is_available=True,
            ).count(),
        },
    )


@login_required
def edit_vehicle(request, pk):
    vehicle = get_object_or_404(
        Vehicle,
        pk=pk,
        seller=request.user,
    )

    existing_photos = vehicle.photos.all()

    if request.method == "POST":
        form = VehicleForm(
            request.POST,
            request.FILES,
            instance=vehicle,
        )

        gallery_photos = request.FILES.getlist("photos")

        delete_ids = request.POST.getlist("delete_photo_ids")

        current_photo_count = existing_photos.exclude(
            pk__in=delete_ids
        ).count()

        if current_photo_count + len(gallery_photos) > 8:
            form.add_error(
                None,
                "A vehicle can have a maximum of 8 gallery photos. "
                "Remove some existing photos or upload fewer new photos.",
            )

        if form.is_valid():
            form.save()

            if delete_ids:
                vehicle.photos.filter(
                    pk__in=delete_ids
                ).delete()

            remaining_slots = max(
                0,
                8 - vehicle.photos.count(),
            )

            for photo in gallery_photos[:remaining_slots]:
                VehiclePhoto.objects.create(
                    vehicle=vehicle,
                    image=photo,
                )

            messages.success(
                request,
                "Your vehicle listing was updated successfully.",
            )

            return redirect("vehicles:dashboard")
    else:
        form = VehicleForm(instance=vehicle)

    return render(
        request,
        "vehicles/edit_vehicle.html",
        {
            "form": form,
            "vehicle": vehicle,
            "vehicle_photos": vehicle.photos.all(),
        },
    )


@login_required
@require_POST
def delete_vehicle(request, pk):
    vehicle = get_object_or_404(
        Vehicle,
        pk=pk,
        seller=request.user,
    )

    vehicle.delete()

    messages.success(
        request,
        "The vehicle was deleted successfully.",
    )

    return redirect("vehicles:dashboard")
