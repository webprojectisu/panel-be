# Phase 1 — Dietitian Management Panel (Backend)

## Project Overview

A full-stack **Dietitian Management Web Panel** backend built with FastAPI.
The backend manages dietitians, their clients, appointments, diet plans, measurements, payments, and notifications.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy (declarative, mapped columns) |
| Database | MySQL 8.0 (running in Docker) |
| Validation | Pydantic |
| Migrations | Alembic (set up, not yet used — `create_all` used for now) |
| DB Driver | PyMySQL (`mysql+pymysql://`) |
| Env loading | python-dotenv |
| Container | Docker + Docker Compose |

---

## Project Structure

```
panel-be/
├── app/
│   ├── __init__.py
│   ├── db/
│   │   ├── __init__.py
│   │   └── base.py              # Base, engine, SessionLocal, get_db()
│   └── models/
│       ├── __init__.py          # Imports all models (required for create_all)
│       ├── mixins.py            # TimestampMixin (created_at, updated_at)
│       ├── associations.py      # MealFood, RecipeFood, diet_plan_recipe
│       ├── user.py
│       ├── client.py
│       ├── appointment.py
│       ├── measurement.py
│       ├── diet_plan.py
│       ├── meal.py
│       ├── food.py
│       ├── recipe.py
│       ├── payment.py
│       └── notification.py
├── main.py                      # FastAPI app entry point with lifespan
├── docker-compose.yml
├── requirements.txt
├── .env                         # Gitignored — real secrets
├── .env.example                 # Safe template to commit
├── .gitignore
└── phase_1_prompt.md            # This file
```

---

## Database Design

### Models & Fields

#### User
Represents a dietitian (or admin) using the panel.
- `id`, `full_name`, `email` (unique), `password_hash`, `phone`
- `role` → Enum: `admin`, `dietitian`
- `is_active` → Boolean
- `created_at`, `updated_at` (via TimestampMixin)

#### Client
A client assigned to a dietitian.
- `id`, `dietitian_id` (FK → users), `full_name`, `email`, `phone`
- `date_of_birth`, `gender` → Enum: `male`, `female`, `other`
- `notes` (Text)
- `created_at`, `updated_at`

#### Appointment
A scheduled session between dietitian and client.
- `id`, `dietitian_id` (FK → users), `client_id` (FK → clients)
- `appointment_date`, `start_time`, `end_time`
- `status` → Enum: `scheduled`, `completed`, `cancelled`, `no_show`
- `notes` (Text)
- `created_at`, `updated_at`

#### Measurement
A snapshot of a client's body metrics at a point in time. Immutable (no `updated_at`).
- `id`, `client_id` (FK → clients)
- `height_cm`, `weight_kg`, `bmi`, `body_fat_percentage`, `waist_cm`, `hip_cm`, `chest_cm` (all Numeric 5,2)
- `recorded_at`, `notes`
- BMI stored explicitly to preserve historical accuracy.

#### DietPlan
A structured nutrition plan created by a dietitian for a client.
- `id`, `client_id` (FK → clients), `dietitian_id` (FK → users)
- `title`, `description` (Text)
- `start_date`, `end_date`
- `status` → Enum: `draft`, `active`, `paused`, `completed`
- `created_at`, `updated_at`

#### Meal
A single meal slot within a diet plan.
- `id`, `diet_plan_id` (FK → diet_plans)
- `name`, `meal_type` → Enum: `breakfast`, `lunch`, `dinner`, `snack`, `pre_workout`, `post_workout`
- `scheduled_time`, `notes`
- `created_at`, `updated_at`

#### Food
A reusable food item with nutritional values (per 100g).
- `id`, `name`
- `calories`, `protein`, `carbs`, `fat` (Numeric)
- `portion_size`, `description`
- `created_at`, `updated_at`

#### Recipe
A reusable recipe that can be referenced by diet plans.
- `id`, `title`, `description`, `instructions` (Text)
- `preparation_time_minutes`, `calories` (Numeric)
- `created_at`, `updated_at`

#### Payment
A payment record between a client and a dietitian.
- `id`, `client_id` (FK → clients), `dietitian_id` (FK → users)
- `amount` (Numeric 10,2 — DECIMAL, never Float for money)
- `currency` (String 3, default `TRY`)
- `payment_date`, `payment_method` → Enum: `cash`, `credit_card`, `debit_card`, `bank_transfer`, `online`
- `status` → Enum: `pending`, `completed`, `failed`, `refunded`
- `notes`, `created_at`, `updated_at`

#### Notification
An in-app notification for a user. Immutable (no `updated_at`).
- `id`, `user_id` (FK → users)
- `title`, `message` (Text)
- `is_read` (Boolean, default False)
- `created_at`

