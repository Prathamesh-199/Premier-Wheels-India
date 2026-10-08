from statistics import median


PREMIER_NOTICE = (
    "PremierScore is a comparative indicator based on available vehicle "
    "and listing information. A higher score does not mean the vehicle is "
    "universally better than another vehicle. It indicates stronger "
    "relative value and listing quality among relevant comparable vehicles."
)


def _age(vehicle, current_year):
    return max(0, current_year - vehicle.year)


def _photo_count(vehicle):
    try:
        gallery_count = len(vehicle.photos.all())
    except Exception:
        gallery_count = 0
    return (1 if vehicle.image else 0) + gallery_count


def _price_score(vehicle, comparison_pool):
    same_model = [
        other for other in comparison_pool
        if other.pk != vehicle.pk
        and other.make.strip().lower() == vehicle.make.strip().lower()
        and other.model.strip().lower() == vehicle.model.strip().lower()
        and other.price > 0
    ]

    if len(same_model) >= 2:
        comparables = same_model
        basis = f"same {vehicle.make} {vehicle.model} listings"
    else:
        lower = vehicle.price * 0.65
        upper = vehicle.price * 1.35
        similar_market = [
            other for other in comparison_pool
            if other.pk != vehicle.pk
            and other.fuel_type == vehicle.fuel_type
            and other.transmission == vehicle.transmission
            and lower <= other.price <= upper
            and other.price > 0
        ]
        if len(similar_market) >= 2:
            comparables = similar_market
            basis = "similar fuel, transmission and price-range listings"
        else:
            return (
                18,
                "limited comparable listings",
                0,
                "Price comparison is limited because there are not enough "
                "closely comparable listings on Premier Wheels.",
            )

    median_price = median([car.price for car in comparables])
    ratio = vehicle.price / median_price if median_price else 1

    if ratio <= 0.85:
        score = 30
        note = (
            "Priced significantly below the comparable-listing median; "
            "buyers should verify condition and vehicle history."
        )
    elif ratio <= 0.95:
        score = 29
        note = "Priced below the comparable-listing median."
    elif ratio <= 1.05:
        score = 27
        note = "Priced close to the comparable-listing median."
    elif ratio <= 1.15:
        score = 24
        note = "Priced moderately above the comparable-listing median."
    elif ratio <= 1.30:
        score = 19
        note = "Priced noticeably above the comparable-listing median."
    else:
        score = 12
        note = "Priced substantially above the comparable-listing median."

    return score, basis, len(comparables), note


def calculate_premier_score(vehicle, comparison_pool, current_year):
    price_points, basis, comparable_count, price_note = _price_score(
        vehicle, comparison_pool
    )
    age = _age(vehicle, current_year)

    if age <= 2:
        age_points = 15
    elif age <= 4:
        age_points = 13
    elif age <= 6:
        age_points = 10
    elif age <= 8:
        age_points = 8
    elif age <= 12:
        age_points = 5
    else:
        age_points = 3

    annual_mileage = vehicle.mileage / max(age, 1)
    if annual_mileage <= 8000:
        mileage_points = 20
    elif annual_mileage <= 12000:
        mileage_points = 18
    elif annual_mileage <= 16000:
        mileage_points = 15
    elif annual_mileage <= 20000:
        mileage_points = 11
    elif annual_mileage <= 25000:
        mileage_points = 7
    else:
        mileage_points = 4

    photo_count = _photo_count(vehicle)
    if photo_count <= 1:
        photo_points = 3
    elif photo_count <= 3:
        photo_points = 6
    elif photo_count <= 5:
        photo_points = 10
    elif photo_count <= 8:
        photo_points = 13
    else:
        photo_points = 15

    description_length = len((vehicle.short_description or "").strip())
    completeness_points = 0
    if vehicle.location:
        completeness_points += 2
    if description_length >= 120:
        completeness_points += 4
    elif description_length >= 60:
        completeness_points += 3
    elif description_length >= 25:
        completeness_points += 2
    if vehicle.engine_specs:
        completeness_points += 3
    if vehicle.fuel_type:
        completeness_points += 1
    if vehicle.transmission:
        completeness_points += 2
    if vehicle.year:
        completeness_points += 1
    if vehicle.mileage is not None:
        completeness_points += 1

    seller_points = 0
    if vehicle.seller_phone:
        seller_points += 2
    if vehicle.seller_email:
        seller_points += 2
    if vehicle.location:
        seller_points += 1

    total = min(
        100,
        price_points + mileage_points + age_points +
        photo_points + completeness_points + seller_points,
    )

    if comparable_count == 0:
        if total >= 85:
            label = "Strong Listing"
        elif total >= 70:
            label = "Good Listing"
        elif total >= 60:
            label = "Fair Listing"
        else:
            label = "Needs Review"
    elif total >= 90:
        label = "Outstanding Value"
    elif total >= 80:
        label = "Excellent Value"
    elif total >= 70:
        label = "Strong Value"
    elif total >= 60:
        label = "Fair Value"
    else:
        label = "Needs Review"

    breakdown = [
        {"label": "Price competitiveness", "points": price_points, "max_points": 30},
        {"label": "Mileage for vehicle age", "points": mileage_points, "max_points": 20},
        {"label": "Vehicle age", "points": age_points, "max_points": 15},
        {"label": "Photos & presentation", "points": photo_points, "max_points": 15},
        {"label": "Listing completeness", "points": completeness_points, "max_points": 15},
        {"label": "Seller information", "points": seller_points, "max_points": 5},
    ]

    return {
        "score": total,
        "label": label,
        "breakdown": breakdown,
        "comparison_basis": basis,
        "comparable_count": comparable_count,
        "price_note": price_note,
        "photo_count": photo_count,
        "annual_mileage": round(annual_mileage),
        "notice": PREMIER_NOTICE,
    }


