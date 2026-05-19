import httpx
from fastmcp import FastMCP

mcp = FastMCP("DeepDish Reservations")

API_BASE_URL = "http://127.0.0.1:8000"


@mcp.tool
async def create_user(phone_number: str, name: str) -> str:
    """
    Register a new user in the restaurant system.
    Must be called before booking a reservation for a new user.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/users/", json={"phone_number": phone_number, "name": name}
        )
        if response.status_code == 200:
            return f"User created successfully: {response.json()}"
        return f"Failed to create user: {response.text}"


@mcp.tool
async def get_user(phone_number: str) -> str:
    """Retrieve user details by their WhatsApp phone number."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/users/{phone_number}")
        if response.status_code == 200:
            return f"User found: {response.json()}"
        return "User not found."


@mcp.tool
async def create_reservation(phone_number: str, date_time: str, party_size: int) -> str:
    """
    Create a new restaurant reservation.
    date_time should be provided in ISO 8601 format (e.g., 2026-05-19T19:30:00).
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/reservations/",
            json={
                "phone_number": phone_number,
                "date_time": date_time,
                "party_size": party_size,
            },
        )
        if response.status_code == 200:
            res_data = response.json()
            return f"Reservation confirmed! ID: {res_data['id']}"
        return f"Failed to book reservation: {response.text}"


@mcp.tool
async def get_user_reservations(phone_number: str) -> str:
    """Get a list of all reservations for a specific user using their phone number."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/reservations/{phone_number}")
        if response.status_code == 200:
            reservations = response.json()
            if not reservations:
                return "No reservations found for this user."
            return f"Reservations: {reservations}"
        return f"Failed to fetch reservations: {response.text}"


@mcp.tool
async def cancel_reservation(reservation_id: str) -> str:
    """Cancel an existing reservation using its unique reservation ID."""
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{API_BASE_URL}/reservations/{reservation_id}")
        if response.status_code == 200:
            return "Reservation successfully cancelled."
        return f"Failed to cancel reservation: {response.text}"


if __name__ == "__main__":
    # Start the FastMCP server with stdio transport (the standard for MCP tools)
    mcp.run()
