# TSK Auth Service

**Authentication microservice** for the TSK Task Scheduler (TSK) project.

This service handles **user registration, login, and JWT authentication**, built with **Django** and **Django REST Framework**. It is part of the full TSK microservices stack.

---

## Purpose

* User registration
* Login and JWT token issuance
* Token refresh
* Authentication for other microservices (calendar, email)

This service does **not** implement domain functionality; it only manages users and authentication.

---

## Tech Stack

* Python ≥ 3.10
* Django ≥ 5.1
* Django REST Framework
* djangorestframework-simplejwt
* Poetry for dependency management

Dependencies are listed in `pyproject.toml`.

---

## Installation

```bash
git clone https://github.com/Codeminister2137/tsk-auth-service.git
cd tsk-auth-service
poetry install
```

---

## Running the Service

Run migrations:

```bash
poetry run python manage.py migrate
```

Start the development server:

```bash
poetry run python manage.py runserver
```

By default, the server runs at `http://127.0.0.1:8000/`.

---

## API Endpoints

* **POST /api/token/** — issue JWT tokens
* **POST /api/token/refresh/** — refresh access token
* **User registration & profile endpoints** — as implemented

All protected endpoints require valid JWT tokens.

---

## Repository Structure

```
auth_app/                   # Django app with auth logic
tests/                      # Unit and integration tests
tsk_auth_service/           # Django project settings
manage.py                   # Django CLI utility
pyproject.toml              # Poetry dependencies
```

---

## Status

Fully implements JWT-based authentication and user management. Intended to integrate with Calendar and Email services.

---

## License

MIT License
