import os

import httpx
from fastmcp import FastMCP

mcp = FastMCP("DeepDish Reservations")

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# Reusable httpx client with connection pooling and keep-alive.
# Creating a new client per tool call was adding per-request TCP overhead.
_http_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
        )
    return _http_client


def reset_http_client_for_testing() -> None:
    """Discard the cached httpx client so pytest-httpx mocks can intercept.

    Call this in a test fixture (e.g. autouse) so every test function gets
    a fresh client that picks up the active HTTPXMock transport.
    """
    global _http_client
    if _http_client is not None:
        try:
            import asyncio

            asyncio.get_event_loop()
            asyncio.ensure_future(_http_client.aclose())
        except RuntimeError:
            pass
    _http_client = None


@mcp.tool
async def create_user(phone_number: str, name: str) -> str:
    """
    Cadastrar um novo cliente no restaurante.
    Sempre chame esta função ANTES de fazer uma reserva para um cliente novo.
    Pergunte o nome do cliente de forma educada antes de chamar esta função.
    """
    client = _get_client()
    response = await client.post(
        f"{API_BASE_URL}/users/", json={"phone_number": phone_number, "name": name}
    )
    if response.status_code == 200:
        data = response.json()
        return f"Cliente cadastrado: {data}"
    return f"Erro ao cadastrar cliente: {response.text}"


@mcp.tool
async def get_user(phone_number: str) -> str:
    """Consultar se um cliente já está cadastrado no restaurante."""
    client = _get_client()
    response = await client.get(f"{API_BASE_URL}/users/{phone_number}")
    if response.status_code == 200:
        return f"Cliente encontrado: {response.json()}"
    return "Cliente não encontrado."


@mcp.tool
async def create_reservation(phone_number: str, date_time: str, party_size: int) -> str:
    """
    Fazer uma nova reserva no restaurante.
    date_time deve ser a data e horário no formato ISO 8601 (ex: 2026-06-21T20:00:00).
    party_size é o número de pessoas.
    NUNCA mostre o formato ISO 8601 para o cliente. Apenas converta a data que ele disser.
    """
    client = _get_client()
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
        return f"Reserva confirmada: {res_data}"
    return f"Erro ao fazer reserva: {response.text}"


@mcp.tool
async def get_user_reservations(phone_number: str) -> str:
    """Consultar todas as reservas de um cliente."""
    client = _get_client()
    response = await client.get(f"{API_BASE_URL}/reservations/{phone_number}")
    if response.status_code == 200:
        reservations = response.json()
        if not reservations:
            return "Nenhuma reserva encontrada."
        return f"Reservas: {reservations}"
    return f"Erro ao consultar reservas: {response.text}"


@mcp.tool
async def update_reservation(
    reservation_id: str, date_time: str | None = None, party_size: int | None = None
) -> str:
    """
    Alterar uma reserva existente (data/horário ou número de pessoas).
    Use o reservation_id da reserva que o cliente quer modificar.
    """
    payload = {}
    if date_time is not None:
        payload["date_time"] = date_time
    if party_size is not None:
        payload["party_size"] = party_size

    if not payload:
        return "Nenhuma alteração solicitada."

    client = _get_client()
    response = await client.patch(
        f"{API_BASE_URL}/reservations/{reservation_id}",
        json=payload,
    )
    if response.status_code == 200:
        res_data = response.json()
        return f"Reserva alterada: {res_data}"
    return f"Erro ao alterar reserva: {response.text}"


@mcp.tool
async def cancel_reservation(reservation_id: str) -> str:
    """Cancelar uma reserva usando o número de identificação dela."""
    client = _get_client()
    response = await client.delete(f"{API_BASE_URL}/reservations/{reservation_id}")
    if response.status_code == 200:
        return "Reserva cancelada com sucesso."
    return f"Erro ao cancelar reserva: {response.text}"


if __name__ == "__main__":
    # Start the FastMCP server with stdio transport (the standard for MCP tools)
    mcp.run()