def _priority_points(vehicle, preference, premier_score, pool):
    if preference == "price":
        median_price = median([v.price for v in pool]) if pool else vehicle.price
        return 5 if vehicle.price <= median_price else 3
    if preference == "mileage":
        median_mileage = median([v.mileage for v in pool]) if pool else vehicle.mileage
        return 5 if vehicle.mileage <= median_mileage else 3
    if preference == "newest":
        median_year = median([v.year for v in pool]) if pool else vehicle.year
        return 5 if vehicle.year >= median_year else 3
    return 5 if premier_score["score"] >= 80 else 3


def calculate_premier_match(vehicle, preferences, comparison_pool, current_year):
    premier_score = calculate_premier_score(vehicle, comparison_pool, current_year)

    min_budget = preferences.get("budget_min")
    max_budget = preferences.get("budget_max")
    price = vehicle.price

    if min_budget is None and max_budget is None:
        budget_points = 30
    elif min_budget is not None and max_budget is not None:
        if min_budget <= price <= max_budget:
            budget_points = 30
        elif price < min_budget:
            budget_points = 24 if price >= min_budget * 0.90 else 14
        else:
            budget_points = (
                24 if price <= max_budget * 1.10
                else 17 if price <= max_budget * 1.20
                else 8
            )
    elif max_budget is not None:
        budget_points = 30 if price <= max_budget else (24 if price <= max_budget * 1.10 else 10)
    else:
        budget_points = 30 if price >= min_budget else (24 if price >= min_budget * 0.90 else 12)

    requested_fuel = preferences.get("fuel_type")
    fuel_points = 20 if not requested_fuel else (20 if vehicle.fuel_type == requested_fuel else 0)

    requested_transmission = preferences.get("transmission")
    transmission_points = (
        15 if not requested_transmission
        else 15 if vehicle.transmission == requested_transmission
        else 0
    )

    min_year = preferences.get("min_year")
    if not min_year:
        year_points = 10
    elif vehicle.year >= min_year:
        year_points = 10
    elif vehicle.year >= min_year - 2:
        year_points = 6
    else:
        year_points = 2

    max_mileage = preferences.get("max_mileage")
    if not max_mileage:
        mileage_points = 10
    elif vehicle.mileage <= max_mileage:
        mileage_points = 10
    elif vehicle.mileage <= max_mileage * 1.20:
        mileage_points = 7
    else:
        mileage_points = 3

    requested_location = (preferences.get("location") or "").strip().lower()
    vehicle_location = (vehicle.location or "").strip().lower()
    if not requested_location:
        location_points = 10
    elif requested_location in vehicle_location:
        location_points = 10
    else:
        location_points = 4

    priority_points = _priority_points(
        vehicle,
        preferences.get("priority", "quality"),
        premier_score,
        comparison_pool,
    )

    total = min(
        100,
        budget_points + fuel_points + transmission_points +
        year_points + mileage_points + location_points + priority_points,
    )

    if total >= 90:
        label = "Excellent Match"
    elif total >= 80:
        label = "Very Strong Match"
    elif total >= 70:
        label = "Strong Match"
    elif total >= 55:
        label = "Possible Match"
    else:
        label = "Low Match"

    return {
        "score": total,
        "label": label,
        "premier_score": premier_score,
        "breakdown": [
            {"label": "Budget", "points": budget_points, "max_points": 30},
            {"label": "Fuel type", "points": fuel_points, "max_points": 20},
            {"label": "Transmission", "points": transmission_points, "max_points": 15},
            {"label": "Minimum year", "points": year_points, "max_points": 10},
            {"label": "Mileage", "points": mileage_points, "max_points": 10},
            {"label": "Location", "points": location_points, "max_points": 10},
            {"label": "Your priority", "points": priority_points, "max_points": 5},
        ],
    }
