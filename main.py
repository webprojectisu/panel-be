from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.base import Base, engine
import app.models  # noqa: F401 — registers all models with Base before create_all

from app.core.error_handlers import register_error_handlers

# Controllers
from app.controllers.auth_controller import router as auth_router
from app.controllers.user_controller import router as user_router
from app.controllers.client_controller import router as client_router
from app.controllers.appointment_controller import router as appointment_router
from app.controllers.diet_plan_controller import router as diet_plan_router
from app.controllers.meal_controller import router as meal_router
from app.controllers.food_controller import router as food_router
from app.controllers.recipe_controller import router as recipe_router
from app.controllers.measurement_controller import router as measurement_router
from app.controllers.payment_controller import router as payment_router
from app.controllers.notification_controller import router as notification_router
from app.controllers.dashboard_controller import router as dashboard_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Dietitian Management Panel",
    description="Backend API for a dietitian management application.",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Global error handlers
# ---------------------------------------------------------------------------
register_error_handlers(app)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(client_router)
app.include_router(appointment_router)
app.include_router(diet_plan_router)
app.include_router(meal_router)
app.include_router(food_router)
app.include_router(recipe_router)
app.include_router(measurement_router)
app.include_router(payment_router)
app.include_router(notification_router)
app.include_router(dashboard_router)


@app.get("/", tags=["Health"])
def read_root() -> dict:
    return {"message": "Dietitian Management Panel API"}