---

### Association Tables / Models

| Name | Type | Extra Columns | Purpose |
|---|---|---|---|
| `MealFood` | Full model | `quantity_g` (Numeric 7,2) | Food items inside a meal with portion weight |
| `RecipeFood` | Full model | `quantity_g` (Numeric 7,2) | Food ingredients inside a recipe with weight |
| `diet_plan_recipe` | Plain `Table` | — | Links diet plans to recipes (no extra data) |

---

### Relationships

| From | To | Type | Via |
|---|---|---|---|
| User | Client | One-to-many | `Client.dietitian_id` |
| User | Appointment | One-to-many | `Appointment.dietitian_id` |
| User | DietPlan | One-to-many | `DietPlan.dietitian_id` |
| User | Payment | One-to-many | `Payment.dietitian_id` |
| User | Notification | One-to-many | `Notification.user_id` |
| Client | Appointment | One-to-many | `Appointment.client_id` |
| Client | Measurement | One-to-many | `Measurement.client_id` |
| Client | DietPlan | One-to-many | `DietPlan.client_id` |
| Client | Payment | One-to-many | `Payment.client_id` |
| DietPlan | Meal | One-to-many | `Meal.diet_plan_id` |
| Meal | Food | Many-to-many | `MealFood` model |
| Recipe | Food | Many-to-many | `RecipeFood` model |
| DietPlan | Recipe | Many-to-many | `diet_plan_recipe` table |

All relationships use `back_populates` consistently (no `backref`).
Cascades: `all, delete-orphan` on all parent → child one-to-many relationships.

---

## Docker Setup

**docker-compose.yml**
- Service: `db` → MySQL 8.0
- Container name: `panel_db`
- Host port `3308` → container port `3306`
- Named volume: `panel_db_data` (persists data between restarts)
- Network: `panel_network` (bridge) — future FastAPI service will join this same network and connect to DB via `panel_db:3306`
- Health check: `mysqladmin ping`

**Credentials (hardcoded for dev):**
```
MYSQL_ROOT_PASSWORD: rootpassword
MYSQL_DATABASE:      panel_db
MYSQL_USER:          panel_user
MYSQL_PASSWORD:      panel_pass
```

**DATABASE_URL (in .env and base.py fallback):**
```
mysql+pymysql://panel_user:panel_pass@localhost:3308/panel_db
```

---

## app/db/base.py

- Loads `.env` via `load_dotenv()`
- Reads `DATABASE_URL` from environment
- Creates SQLAlchemy `engine` with `pool_pre_ping=True` and `pool_recycle=3600`
- Exposes `SessionLocal`, `Base`, and `get_db()` dependency

---

## main.py

- Uses FastAPI `lifespan` context manager (modern replacement for `@app.on_event`)
- On startup: imports all models via `import app.models`, then calls `Base.metadata.create_all(bind=engine)`
- This creates all tables automatically when uvicorn starts

> **Important:** `import app.models` must happen before `create_all()` — SQLAlchemy only knows about a table if its model class has been imported and registered with `Base.metadata`.

---

## requirements.txt

```
fastapi
uvicorn[standard]
sqlalchemy
alembic
pymysql
cryptography
pydantic
pydantic-settings
python-dotenv
```

---

## Alembic Migration Order (planned, not yet initialized)

When switching from `create_all` to Alembic:
```
1.  users
2.  clients              (FK → users)
3.  appointments         (FK → users, clients)
4.  measurements         (FK → clients)
5.  foods
6.  recipes
7.  diet_plans           (FK → users, clients)
8.  meals                (FK → diet_plans)
9.  diet_plan_recipe     (FK → diet_plans, recipes)
10. meal_foods           (FK → meals, foods)
11. recipe_foods         (FK → recipes, foods)
12. payments             (FK → users, clients)
13. notifications        (FK → users)
```

---

## Known Notes & Decisions

- Pylance warnings (`sqlalchemy could not be resolved`) appear because SQLAlchemy is not installed in the local Python environment. Run `pip install -r requirements.txt` to fix.
- `Measurement` and `Notification` are intentionally immutable — no `updated_at`.
- `currency` field defaults to `TRY` — change to match target market.
- No timezone on `DateTime` fields — UTC convention enforced at the app layer.
- Alembic is in `requirements.txt` but not yet initialized. `create_all` is used for now during early development.
- Soft-delete (`is_deleted` column) not yet implemented — cascading hard deletes are used.

---

## What Comes Next (Phase 2)

- [ ] Pydantic schemas (request/response models)
- [ ] FastAPI routers for each entity
- [ ] Authentication (JWT)
- [ ] Alembic migration setup (`alembic init`)
- [ ] Add FastAPI app service to docker-compose
