# NutriFlow — Dietitian Management Panel

A modern, full-stack digital clinic management system designed for dietitians to manage clients, appointments, nutrition programs, measurements, and business operations.

## Overview

NutriFlow is a comprehensive web application that helps dietitians run their practice efficiently. The system provides tools for client management, appointment scheduling, nutrition program creation, measurement tracking, recipe management, financial tracking, and analytics — all in one unified platform.

## Repository Structure

```
asd/
├── panel-be/              # FastAPI backend (REST API + MySQL database)
├── panel-fe/              # React frontend (Vite + modern UI)
├── docs/                  # Documentation
│   └── architecture.md    # Backend architecture details
└── README.md              # This file
```

## Features

### Client Management
- Complete client profiles with personal information
- Health goals and dietary preferences tracking
- Client status management (active, inactive, archived)
- Client summary dashboard with key metrics

### Appointment System
- Calendar-based appointment scheduling
- Multiple appointment types (in-person, online, follow-up)
- Status tracking (scheduled, completed, cancelled, no-show)
- Conflict detection for overlapping time slots
- Today's appointments quick view

### Nutrition Programs
- Custom diet plan creation for each client
- Meal planning with detailed food composition
- Recipe library with nutritional information
- Program status tracking (draft, active, paused, completed)
- Assign recipes to diet plans

### Measurement Tracking
- Body measurements (weight, height, BMI, body fat %)
- Circumference measurements (waist, hip, chest)
- Automatic BMI calculation
- Historical tracking and trend visualization
- Latest measurement quick access

### Recipe & Food Database
- Comprehensive food database with nutritional values
- Recipe creation with ingredient lists
- Calorie and macronutrient tracking
- Preparation time and instructions
- Add foods to meals and recipes

### Business Management
- Payment tracking with multiple payment methods
- Income analytics and monthly trends
- Payment status management (completed, pending, failed, refunded)
- Financial summary reports

### Dashboard & Analytics
- Real-time statistics (active clients, appointments, success rate)
- Revenue tracking and trends
- Appointment analytics
- Client success metrics

### Notifications
- System notifications for important events
- Unread notification counter
- Mark as read functionality
- Bulk read-all option

## Quick Start

### Prerequisites

- **Python 3.11+** for backend
- **Node.js 18+** for frontend
- **MySQL 8.0** (via Docker or local installation)

### 1. Start the Database

Using Docker (recommended):

```bash
cd panel-be
docker-compose up -d
```

This starts MySQL 8.0 on port **3308** with database `nutriflow_db`.

### 2. Start the Backend

```bash
cd panel-be
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

**Interactive API documentation:**
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

### 3. Start the Frontend

Open a **new terminal**:

```bash
cd panel-fe
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`.

> **Note:** The backend must be running for the frontend to function properly.

### 4. Login

Use the default admin credentials (or register a new account):

```
Email: admin@nutriflow.com
Password: Admin123!
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login with email and password |
| POST | `/api/auth/register` | Register new dietitian account |
| POST | `/api/auth/logout` | Logout current session |
| POST | `/api/auth/refresh` | Refresh access token |

### User Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/me` | Get current user profile |
| PUT | `/api/users/me` | Update current user profile |
| PUT | `/api/users/me/password` | Change password |
| GET | `/api/users` | List all users (admin only) |

### Clients
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/clients` | List all clients |
| POST | `/api/clients` | Create a new client |
| GET | `/api/clients/{id}` | Get client details |
| PUT | `/api/clients/{id}` | Update client |
| DELETE | `/api/clients/{id}` | Delete client |
| GET | `/api/clients/{id}/summary` | Get client summary with stats |
| GET | `/api/clients/{id}/measurements` | Get client measurements |
| POST | `/api/clients/{id}/measurements` | Add measurement |
| GET | `/api/clients/{id}/measurements/latest` | Get latest measurement |

### Appointments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/appointments` | List appointments (with date filters) |
| POST | `/api/appointments` | Create appointment |
| GET | `/api/appointments/today` | Get today's appointments |
| GET | `/api/appointments/{id}` | Get appointment details |
| PUT | `/api/appointments/{id}` | Update appointment |
| DELETE | `/api/appointments/{id}` | Delete appointment |

