# TravelBook — Travel Booking System

A Django-based travel booking web application that lets users discover available flights, trains, and buses, search routes, reserve seats, and manage their bookings. The application uses Django's built-in authentication system, server-rendered templates, and an SQLite database by default.

> **Project type:** Django web application (HTML templates and form-based views). Django REST Framework is present in the dependency list, but the current codebase does not expose a REST API.

## Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Data Models](#data-models)
- [Getting Started](#getting-started)
- [Creating an Admin User](#creating-an-admin-user)
- [Using the Application](#using-the-application)
- [URL Reference](#url-reference)
- [Running Tests](#running-tests)
- [Configuration and Security Notes](#configuration-and-security-notes)
- [Possible Enhancements](#possible-enhancements)
- [Contributing](#contributing)
- [License](#license)

## Overview

TravelBook provides a simple end-to-end booking flow. Visitors can browse upcoming travel options and filter them by transport type, source, destination, and date. Registered users can book seats, view their own booking details, cancel confirmed bookings, and maintain profile information. Staff can manage application data through Django Admin.

The project is useful as a learning example for Django models, model forms, authentication, access-controlled views, template rendering, pagination, and relationships between users, travel options, and bookings.

## Features

### Travel discovery

- Supports **flights, trains, and buses**.
- Displays upcoming travel options that have seats available.
- Search/filter by transport type, source, destination, and travel date.
- Source and destination searches are case-insensitive partial matches.
- Paginates travel results, showing up to 10 options per page.
- Displays a selection of recent available trips on the home page.

### User accounts and profiles

- User registration with username, first name, last name, email, and password.
- Login and logout using Django authentication views.
- Profile management for name, email, phone number, address, and date of birth.
- Booking and profile pages require authentication where appropriate.

### Booking management

- Users select a travel option and number of seats.
- Validates that the requested seat count is at least one and does not exceed the available inventory at form-validation time.
- Calculates the booking total from the travel option's price and requested seat count.
- Generates a booking reference automatically when one is not provided (`BK` followed by an uppercase identifier).
- Reduces available seats after a successful booking.
- Shows a user's bookings and individual booking details.
- Allows users to cancel their own confirmed bookings and restores the reserved seats.
- Prevents users from viewing another user's booking through the booking-detail view's ownership filter.

### Administration

- Uses Django Admin for managing travel options, bookings, and profiles.
- Includes Django's standard password validation and CSRF middleware in the default configuration.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application language |
| Django 5.1.1 | Web framework, ORM, routing, forms, authentication, templates, and admin |
| SQLite | Default local database |
| Django Templates | Server-rendered user interface |
| django-crispy-forms / crispy-bootstrap4 | Form rendering integration |
| Pillow | Image-related Python dependency |
| PostgreSQL driver (`psycopg2-binary`) | Optional database support in the dependency set |
| Gunicorn / WhiteNoise | Deployment-related dependencies included in requirements |

The exact dependency versions are listed in [`requirements.txt`](requirements.txt).

## How It Works

1. **Travel options** are stored in the `TravelOption` table with a unique travel code, mode, route, departure date/time, price, and available-seat count.
2. Visitors browse or search for future options with seats remaining.
3. A user registers or logs in before creating a booking.
4. The booking form validates the requested seat count against the selected option's current availability.
5. A `Booking` record is saved with the user, travel option, seat count, calculated total, generated booking reference, and status.
6. The available-seat count is reduced by the number of seats booked.
7. The user can review the booking or cancel it. Cancellation changes the status and returns the seats to the option's available inventory.

**Important implementation note:** the current booking flow performs a normal availability check and update, but it does not wrap the booking and inventory update in a database transaction with row locking. For production or concurrent traffic, this should be strengthened to prevent two simultaneous requests from reserving the same remaining seats.

## Project Structure

```text
Booking_Travel-main/
├── booking/
│   ├── migrations/             # Database schema migrations
│   ├── templates/booking/      # HTML templates
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── travel_list.html
│   │   ├── booking_form.html
│   │   ├── booking_detail.html
│   │   ├── my_bookings.html
│   │   ├── register.html
│   │   ├── login.html
│   │   └── profile.html
│   ├── admin.py                # Django Admin configuration
│   ├── apps.py                 # Application configuration
│   ├── forms.py                # Registration, profile, search, booking forms
│   ├── models.py               # TravelOption, UserProfile, Booking
│   ├── tests.py                # Automated tests
│   ├── urls.py                 # Application URL routes
│   └── views.py                # Request handling and business logic
├── travel_booking/
│   ├── settings.py             # Django project settings
│   ├── urls.py                 # Root URL configuration
│   ├── asgi.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
├── README.md
└── db.sqlite3                  # Local development database, if included
```

## Data Models

### `TravelOption`

Represents a scheduled travel service.

| Field | Description |
|---|---|
| `travel_id` | Unique human-readable travel code |
| `type` | `flight`, `train`, or `bus` |
| `source` | Origin location |
| `destination` | Destination location |
| `date_time` | Scheduled departure date and time |
| `price` | Price per seat; validated to be non-negative |
| `available_seats` | Number of seats currently available |
| `created_at` | Record creation timestamp |

Travel options are ordered by departure date/time.

### `UserProfile`

Stores additional information for Django's built-in `User` model.

- `user`: one-to-one relationship with a Django user.
- `phone_number`: optional phone number.
- `address`: optional address.
- `date_of_birth`: optional date of birth.

### `Booking`

Represents a user's reservation.

| Field | Description |
|---|---|
| `booking_id` | Unique generated booking reference |
| `user` | User who made the booking |
| `travel_option` | Travel service being booked |
| `number_of_seats` | Number of seats requested; minimum 1 |
| `total_price` | Price per seat multiplied by the seat count |
| `booking_date` | Timestamp when the booking record was created |
| `status` | `confirmed` or `cancelled` |

Bookings are ordered newest first. The user-to-booking relationship allows each account to retrieve its own booking history.

## Getting Started

### Prerequisites

- Python 3.10 or later recommended.
- `pip` (Python package installer).
- Git, if cloning the repository.

### 1. Clone the repository

Replace the example URL below with the actual URL of your GitHub repository:

```bash
git clone https://github.com/<your-username>/<your-repository>.git
cd <your-repository>
```

If you already have the project files locally, open a terminal in the project root—the directory containing `manage.py`.

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

This creates or updates the local SQLite database according to the project's migrations.

### 5. Create an administrator account

```bash
python manage.py createsuperuser
```

Follow the prompts to choose a username and password.

### 6. Start the development server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

### 7. Add travel options

Open [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) and sign in with the superuser account. Add travel options with a unique travel ID, transport type, source, destination, future departure date/time, price, and available seats. You can then browse them from the public travel list.

## Using the Application

1. Visit the home page to see selected upcoming travel options.
2. Open **Travels** to browse available services.
3. Filter by mode of transport, origin, destination, or travel date.
4. Register for an account or log in.
5. Choose a travel option and enter the number of seats.
6. Review the booking confirmation and generated booking reference.
7. Open **My Bookings** to review your reservations.
8. Open a booking to see its details, or cancel a confirmed booking if needed.
9. Visit **Profile** to update your contact and personal details.

## URL Reference

| URL | Name | Access | Purpose |
|---|---|---|---|
| `/` | `home` | Public | Home page and recent travel options |
| `/register/` | `register` | Public | Create an account |
| `/login/` | `login` | Public | Sign in |
| `/logout/` | `logout` | Authenticated session | Sign out |
| `/profile/` | `profile` | Login required | View/update profile information |
| `/travels/` | `travel_list` | Public | Search and browse travel options |
| `/book/<travel_id>/` | `booking_create` | Login required | Book seats for a travel option (the route parameter is the database record ID) |
| `/my-bookings/` | `my_bookings` | Login required | List the current user's bookings |
| `/booking/<booking_id>/` | `booking_detail` | Login required; owner only | View a booking by its booking reference |
| `/cancel-booking/<booking_id>/` | `cancel_booking` | Login required; owner only | Cancel a confirmed booking |
| `/admin/` | Django Admin | Staff/superuser permissions | Manage application records |

## Running Tests

Run the automated tests for the `booking` application with:

```bash
python manage.py test booking
```

The test suite covers model creation, booking price calculation, basic page responses, registration, login requirements for booking, booking creation, and seat-count/cancellation behavior.

## Configuration and Security Notes

The repository's current settings are configured for local development. Before deploying publicly, make the following changes:

- **Secret key:** remove the hard-coded `SECRET_KEY` and load it from an environment variable. If the current key has been exposed in a public repository, rotate it.
- **Debug mode:** set `DEBUG = False` in production.
- **Allowed hosts:** configure `ALLOWED_HOSTS` for the deployed domain.
- **Database:** configure a production database and keep credentials outside source control.
- **Database file:** avoid committing a populated local `db.sqlite3` file if it contains personal or test data; use migrations to create the schema.
- **Seat inventory consistency:** use `transaction.atomic()` and appropriate row locking or conditional database updates to make booking/cancellation inventory changes safe under concurrent requests.
- **Cancellation requests:** make cancellation a POST action protected by CSRF rather than a state-changing GET request.
- **Static files and HTTPS:** configure static-file collection/serving, secure cookies, HTTPS, and Django's deployment checklist for the chosen hosting platform.
- **Environment variables:** never commit `.env` files, database passwords, API keys, or other secrets.

Useful command before deployment:

```bash
python manage.py check --deploy
```

This README documents the code as currently implemented; it does not imply that production deployment settings have already been applied.

## Possible Enhancements

- Add atomic seat reservations and concurrency tests.
- Add payment integration and booking invoices.
- Add email confirmation and cancellation notifications.
- Add booking history filters and status badges.
- Add sorting by price, departure time, and duration.
- Add a REST API with Django REST Framework serializers, permissions, and API tests if API access is required.
- Add automated CI checks and deployment instructions for the target hosting provider.
- Add screenshots or a short demo GIF to showcase the interface.

## Contributing

Contributions and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-change`.
3. Make your changes and add/update tests.
4. Run `python manage.py test booking`.
5. Commit your changes and open a pull request with a clear summary.

## License

No license file was present in the supplied project files. Add a `LICENSE` file if you want to specify how others may use, modify, and distribute this project.
