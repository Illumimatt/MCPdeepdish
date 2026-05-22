import pytest
import time
from mcp_server import create_user, get_user, create_reservation, get_user_reservations

@pytest.mark.integration
@pytest.mark.anyio
async def test_integracao_ciclo_vida_usuario():
    """
    Teste Real: Cria um usuário com dados dinâmicos na API ativa
    e valida se o MCP consegue criar e buscar o registro corretamente.
    """
    # 1. ARRANGE: Gera um número único baseado no carimbo de tempo atual
    # Ex: 5511999 + final do timestamp (garante que nunca se repete na mesma sessão)
    timestamp_unico = str(int(time.time()))[-6:]
    phone_teste = f"551199{timestamp_unico}"
    nome_teste = f"User Integracao {timestamp_unico}"

    # 2. ACT: Cria o usuário de verdade usando a ferramenta do MCP
    resultado_criacao = await create_user(phone_number=phone_teste, name=nome_teste)

    # 3. ASSERT: Garante que o MCP e a API conversaram e criaram com sucesso
    assert "User created successfully" in resultado_criacao

    # Validação extra: tenta buscar ele via get_user do MCP
    resultado_busca = await get_user(phone_number=phone_teste)
    assert "User found" in resultado_busca
    assert nome_teste in resultado_busca

@pytest.mark.integration
@pytest.mark.anyio
async def test_integracao_fluxo_reserva_completo():
    """
    Teste Real: Cria um usuário e depois agenda uma reserva para ele,
    garantindo que o relacionamento e a listagem na API funcionem.
    """
    # 1. ARRANGE: Dados dinâmicos para não chocar com execuções anteriores
    timestamp_unico = str(int(time.time()))[-6:]
    phone_teste = f"551198{timestamp_unico}"  # Prefixo levemente diferente
    nome_teste = f"Cliente Reserva {timestamp_unico}"
    
    data_reserva = "2026-06-15T20:00:00"
    tamanho_mesa = 4

    # 2. ACT & ASSERT PASSO 1: O usuário precisa existir primeiro
    resultado_usuario = await create_user(phone_number=phone_teste, name=nome_teste)
    assert "User created successfully" in resultado_usuario

    # 3. ACT PASSO 2: Cria a reserva real vinculada a esse usuário
    resultado_reserva = await create_reservation(
        phone_number=phone_teste,
        date_time=data_reserva,
        party_size=tamanho_mesa
    )

    # ASSERT PASSO 2: Valida se a API aceitou o agendamento
    assert "Reservation confirmed!" in resultado_reserva
    assert "ID:" in resultado_reserva

    # 4. ACT PASSO 3: Lista as reservas do usuário para ver se ela aparece
    resultado_listagem = await get_user_reservations(phone_number=phone_teste)
    
    # ASSERT PASSO 3: Garante que a reserva criada está listada na resposta
    assert "Reservations:" in resultado_listagem
    assert data_reserva in resultado_listagem