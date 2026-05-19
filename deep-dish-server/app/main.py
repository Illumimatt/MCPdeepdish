from fastapi import FastAPI

from app.routers import reservations, users

app = FastAPI(
    title="Deep-Dish API",
    description="Backend for the WhatsApp AI Restaurant Reservation Bot",
    version="1.0.0",
)

# Include the modular routers
app.include_router(users.router)
app.include_router(reservations.router)


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "deep-dish"}
