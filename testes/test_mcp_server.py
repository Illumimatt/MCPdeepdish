import pytest
from mcp_server import create_user, get_user, create_reservation, get_user_reservations, cancel_reservation

# -----------------------------------------------------------------------------
# 1. TESTES DA FERRAMENTA: create_user
# -----------------------------------------------------------------------------

@pytest.mark.anyio
async def test_create_user_sucesso(httpx_mock, dados_usuario_valido):
    httpx_mock.add_response(
        method="POST",
        url="http://127.0.0.1:8000/users/",
        json=dados_usuario_valido,  # Usando a fixture aqui
        status_code=200
    )

    resultado = await create_user(
        phone_number=dados_usuario_valido["phone_number"], 
        name=dados_usuario_valido["name"]
    )

    assert "User created successfully" in resultado
    assert dados_usuario_valido["name"] in resultado


@pytest.mark.anyio
async def test_create_user_falha_ja_existente(httpx_mock, dados_usuario_valido):
    httpx_mock.add_response(
        method="POST",
        url="http://127.0.0.1:8000/users/",
        text="User already exists",
        status_code=400
    )

    resultado = await create_user(
        phone_number=dados_usuario_valido["phone_number"], 
        name=dados_usuario_valido["name"]
    )

    assert "Failed to create user" in resultado
    assert "User already exists" in resultado


# -----------------------------------------------------------------------------
# 2. TESTES DA FERRAMENTA: get_user
# -----------------------------------------------------------------------------

@pytest.mark.anyio
async def test_get_user_sucesso(httpx_mock, dados_usuario_valido):
    phone = dados_usuario_valido["phone_number"]
    httpx_mock.add_response(
        method="GET",
        url=f"http://127.0.0.1:8000/users/{phone}",
        json=dados_usuario_valido,
        status_code=200
    )

    resultado = await get_user(phone_number=phone)

    assert "User found" in resultado
    assert dados_usuario_valido["name"] in resultado


@pytest.mark.anyio
async def test_get_user_nao_encontrado(httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="http://127.0.0.1:8000/users/5511000000000",
        status_code=404
    )

    resultado = await get_user(phone_number="5511000000000")
    assert resultado == "User not found."


# -----------------------------------------------------------------------------
# 3. TESTES DA FERRAMENTA: create_reservation
# -----------------------------------------------------------------------------

@pytest.mark.anyio
async def test_create_reservation_sucesso(httpx_mock, dados_reserva_valida):
    httpx_mock.add_response(
        method="POST",
        url="http://127.0.0.1:8000/reservations/",
        json=dados_reserva_valida,
        status_code=200
    )

    resultado = await create_reservation(
        phone_number=dados_reserva_valida["phone_number"],
        date_time=dados_reserva_valida["date_time"],
        party_size=dados_reserva_valida["party_size"]
    )

    assert "Reservation confirmed!" in resultado
    assert f"ID: {dados_reserva_valida['id']}" in resultado


@pytest.mark.anyio
async def test_create_reservation_utilizador_nao_registado(httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="http://127.0.0.1:8000/reservations/",
        text="User must be registered first",
        status_code=404
    )

    resultado = await create_reservation(
        phone_number="5511000000000",
        date_time="2026-05-19T19:30:00",
        party_size=2
    )

    assert "Failed to book reservation" in resultado
    assert "User must be registered first" in resultado


# -----------------------------------------------------------------------------
# 4. TESTES DA FERRAMENTA: get_user_reservations
# -----------------------------------------------------------------------------

@pytest.mark.anyio
async def test_get_user_reservations_com_sucesso(httpx_mock, dados_reserva_valida):
    phone = dados_reserva_valida["phone_number"]
    httpx_mock.add_response(
        method="GET",
        url=f"http://127.0.0.1:8000/reservations/{phone}",
        json=[dados_reserva_valida],
        status_code=200
    )

    resultado = await get_user_reservations(phone_number=phone)

    assert "Reservations:" in resultado
    assert dados_reserva_valida["id"] in resultado


@pytest.mark.anyio
async def test_get_user_reservations_vazia(httpx_mock, dados_usuario_valido):
    phone = dados_usuario_valido["phone_number"]
    httpx_mock.add_response(
        method="GET",
        url=f"http://127.0.0.1:8000/reservations/{phone}",
        json=[],
        status_code=200
    )

    resultado = await get_user_reservations(phone_number=phone)
    assert resultado == "No reservations found for this user."


@pytest.mark.anyio
async def test_get_user_reservations_falha(httpx_mock, dados_usuario_valido):
    phone = dados_usuario_valido["phone_number"]
    httpx_mock.add_response(
        method="GET",
        url=f"http://127.0.0.1:8000/reservations/{phone}",
        text="Internal Server Error",
        status_code=500
    )

    resultado = await get_user_reservations(phone_number=phone)
    assert "Failed to fetch reservations" in resultado


# -----------------------------------------------------------------------------
# 5. TESTES DA FERRAMENTA: cancel_reservation
# -----------------------------------------------------------------------------

@pytest.mark.anyio
async def test_cancel_reservation_sucesso(httpx_mock):
    httpx_mock.add_response(
        method="DELETE",
        url="http://127.0.0.1:8000/reservations/res-123",
        status_code=200
    )

    resultado = await cancel_reservation(reservation_id="res-123")
    assert resultado == "Reservation successfully cancelled."


@pytest.mark.anyio
async def test_cancel_reservation_nao_encontrada(httpx_mock):
    httpx_mock.add_response(
        method="DELETE",
        url="http://127.0.0.1:8000/reservations/res-invalido",
        text="Reservation not found",
        status_code=404
    )

    resultado = await cancel_reservation(reservation_id="res-invalido")

    assert "Failed to cancel reservation" in resultado
    assert "Reservation not found" in resultado