### Diet Plans
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/diet-plans` | List all diet plans |
| POST | `/api/diet-plans` | Create diet plan |
| GET | `/api/diet-plans/{id}` | Get plan details |
| PUT | `/api/diet-plans/{id}` | Update plan |
| DELETE | `/api/diet-plans/{id}` | Delete plan |
| GET | `/api/diet-plans/{id}/meals` | Get plan meals |
| POST | `/api/diet-plans/{id}/meals` | Add meal to plan |
| POST | `/api/diet-plans/{id}/recipes/{recipe_id}` | Assign recipe to plan |
| DELETE | `/api/diet-plans/{id}/recipes/{recipe_id}` | Remove recipe from plan |

### Meals
| Method | Endpoint | Description |
|--------|----------|-------------|
| PUT | `/api/meals/{id}` | Update meal |
| DELETE | `/api/meals/{id}` | Delete meal |
| POST | `/api/meals/{id}/foods` | Add food to meal |
| DELETE | `/api/meals/{id}/foods/{food_id}` | Remove food from meal |

### Foods
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/foods` | List all foods |
| POST | `/api/foods` | Create food |
| GET | `/api/foods/{id}` | Get food details |
| PUT | `/api/foods/{id}` | Update food |
| DELETE | `/api/foods/{id}` | Delete food |

### Recipes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/recipes` | List all recipes |
| POST | `/api/recipes` | Create recipe |
| GET | `/api/recipes/{id}` | Get recipe details |
| PUT | `/api/recipes/{id}` | Update recipe |
| DELETE | `/api/recipes/{id}` | Delete recipe |
| POST | `/api/recipes/{id}/foods` | Add food to recipe |
| DELETE | `/api/recipes/{id}/foods/{food_id}` | Remove food from recipe |

### Measurements
| Method | Endpoint | Description |
|--------|----------|-------------|
| DELETE | `/api/measurements/{id}` | Delete measurement |

### Payments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/payments` | List all payments |
| POST | `/api/payments` | Create payment record |
| GET | `/api/payments/summary` | Get payment summary with trends |
| GET | `/api/payments/{id}` | Get payment details |
| PUT | `/api/payments/{id}` | Update payment |
| DELETE | `/api/payments/{id}` | Delete payment |

### Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications` | List notifications |
| GET | `/api/notifications/unread-count` | Get unread count |
| PUT | `/api/notifications/read-all` | Mark all as read |
| PUT | `/api/notifications/{id}/read` | Mark notification as read |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/stats` | Get dashboard statistics |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Vite, React Router, Chart.js, Axios |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| **Database** | MySQL 8.0 |
| **Authentication** | JWT (python-jose), bcrypt (passlib) |
| **Validation** | Pydantic v2 with custom validators |
| **API Docs** | OpenAPI (Swagger UI, ReDoc) |

## Architecture

The backend follows a strict **three-layer architecture**:

```
┌─────────────────────────────────────────────────────┐
│  Controllers (app/controllers/)                     │
│  • FastAPI routers                                  │
│  • Route definitions and HTTP handling              │
│  • No business logic or try/except blocks           │
└──────────────────────────┬──────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│  Services (app/services/)                           │
│  • All business logic                               │
│  • Database operations                              │
│  • Authorization checks                             │
│  • Exception handling                               │
└──────────────────────────┬──────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│  Models (app/models/)                               │
│  • SQLAlchemy ORM definitions                       │
│  • Relationships and constraints                    │
└─────────────────────────────────────────────────────┘
```

For detailed architecture documentation, see [`docs/architecture.md`](docs/architecture.md).

## Key Features

### Authentication & Authorization
- JWT-based authentication with Bearer tokens
- Password hashing with bcrypt
- Role-based access control (dietitian, admin)
- Resource ownership validation (dietitians can only access their own data)

### Data Validation
- Comprehensive Pydantic v2 schemas with custom validators
- Email, phone, password strength validation
- Date range and time range validation
- Numeric constraints (BMI, measurements, amounts)
- Turkish character support in names

### Error Handling
- Global exception handlers for consistent error responses
- Custom exception hierarchy (NotFoundException, ConflictException, etc.)
- Uniform error response format with error codes
- Detailed validation error messages

### Business Logic
- Automatic BMI calculation from height and weight
- Appointment conflict detection
- Payment summary with monthly trends
- Client success rate calculation
- Resource usage checks before deletion

## Environment Variables

Create a `.env` file in `panel-be/`:

```env
# Database
DATABASE_URL=mysql+pymysql://nutriflow_user:nutriflow_pass@localhost:3308/nutriflow_db

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM=HS256

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Development

### Running Tests

```bash
cd panel-be
pytest
```

### Database Migrations

The application uses SQLAlchemy models. To reset the database:

```bash
# Stop the app
# Drop and recreate the database in MySQL
# Restart the app - tables will be created automatically
```

### Code Style

- **Backend:** Follow PEP 8, use type hints
- **Frontend:** ESLint + Prettier configuration included

## Screenshots

### Dashboard
<img src="screenshots/dashboard.PNG" width="45%"/>

### Clients
<img src="screenshots/client.PNG" width="45%"/>

### Appointments
<img src="screenshots/appointment.PNG" width="45%"/>

### Recipes
<img src="screenshots/recipe.PNG" width="45%"/>

## License

This project is developed for educational purposes.

## Support

For issues and questions, please refer to the documentation in the `docs/` folder or contact the development team.
