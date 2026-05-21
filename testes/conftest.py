import sys
from pathlib import Path
import pytest

# Garante que a pasta 'deep-dish-server' está no caminho de busca do Python
BASE_DIR = Path(__file__).resolve().parent.parent
SERVER_DIR = BASE_DIR / "deep-dish-server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

# --- FIXTURES DE DADOS REUTILIZÁVEIS ---

@pytest.fixture
def dados_usuario_valido():
    """Retorna um dicionário padrão com dados de um usuário válido para os testes."""
    return {"phone_number": "5511999999999", "name": "Matheus"}

@pytest.fixture
def dados_reserva_valida():
    """Retorna um dicionário padrão com dados de uma reserva para os testes."""
    return {
        "id": "res-12345-uuid",
        "phone_number": "5511999999999",
        "date_time": "2026-05-19T19:30:00",
        "party_size": 4,
        "status": "confirmed"
    }