# Premier Wheels India 🚗

A full-stack Django web application for buying and selling pre-owned vehicles.

Premier Wheels is designed as an OLX-style used-car marketplace with a stronger
buyer decision layer: transparent vehicle scoring, personalized matching and
an ownership-cost estimator.

## Core Features

### Marketplace
- User registration, login and logout
- Create, edit and delete vehicle listings
- Vehicle images and multi-photo galleries
- Search by make, model, location and engine details
- Advanced filters: make, fuel, transmission, year, price and location
- Sorting by price, mileage and year
- Individual vehicle detail pages
- Seller phone and seller email
- In-app buyer enquiries

### Buyer Tools
- Saved Cars / Favorites
- PremierScore
- PremierMatch
- Ownership Estimate
- Similar vehicles

### Seller Tools
- Seller dashboard
- Listing management
- Buyer enquiry inbox
- Image/gallery management
- Seller-specific phone/email information

## Signature Features

### ⭐ PremierScore

PremierScore is a transparent, rule-based comparative indicator. It is NOT a
claim that one vehicle is universally better than another.

It considers:
- Price competitiveness: 30 points
- Mileage relative to vehicle age: 20 points
- Vehicle age: 15 points
- Photos & presentation: 15 points
- Listing completeness: 15 points
- Seller information: 5 points

The price component prefers same make/model comparisons and falls back to
similar listings when enough direct comparisons are unavailable.

### 🎯 PremierMatch

PremierMatch asks the buyer for:
- Budget
- Fuel type
- Transmission
- Minimum year
- Maximum mileage
- Location
- Main priority

It produces a transparent percentage match. A match percentage is a
personalized preference score, not an objective ranking of the best car.

### 💰 Ownership Estimate

The vehicle page includes a client-side calculator for:
- Annual kilometres
- Fuel/energy price
- Estimated efficiency
- Insurance per year
- Maintenance per year

It returns estimated annual and five-year ownership running cost.

All results are estimates and depend on user-entered assumptions.

## Tech Stack

- Python 3.11
- Django 5.2
- SQLite
- HTML5
- CSS3
- JavaScript
- Pillow

## Application Structure

```text
PremierWheelsDjango_updated/
├── Cars/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── vehicles/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── scoring.py
│   ├── urls.py
│   ├── admin.py
│   ├── tests.py
│   ├── migrations/
│   ├── templates/vehicles/
│   └── static/vehicles/
│
├── media/
├── manage.py
├── requirements.txt
└── README.md
```

## Database Models

The application uses Django ORM models for:
- `Vehicle`
- `VehiclePhoto`
- `Enquiry`
- `Favorite`

Vehicles are linked to Django's built-in `User` model so ownership,
permissions and seller enquiries are tied to authenticated accounts.

## Local Setup

```bash
python -m venv prathamesh
```

Windows PowerShell:

```powershell
.\prathamesh\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Apply migrations:

```powershell
python manage.py migrate
```

Run Django's system checks:

```powershell
python manage.py check
```

Run tests:

```powershell
python manage.py test
```

Start the development server:

```powershell
python manage.py runserver 8080
```

Then open:

```text
http://127.0.0.1:8080/
```

## Environment Variables

For a production deployment, set:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`

The local development settings provide safe development defaults so the project
can still run without additional configuration.

## Resume Description

**Premier Wheels India — Django Used-Car Marketplace**

Developed a full-stack used-car marketplace using Django, SQLite, HTML, CSS and
JavaScript with authentication, vehicle CRUD, multi-image galleries, advanced
search/filtering, seller contact, buyer enquiries and saved cars. Implemented
a transparent rule-based PremierScore, personalized PremierMatch recommendation
system and interactive ownership-cost estimator to help users evaluate used
vehicles.

## Interview Talking Points

1. Why Django ORM was used for vehicle/seller/enquiry relationships.
2. How seller ownership is enforced for edit/delete operations.
3. How gallery photos are linked to vehicles with a separate model.
4. How PremierScore avoids comparing unrelated vehicles directly.
5. How PremierMatch differs from PremierScore.
6. Why ownership estimates are explicitly presented as assumptions rather than
   exact financial predictions.
7. How authentication, CSRF protection and form validation protect marketplace
   actions.

## Security / Production Note

This project is configured for local development. Before deployment:
- Use a production secret key through `DJANGO_SECRET_KEY`
- Set `DJANGO_DEBUG=False`
- Configure production `ALLOWED_HOSTS`
- Use a production database
- Configure a proper static/media storage backend
- Serve the application through a production WSGI/ASGI setup
