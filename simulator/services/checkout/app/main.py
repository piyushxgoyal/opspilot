"""HTTP API for the AcmeCloud checkout service.

Phase 0 exposes two endpoints:

GET  /health
    Verifies that the service and its PostgreSQL dependency are
    reachable.

POST /checkout
    Creates and persists a basic order.

This service represents part of the simulated AcmeCloud production
environment. It is intentionally small in Phase 0. Additional
business dependencies and failure modes will be introduced in later
phases.
"""

import uuid
from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from .db import get_db
from .models import Order

SERVICE_NAME = "checkout-service"
SERVICE_VERSION = "2.4.0"

app = FastAPI(
    title="AcmeCloud Checkout Service",
    version=SERVICE_VERSION,
    description=("Checkout API belonging to the simulated AcmeCloud environment."),
)


class CheckoutRequest(BaseModel):
    """Request body used to create an order."""

    customer_id: uuid.UUID
    total_amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)


class CheckoutResponse(BaseModel):
    """Response returned after an order is created."""

    order_id: uuid.UUID
    status: str


@app.get("/health")
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    """Return service health and verify PostgreSQL connectivity.

    A service is not considered healthy merely because the HTTP process
    is running. PostgreSQL connectivity is part of the service's
    dependency health.
    """
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": SERVICE_NAME,
                "database": "unavailable",
            },
        ) from exc

    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "database": "healthy",
    }


@app.post("/checkout", response_model=CheckoutResponse, status_code=201)
def checkout(
    request: CheckoutRequest,
    db: Session = Depends(get_db),
) -> CheckoutResponse:
    """Create and persist an order.

    The Phase 0 checkout flow only persists the order. Payment,
    inventory, notification, authentication, and other AcmeCloud
    dependencies will be introduced in later phases.
    """
    order = Order(
        id=uuid.uuid4(),
        customer_id=request.customer_id,
        status="confirmed",
        total_amount=request.total_amount,
        currency=request.currency.upper(),
    )

    db.add(order)
    db.commit()

    return CheckoutResponse(
        order_id=order.id,
        status=order.status,
    )
