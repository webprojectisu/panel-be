# Backend Architecture Documentation

**Project:** Dietitian Management Panel API
**Stack:** FastAPI · SQLAlchemy 2.0 · MySQL 8.0 · Pydantic v2 · python-jose · passlib

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Layer Architecture](#2-layer-architecture)
3. [Core Module](#3-core-module)
4. [Schemas & Validation](#4-schemas--validation)
5. [Services](#5-services)
6. [Controllers](#6-controllers)
7. [Authentication & Authorization](#7-authentication--authorization)
8. [Global Error Handling](#8-global-error-handling)
9. [Route Index](#9-route-index)
10. [Adding a New Feature](#10-adding-a-new-feature)

---

## 1. Project Structure

```
panel-be/
├── main.py                          # App entry point — CORS, routers, error handlers
├── requirements.txt
├── docker-compose.yml               # MySQL 8.0 on port 3308
├── docs/
│   └── architecture.md             # This file
└── app/
    ├── db/
    │   └── base.py                  # SQLAlchemy engine, SessionLocal, Base, get_db()
    ├── models/                      # SQLAlchemy ORM models (11 models)
    │   ├── mixins.py                # TimestampMixin (created_at, updated_at)
    │   ├── associations.py          # MealFood, RecipeFood, diet_plan_recipe
    │   ├── user.py
    │   ├── client.py
    │   ├── appointment.py
    │   ├── measurement.py
    │   ├── diet_plan.py
    │   ├── meal.py
    │   ├── food.py
    │   ├── recipe.py
    │   ├── payment.py
    │   └── notification.py
    ├── core/                        # Cross-cutting concerns
    │   ├── exceptions.py            # Custom exception hierarchy
    │   ├── error_handlers.py        # Global FastAPI exception handlers
    │   ├── security.py              # JWT + bcrypt
    │   └── dependencies.py          # get_current_user FastAPI dependency
    ├── schemas/                     # Pydantic v2 request & response models
    │   ├── common.py
    │   ├── auth.py
    │   ├── user.py
    │   ├── client.py
    │   ├── appointment.py
    │   ├── diet_plan.py
    │   ├── meal.py
    │   ├── food.py
    │   ├── recipe.py
    │   ├── measurement.py
    │   ├── payment.py
    │   ├── notification.py
    │   └── dashboard.py
    ├── services/                    # Business logic + DB operations
    │   ├── auth_service.py
    │   ├── user_service.py
    │   ├── client_service.py
    │   ├── appointment_service.py
    │   ├── diet_plan_service.py
    │   ├── meal_service.py
    │   ├── food_service.py
    │   ├── recipe_service.py
    │   ├── measurement_service.py
    │   ├── payment_service.py
    │   ├── notification_service.py
    │   └── dashboard_service.py
    └── controllers/                 # FastAPI routers (thin, no try/except)
        ├── auth_controller.py
        ├── user_controller.py
        ├── client_controller.py
        ├── appointment_controller.py
        ├── diet_plan_controller.py
        ├── meal_controller.py
        ├── food_controller.py
        ├── recipe_controller.py
        ├── measurement_controller.py
        ├── payment_controller.py
        ├── notification_controller.py
        └── dashboard_controller.py
```

---

## 2. Layer Architecture

The app follows a strict three-layer architecture. Each layer has a single responsibility and a strict rule about where exception handling is allowed.

```
HTTP Request
     │
     ▼
┌─────────────────────────────────────────────────────┐
│  Controller  (app/controllers/)                     │
│  • FastAPI APIRouter                                │
│  • Declares routes, path/query params, status codes │
│  • Calls service functions                          │
│  • NO try/except — errors bubble up to global handler│
│  • Returns validated Pydantic response schemas      │
└──────────────────────────┬──────────────────────────┘
                           │ calls
                           ▼
┌─────────────────────────────────────────────────────┐
│  Service  (app/services/)                           │
│  • All business logic                               │
│  • All database queries (SQLAlchemy ORM)            │
│  • ALL try/except blocks live here                  │
│  • Raises custom AppException subclasses            │
│  • Checks authorization (dietitian ownership)       │
│  • Handles transactions (commit / rollback)         │
└──────────────────────────┬──────────────────────────┘
                           │ queries
                           ▼
┌─────────────────────────────────────────────────────┐
│  Models  (app/models/)                              │
│  • SQLAlchemy ORM table definitions                 │
│  • Relationships, indexes, constraints              │
└─────────────────────────────────────────────────────┘
```

**Request lifecycle:**

```
Request body
  → Pydantic schema validation (automatic, raises RequestValidationError)
  → Controller function called
  → Controller calls service function
  → Service executes DB query, runs business rules
  → Service raises AppException on failure
  → Global error handler converts exception → JSON response
  → Controller returns Pydantic response schema → JSON
```

---

## 3. Core Module

### `app/core/exceptions.py`

Custom exception hierarchy. Every domain error is an `AppException` subclass so the global handler can catch them all uniformly.

```
AppException (base)
├── NotFoundException     → HTTP 404  / error_code: NOT_FOUND
├── ConflictException     → HTTP 409  / error_code: CONFLICT
├── ForbiddenException    → HTTP 403  / error_code: FORBIDDEN
├── UnauthorizedException → HTTP 401  / error_code: UNAUTHORIZED
└── BadRequestException   → HTTP 400  / error_code: BAD_REQUEST
```

All exceptions accept an optional `detail: str` override. Raise them like:

```python
raise NotFoundException(f"Client with id={client_id} not found.")
raise ConflictException("Email is already registered.")
raise ForbiddenException()  # uses class-level default message
```

### `app/core/security.py`

| Function | Description |
|---|---|
| `hash_password(plain)` | bcrypt hash via passlib |
| `verify_password(plain, hashed)` | bcrypt verify |
| `create_access_token(data, expires_delta)` | HS256 JWT signed with `SECRET_KEY` |
| `decode_token(token)` | Decodes JWT; raises `UnauthorizedException` on invalid/expired token |

**Environment variables:**

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `"change-me-in-production"` | JWT signing key — **must be changed in production** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token lifetime in minutes |
| `ALGORITHM` | `"HS256"` | Hardcoded, not configurable |

### `app/core/dependencies.py`

Provides two FastAPI dependencies used across all controllers:

- **`get_db`** — yields a `Session`, re-exported from `app.db.base`
- **`get_current_user`** — extracts Bearer token from `Authorization` header, decodes it, fetches the `User` from DB. Raises `UnauthorizedException` if the token is invalid, the user is not found, or the account is inactive.

Usage in a controller:

```python
from typing import Annotated
from fastapi import Depends
from app.core.dependencies import get_current_user, get_db

@router.get("/example")
def example(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    ...
```

---

## 4. Schemas & Validation

All request/response models are Pydantic v2. Response schemas set `model_config = ConfigDict(from_attributes=True)` so they can be built directly from SQLAlchemy model instances.

### Validation rules applied to user input fields

| Field type | Rule |
|---|---|
| **full_name / title** | Strip whitespace · min 2 chars · max 150 chars · only letters, spaces, hyphens, apostrophes, Turkish chars (ğüşıöçĞÜŞİÖÇ) · cannot be purely numeric |
| **email** | Pydantic `EmailStr` · strip and lowercase · max 255 chars |
| **phone** | Strip all spaces/dashes/parens · must be digits only after stripping · 7–15 digits · leading `+` allowed |
| **password** | Min 8 chars · max 128 · must contain at least 1 uppercase, 1 lowercase, 1 digit |
| **date_of_birth** | Cannot be in the future · cannot be before 1900-01-01 |
| **start_date / end_date** | `end_date` must be after `start_date` — enforced via `model_validator(mode='after')` |
| **start_time / end_time** | `end_time` must be after `start_time` — enforced via `model_validator(mode='after')` |
| **amount** | Must be > 0 · max 2 decimal places · `Decimal` type |
| **currency** | 3-letter uppercase ISO 4217 code (e.g. `TRY`, `USD`) · default `TRY` |
| **height_cm** | 50.0 – 300.0 |
| **weight_kg** | 1.0 – 500.0 |
| **bmi** | 5.0 – 100.0 (auto-computed if `height_cm` + `weight_kg` are given but `bmi` is not) |
| **body_fat_percentage** | 0.0 – 100.0 |
| **waist_cm / hip_cm / chest_cm** | 10.0 – 300.0 |
| **notes / description** | Strip whitespace · max 2000 chars |
| **instructions** | Strip whitespace · max 10 000 chars |
| **portion_size** | Max 50 chars |
| **preparation_time_minutes** | > 0 · max 1440 (24 h) |
| **quantity_g** (food in meal/recipe) | > 0 · max 10 000 |
| **calories / protein / carbs / fat** | ≥ 0 |
| **skip** (pagination) | ≥ 0 |
| **limit** (pagination) | 1 – 100 |

### Validator pattern

Validators are implemented as `@field_validator` class methods (Pydantic v2 style). Shared validators (e.g. `_validate_full_name`, `_validate_phone`) are defined once in `app/schemas/auth.py` and imported by other schema files to avoid duplication.

```python
from pydantic import BaseModel, field_validator, model_validator

class DietPlanCreate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @model_validator(mode="after")
    def check_date_range(self) -> "DietPlanCreate":
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date.")
        return self
```

---

## 5. Services

### Rules

- Accept `db: Session` as the first argument (injected by FastAPI via `Depends(get_db)`).
- **All try/except blocks live here** — nowhere else.
- Always check **authorization** before acting: first confirm the resource exists (`NotFoundException`), then confirm it belongs to the current dietitian (`ForbiddenException`). This order prevents information leakage.
- Use `db.commit()` after writes. Use `db.rollback()` in the except clause of mutating operations.

### Authorization pattern

```python
def get_client(db: Session, client_id: int, dietitian_id: int) -> Client:
    try:
        client = db.get(Client, client_id)
        if client is None:
            raise NotFoundException(f"Client with id={client_id} not found.")
        if client.dietitian_id != dietitian_id:
            raise ForbiddenException()
        return client
    except (NotFoundException, ForbiddenException):
        raise
    except Exception as exc:
        raise exc
```

### Notable service behaviors

| Service | Behavior |
|---|---|
| `auth_service.login` | Raises `UnauthorizedException` (not `NotFoundException`) for wrong email/password to avoid revealing whether an email exists |
| `appointment_service.create_appointment` | Detects overlapping time slots for the same dietitian on the same date (excluding cancelled appointments) |
| `food_service.delete_food` | Checks `MealFood` and `RecipeFood` tables; raises `BadRequestException("Food is in use")` before deleting |
| `measurement_service.create_measurement` | Auto-computes `bmi = weight_kg / (height_cm / 100)²` when `height_cm` and `weight_kg` are provided but `bmi` is not |
| `meal_service.add_food_to_meal` | Upserts: if the food is already in the meal, updates `quantity_g` instead of creating a duplicate |
| `recipe_service.create_recipe` | Verifies all `food_id` values exist before creating `RecipeFood` entries |
| `dashboard_service.get_stats` | Computes `success_rate` as `completed / (completed + cancelled + no_show)` for appointments in the last 30 days |
| `payment_service.get_payment_summary` | Returns 6-month monthly income trend, breakdown by payment method |

---

## 6. Controllers

### Rules

- Use `APIRouter` with a `prefix` and `tags`.
- **No try/except blocks** — errors raised in services propagate to the global handler.
- Declare all dependencies with `Annotated[T, Depends(...)]`.
- Return Pydantic response schemas built with `Model.model_validate(orm_obj)`.
- Use `status_code=status.HTTP_201_CREATED` on POST endpoints, `status_code=status.HTTP_204_NO_CONTENT` on DELETE endpoints.

### Example controller function

```python
@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    data: ClientCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ClientResponse:
    client = client_service.create_client(db, current_user.id, data)
    return ClientResponse.model_validate(client)
```

### Path ordering

Static path segments must be registered **before** parameterized ones to avoid FastAPI treating them as path parameter values.

```python
# CORRECT ORDER
@router.get("/today")           # registered first
@router.get("/{appointment_id}")  # registered second

@router.get("/unread-count")    # registered first
@router.put("/read-all")        # registered second
@router.put("/{notification_id}/read")  # registered third
```

---

## 7. Authentication & Authorization

### Flow

```
Client                          Server
  │                               │
  │  POST /auth/login             │
  │  { email, password }  ──────► │
  │                               │  1. Find user by email
  │                               │  2. verify_password(plain, hash)
  │                               │  3. create_access_token({"sub": user.id})
  │  { access_token, user } ◄──── │
  │                               │
  │  GET /clients                 │
  │  Authorization: Bearer <token>│
  │  ────────────────────────────►│
  │                               │  1. oauth2_scheme extracts token
  │                               │  2. decode_token() → payload
  │                               │  3. db.get(User, payload["sub"])
  │                               │  4. check is_active
  │  [ client list ] ◄───────────│
```

### Token payload

```json
{
  "sub": "<user_id>",
  "exp": "<unix_timestamp>"
}
```

### Protected vs public endpoints

| Public (no auth required) | Protected (Bearer token required) |
|---|---|
| `POST /auth/login` | All other endpoints |
| `POST /auth/register` | |
| `GET /` | |

### Admin-only endpoints

`GET /users` checks `current_user.role == UserRole.admin` in the controller and raises `ForbiddenException` if not.

---

## 8. Global Error Handling

Registered in `main.py` via `register_error_handlers(app)` from `app/core/error_handlers.py`.

### Handlers

| Exception type | Status | error_code |
|---|---|---|
| `AppException` (and all subclasses) | from exception | from exception |
| `RequestValidationError` (Pydantic) | 422 | `VALIDATION_ERROR` |
| `Exception` (catch-all) | 500 | `INTERNAL_ERROR` |

### Uniform response envelope

Every error response — regardless of source — returns this shape:

```json
{
  "error": "NOT_FOUND",
  "message": "Client with id=42 not found.",
  "status_code": 404
}
```

Pydantic validation errors include an additional `details` array with per-field information:

```json
{
  "error": "VALIDATION_ERROR",
  "message": "full_name: Name must be at least 2 characters long.; phone: Phone must contain 7–15 digits.",
  "status_code": 422,
  "details": [
    { "field": "full_name", "message": "Name must be at least 2 characters long.", "type": "value_error" },
    { "field": "phone",     "message": "Phone must contain 7–15 digits.",          "type": "value_error" }
  ]
}
```

The 500 catch-all handler **logs** the full traceback server-side via `logger.exception(...)` but **hides** internal details from the client.

---

## 9. Route Index

All 65 registered routes:

```
Method   Path
──────   ────────────────────────────────────────────
GET      /

POST     /auth/login
POST     /auth/register
POST     /auth/logout
POST     /auth/refresh

GET      /users/me
PUT      /users/me
PUT      /users/me/password
GET      /users                              (admin only)

GET      /clients
POST     /clients
GET      /clients/{client_id}
PUT      /clients/{client_id}
DELETE   /clients/{client_id}
GET      /clients/{client_id}/summary
GET      /clients/{client_id}/measurements
POST     /clients/{client_id}/measurements
GET      /clients/{client_id}/measurements/latest

GET      /appointments
POST     /appointments
GET      /appointments/today
GET      /appointments/{appointment_id}
PUT      /appointments/{appointment_id}
DELETE   /appointments/{appointment_id}

GET      /diet-plans
POST     /diet-plans
GET      /diet-plans/{plan_id}
PUT      /diet-plans/{plan_id}
DELETE   /diet-plans/{plan_id}
GET      /diet-plans/{plan_id}/meals
POST     /diet-plans/{plan_id}/meals
POST     /diet-plans/{plan_id}/recipes/{recipe_id}
DELETE   /diet-plans/{plan_id}/recipes/{recipe_id}

PUT      /meals/{meal_id}
DELETE   /meals/{meal_id}
POST     /meals/{meal_id}/foods
DELETE   /meals/{meal_id}/foods/{food_id}

GET      /foods
POST     /foods
GET      /foods/{food_id}
PUT      /foods/{food_id}
DELETE   /foods/{food_id}

GET      /recipes
POST     /recipes
GET      /recipes/{recipe_id}
PUT      /recipes/{recipe_id}
DELETE   /recipes/{recipe_id}
POST     /recipes/{recipe_id}/foods
DELETE   /recipes/{recipe_id}/foods/{food_id}

DELETE   /measurements/{measurement_id}

GET      /payments
POST     /payments
GET      /payments/summary
GET      /payments/{payment_id}
PUT      /payments/{payment_id}
DELETE   /payments/{payment_id}

GET      /notifications
GET      /notifications/unread-count
PUT      /notifications/read-all
PUT      /notifications/{notification_id}/read

GET      /dashboard/stats
```

**Interactive docs available at runtime:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 10. Adding a New Feature

Follow these steps every time a new resource is added:

**1. Model** — add `app/models/your_model.py`, import it in `app/models/__init__.py`.

**2. Schema** — add `app/schemas/your_model.py` with:
- `YourModelCreate` — validated input fields
- `YourModelUpdate` — all fields optional, same validators
- `YourModelResponse` — `model_config = ConfigDict(from_attributes=True)`

**3. Service** — add `app/services/your_model_service.py`:
- All functions receive `db: Session` as first arg
- Wrap DB operations in `try/except`, re-raise `AppException` subclasses, rollback on mutation errors
- Check existence → `NotFoundException`, then ownership → `ForbiddenException`

**4. Controller** — add `app/controllers/your_model_controller.py`:
- `router = APIRouter(prefix="/your-models", tags=["Your Models"])`
- No try/except
- Use `Annotated[User, Depends(get_current_user)]` for auth
- Use correct HTTP status codes (201 for POST, 204 for DELETE)

**5. Register** — import the router in `main.py` and call `app.include_router(your_router)`.

**6. Dependencies** — if new packages are needed, add to `requirements.txt`.
