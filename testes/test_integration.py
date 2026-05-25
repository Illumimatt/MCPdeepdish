import pytest
import time
from mcp_server import create_user, get_user, create_reservation, get_user_reservations, cancel_reservation

@pytest.mark.integration
@pytest.mark.anyio
async def test_integracao_ciclo_vida_usuario(api_base_url):
    """
    Teste Real: Cria um usuário com dados dinâmicos na API ativa
    e valida se o MCP consegue criar e buscar o registro corretamente.
    """
    #Gera um número único baseado no carimbo de tempo atual
    # Ex: 5511999 + final do timestamp (garante que nunca se repete na mesma sessão)
    timestamp_unico = str(int(time.time()))[-6:]
    phone_teste = f"551199{timestamp_unico}"
    nome_teste = f"User Integracao {timestamp_unico}"

    #Cria o usuário de verdade usando a ferramenta do MCP
    resultado_criacao = await create_user(phone_number=phone_teste, name=nome_teste)

    #Garante que o MCP e a API conversaram e criaram com sucesso
    assert "User created successfully" in resultado_criacao

    # Validação extra: tenta buscar ele via get_user do MCP
    resultado_busca = await get_user(phone_number=phone_teste)
    assert "User found" in resultado_busca
    assert nome_teste in resultado_busca

@pytest.mark.integration
@pytest.mark.anyio
async def test_integracao_fluxo_reserva_completo(api_base_url):
    """
    Teste Real: Cria um usuário e depois agenda uma reserva para ele,
    garantindo que o relacionamento e a listagem na API funcionem.
    """
    #Dados dinâmicos para não chocar com execuções anteriores
    timestamp_unico = str(int(time.time()))[-6:]
    phone_teste = f"551198{timestamp_unico}"  # Prefixo levemente diferente
    nome_teste = f"Cliente Reserva {timestamp_unico}"
    
    data_reserva = "2026-06-15T20:00:00"
    tamanho_mesa = 4

    #O usuário precisa existir primeiro
    resultado_usuario = await create_user(phone_number=phone_teste, name=nome_teste)
    assert "User created successfully" in resultado_usuario

    #Cria a reserva real vinculada a esse usuário
    resultado_reserva = await create_reservation(
        phone_number=phone_teste,
        date_time=data_reserva,
        party_size=tamanho_mesa
    )

    #Valida se a API aceitou o agendamento
    assert "Reservation confirmed!" in resultado_reserva
    assert "ID:" in resultado_reserva

    #Lista as reservas do usuário para ver se ela aparece
    resultado_listagem = await get_user_reservations(phone_number=phone_teste)
    
    #Garante que a reserva criada está listada na resposta
    assert "Reservations:" in resultado_listagem
    assert data_reserva in resultado_listagem

    #Extrai o ID da reserva e cancela de verdade
    # O ID vem na string: "Reservation confirmed! ID: res-xxxxx"
    id_reserva = resultado_reserva.split("ID: ")[1].strip()
    resultado_cancelamento = await cancel_reservation(reservation_id=id_reserva)

    #Valida se o backend processou a exclusão/cancelamento
    assert "Reservation successfully cancelled" in resultado_cancelamento
