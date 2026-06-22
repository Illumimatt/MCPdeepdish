import pytest
from mcp_server import (
    cancel_reservation,
    create_reservation,
    create_user,
    get_user,
    get_user_reservations,
)

# -----------------------------------------------------------------------------
# 1. TESTES DA FERRAMENTA: create_user
# -----------------------------------------------------------------------------


@pytest.mark.anyio
async def test_create_user_sucesso(httpx_mock, dados_usuario_valido, api_base_url):
    httpx_mock.add_response(
        method="POST",
        url=f"{api_base_url}/users/",
        json=dados_usuario_valido,
        status_code=200,
    )

    resultado = await create_user(
        phone_number=dados_usuario_valido["phone_number"],
        name=dados_usuario_valido["name"],
    )

    assert "Cliente cadastrado" in resultado
    assert dados_usuario_valido["name"] in resultado


@pytest.mark.anyio
async def test_create_user_falha_ja_existente(
    httpx_mock, dados_usuario_valido, api_base_url
):
    httpx_mock.add_response(
        method="POST",
        url=f"{api_base_url}/users/",
        text="User already exists",
        status_code=400,
    )

    resultado = await create_user(
        phone_number=dados_usuario_valido["phone_number"],
        name=dados_usuario_valido["name"],
    )

    assert "Erro ao cadastrar cliente" in resultado
    assert "User already exists" in resultado


# -----------------------------------------------------------------------------
# 2. TESTES DA FERRAMENTA: get_user
# -----------------------------------------------------------------------------


@pytest.mark.anyio
async def test_get_user_sucesso(httpx_mock, dados_usuario_valido, api_base_url):
    phone = dados_usuario_valido["phone_number"]
    httpx_mock.add_response(
        method="GET",
        url=f"{api_base_url}/users/{phone}",
        json=dados_usuario_valido,
        status_code=200,
    )

    resultado = await get_user(phone_number=phone)

    assert "Cliente encontrado" in resultado
    assert dados_usuario_valido["name"] in resultado


@pytest.mark.anyio
async def test_get_user_nao_encontrado(httpx_mock, api_base_url):
    httpx_mock.add_response(
        method="GET", url=f"{api_base_url}/users/5511000000000", status_code=404
    )

    resultado = await get_user(phone_number="5511000000000")
    assert resultado == "Cliente não encontrado."


# -----------------------------------------------------------------------------
# 3. TESTES DA FERRAMENTA: create_reservation
# -----------------------------------------------------------------------------


@pytest.mark.anyio
async def test_create_reservation_sucesso(
    httpx_mock, dados_reserva_valida, api_base_url
):
    httpx_mock.add_response(
        method="POST",
        url=f"{api_base_url}/reservations/",
        json=dados_reserva_valida,
        status_code=200,
    )

    resultado = await create_reservation(
        phone_number=dados_reserva_valida["phone_number"],
        date_time=dados_reserva_valida["date_time"],
        party_size=dados_reserva_valida["party_size"],
    )

    assert "Reserva confirmada" in resultado
    assert dados_reserva_valida["id"] in resultado


@pytest.mark.anyio
async def test_create_reservation_utilizador_nao_registado(httpx_mock, api_base_url):
    httpx_mock.add_response(
        method="POST",
        url=f"{api_base_url}/reservations/",
        text="User must be registered first",
        status_code=404,
    )

    resultado = await create_reservation(
        phone_number="5511000000000", date_time="2026-05-19T19:30:00", party_size=2
    )

    assert "Erro ao fazer reserva" in resultado
    assert "User must be registered first" in resultado


# -----------------------------------------------------------------------------
# 4. TESTES DA FERRAMENTA: get_user_reservations
# -----------------------------------------------------------------------------


@pytest.mark.anyio
async def test_get_user_reservations_com_sucesso(
    httpx_mock, dados_reserva_valida, api_base_url
):
    phone = dados_reserva_valida["phone_number"]
    httpx_mock.add_response(
        method="GET",
        url=f"{api_base_url}/reservations/{phone}",
        json=[dados_reserva_valida],
        status_code=200,
    )

    resultado = await get_user_reservations(phone_number=phone)

    assert "Reservas:" in resultado
    assert dados_reserva_valida["id"] in resultado


@pytest.mark.anyio
async def test_get_user_reservations_vazia(
    httpx_mock, dados_usuario_valido, api_base_url
):
    phone = dados_usuario_valido["phone_number"]
    httpx_mock.add_response(
        method="GET",
        url=f"{api_base_url}/reservations/{phone}",
        json=[],
        status_code=200,
    )

    resultado = await get_user_reservations(phone_number=phone)
    assert resultado == "Nenhuma reserva encontrada."


@pytest.mark.anyio
async def test_get_user_reservations_falha(
    httpx_mock, dados_usuario_valido, api_base_url
):
    phone = dados_usuario_valido["phone_number"]
    httpx_mock.add_response(
        method="GET",
        url=f"{api_base_url}/reservations/{phone}",
        text="Internal Server Error",
        status_code=500,
    )

    resultado = await get_user_reservations(phone_number=phone)
    assert "Erro ao consultar reservas" in resultado


# -----------------------------------------------------------------------------
# 5. TESTES DA FERRAMENTA: cancel_reservation
# -----------------------------------------------------------------------------


@pytest.mark.anyio
async def test_cancel_reservation_sucesso(httpx_mock, api_base_url):
    httpx_mock.add_response(
        method="DELETE", url=f"{api_base_url}/reservations/res-123", status_code=200
    )

    resultado = await cancel_reservation(reservation_id="res-123")
    assert resultado == "Reserva cancelada com sucesso."


@pytest.mark.anyio
async def test_cancel_reservation_nao_encontrada(httpx_mock, api_base_url):
    httpx_mock.add_response(
        method="DELETE",
        url=f"{api_base_url}/reservations/res-invalido",
        text="Reservation not found",
        status_code=404,
    )

    resultado = await cancel_reservation(reservation_id="res-invalido")

    assert "Erro ao cancelar reserva" in resultado
    assert "Reservation not found" in resultado
