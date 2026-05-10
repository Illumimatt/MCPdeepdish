from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4

from fastmcp import FastMCP

mcp = FastMCP("deep-dish-mcp")


class PapelUsuario(str, Enum):
    CLIENTE = "cliente"
    RESTAURANTE = "restaurante"
    ADMINISTRADOR = "administrador"


class StatusFila(str, Enum):
    AGUARDANDO = "aguardando"
    PRONTO = "pronto"
    SENTADO = "sentado"
    CANCELADO = "cancelado"
    FALTOU = "faltou"


class StatusReserva(str, Enum):
    PENDENTE = "pendente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    FINALIZADA = "finalizada"
    FALTOU = "faltou"


class StatusMesa(str, Enum):
    LIVRE = "livre"
    OCUPADA = "ocupada"
    DESATIVADA = "desativada"


@dataclass
class Usuario:
    id: str
    nome: str
    email: str
    senha: str
    papel: PapelUsuario
    criado_em: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Restaurante:
    id: str
    id_proprietario: str
    nome: str
    localizacao: str
    tipo_cozinha: str
    capacidade: int
    horario_abertura: str
    horario_fechamento: str
    ativo: bool = True


@dataclass
class EntradaFila:
    id: str
    id_restaurante: str
    id_usuario: str
    quantidade_pessoas: int
    status: StatusFila
    criado_em: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Reserva:
    id: str
    id_restaurante: str
    id_usuario: str
    quantidade_pessoas: int
    horario_reserva: datetime
    status: StatusReserva
    id_mesa: Optional[str] = None


@dataclass
class Mesa:
    id: str
    id_restaurante: str
    numero: int
    capacidade: int
    status: StatusMesa


usuarios_banco: Dict[str, Usuario] = {}
restaurantes_banco: Dict[str, Restaurante] = {}
fila_banco: Dict[str, EntradaFila] = {}
reservas_banco: Dict[str, Reserva] = {}
mesas_banco: Dict[str, Mesa] = {}


@mcp.tool()
def registrar_usuario(nome: str, email: str, senha: str, papel: str) -> dict:
    """
    Registra um novo usuário no sistema.

    Args:
        nome: Nome completo do usuário.
        email: E-mail do usuário.
        senha: Senha do usuário.
        papel: Papel do usuário no sistema.

    Returns:
        Dados básicos do usuário criado.
    """

    for usuario in usuarios_banco.values():
        if usuario.email == email:
            raise ValueError("E-mail já cadastrado")

    usuario = Usuario(
        id=str(uuid4()),
        nome=nome,
        email=email,
        senha=senha,
        papel=PapelUsuario(papel),
    )

    usuarios_banco[usuario.id] = usuario

    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "papel": usuario.papel.value,
    }


@mcp.tool()
def autenticar_usuario(email: str, senha: str) -> dict:
    """
    Autentica um usuário existente.

    Args:
        email: E-mail cadastrado.
        senha: Senha informada.

    Returns:
        Dados de autenticação simulados.
    """

    for usuario in usuarios_banco.values():
        if usuario.email == email and usuario.senha == senha:
            return {
                "token": f"mock-jwt-{usuario.id}",
                "id_usuario": usuario.id,
                "papel": usuario.papel.value,
            }

    raise ValueError("Credenciais inválidas")


@mcp.tool()
def criar_restaurante(
    id_proprietario: str,
    nome: str,
    localizacao: str,
    tipo_cozinha: str,
    capacidade: int,
    horario_abertura: str,
    horario_fechamento: str,
) -> dict:
    """
    Cria um restaurante no sistema.

    Args:
        id_proprietario: Identificador do proprietário.
        nome: Nome do restaurante.
        localizacao: Localização do restaurante.
        tipo_cozinha: Tipo de cozinha.
        capacidade: Capacidade máxima.
        horario_abertura: Horário de abertura.
        horario_fechamento: Horário de fechamento.

    Returns:
        Dados do restaurante criado.
    """

    restaurante = Restaurante(
        id=str(uuid4()),
        id_proprietario=id_proprietario,
        nome=nome,
        localizacao=localizacao,
        tipo_cozinha=tipo_cozinha,
        capacidade=capacidade,
        horario_abertura=horario_abertura,
        horario_fechamento=horario_fechamento,
    )

    restaurantes_banco[restaurante.id] = restaurante

    return {
        "id": restaurante.id,
        "id_proprietario": restaurante.id_proprietario,
        "nome": restaurante.nome,
        "localizacao": restaurante.localizacao,
        "tipo_cozinha": restaurante.tipo_cozinha,
        "capacidade": restaurante.capacidade,
        "horario_abertura": restaurante.horario_abertura,
        "horario_fechamento": restaurante.horario_fechamento,
        "ativo": restaurante.ativo,
    }


@mcp.tool()
def buscar_restaurantes(consulta: str) -> List[dict]:
    """
    Busca restaurantes por nome ou localização.

    Args:
        consulta: Termo de busca.

    Returns:
        Lista de restaurantes encontrados.
    """

    resultados = []

    for restaurante in restaurantes_banco.values():
        if consulta.lower() in restaurante.nome.lower() or consulta.lower() in restaurante.localizacao.lower():
            resultados.append(
                {
                    "id": restaurante.id,
                    "nome": restaurante.nome,
                    "localizacao": restaurante.localizacao,
                    "tipo_cozinha": restaurante.tipo_cozinha,
                    "capacidade": restaurante.capacidade,
                    "ativo": restaurante.ativo,
                }
            )

    return resultados


@mcp.tool()
def obter_detalhes_restaurante(id_restaurante: str) -> dict:
    """
    Retorna os detalhes de um restaurante.

    Args:
        id_restaurante: Identificador do restaurante.

    Returns:
        Dados completos do restaurante.
    """

    restaurante = restaurantes_banco.get(id_restaurante)

    if not restaurante:
        raise ValueError("Restaurante não encontrado")

    return {
        "id": restaurante.id,
        "id_proprietario": restaurante.id_proprietario,
        "nome": restaurante.nome,
        "localizacao": restaurante.localizacao,
        "tipo_cozinha": restaurante.tipo_cozinha,
        "capacidade": restaurante.capacidade,
        "horario_abertura": restaurante.horario_abertura,
        "horario_fechamento": restaurante.horario_fechamento,
        "ativo": restaurante.ativo,
    }


@mcp.tool()
def criar_entrada_fila(id_restaurante: str, id_usuario: str, quantidade_pessoas: int) -> dict:
    """
    Adiciona um cliente à fila do restaurante.

    Args:
        id_restaurante: Identificador do restaurante.
        id_usuario: Identificador do usuário.
        quantidade_pessoas: Quantidade de pessoas no grupo.

    Returns:
        Dados da entrada na fila.
    """

    entrada = EntradaFila(
        id=str(uuid4()),
        id_restaurante=id_restaurante,
        id_usuario=id_usuario,
        quantidade_pessoas=quantidade_pessoas,
        status=StatusFila.AGUARDANDO,
    )

    fila_banco[entrada.id] = entrada

    return {
        "id_fila": entrada.id,
        "posicao": calcular_posicao_fila(entrada.id),
        "status": entrada.status.value,
    }


@mcp.tool()
def calcular_posicao_fila(id_fila: str) -> int:
    """
    Calcula a posição atual de uma entrada na fila.

    Args:
        id_fila: Identificador da entrada na fila.

    Returns:
        Posição numérica na fila.
    """

    entrada_fila = fila_banco.get(id_fila)

    if not entrada_fila:
        raise ValueError("Entrada da fila não encontrada")

    entradas = [
        entrada
        for entrada in fila_banco.values()
        if entrada.id_restaurante == entrada_fila.id_restaurante and entrada.status == StatusFila.AGUARDANDO
    ]

    entradas.sort(key=lambda entrada: entrada.criado_em)

    for indice, entrada in enumerate(entradas, start=1):
        if entrada.id == id_fila:
            return indice

    return -1


@mcp.tool()
def obter_status_fila(id_fila: str) -> dict:
    """
    Retorna o status e a posição de uma entrada na fila.

    Args:
        id_fila: Identificador da entrada na fila.

    Returns:
        Dados atuais da fila.
    """

    entrada = fila_banco.get(id_fila)

    if not entrada:
        raise ValueError("Entrada da fila não encontrada")

    return {
        "id_fila": entrada.id,
        "status": entrada.status.value,
        "posicao": calcular_posicao_fila(id_fila),
    }


@mcp.tool()
def atualizar_status_fila(id_fila: str, status: str) -> dict:
    """
    Atualiza o status de uma entrada na fila.

    Args:
        id_fila: Identificador da entrada na fila.
        status: Novo status da fila.

    Returns:
        Dados atualizados da fila.
    """

    entrada = fila_banco.get(id_fila)

    if not entrada:
        raise ValueError("Entrada da fila não encontrada")

    entrada.status = StatusFila(status)

    return {
        "id_fila": entrada.id,
        "status": entrada.status.value,
    }


@mcp.tool()
def criar_reserva(
    id_restaurante: str,
    id_usuario: str,
    quantidade_pessoas: int,
    horario_reserva: str,
) -> dict:
    """
    Cria uma reserva futura no sistema.

    Args:
        id_restaurante: Identificador do restaurante.
        id_usuario: Identificador do usuário.
        quantidade_pessoas: Quantidade de pessoas.
        horario_reserva: Data e hora da reserva em ISO 8601.

    Returns:
        Dados da reserva criada.
    """

    reserva = Reserva(
        id=str(uuid4()),
        id_restaurante=id_restaurante,
        id_usuario=id_usuario,
        quantidade_pessoas=quantidade_pessoas,
        horario_reserva=datetime.fromisoformat(horario_reserva),
        status=StatusReserva.PENDENTE,
    )

    reservas_banco[reserva.id] = reserva

    return {
        "id": reserva.id,
        "id_restaurante": reserva.id_restaurante,
        "id_usuario": reserva.id_usuario,
        "quantidade_pessoas": reserva.quantidade_pessoas,
        "horario_reserva": reserva.horario_reserva.isoformat(),
        "status": reserva.status.value,
        "id_mesa": reserva.id_mesa,
    }


@mcp.tool()
def confirmar_reserva(id_reserva: str) -> dict:
    """
    Confirma uma reserva existente.

    Args:
        id_reserva: Identificador da reserva.

    Returns:
        Dados atualizados da reserva.
    """

    reserva = reservas_banco.get(id_reserva)

    if not reserva:
        raise ValueError("Reserva não encontrada")

    reserva.status = StatusReserva.CONFIRMADA

    return {
        "id": reserva.id,
        "status": reserva.status.value,
        "id_mesa": reserva.id_mesa,
    }


@mcp.tool()
def cancelar_reserva(id_reserva: str) -> dict:
    """
    Cancela uma reserva existente.

    Args:
        id_reserva: Identificador da reserva.

    Returns:
        Dados atualizados da reserva.
    """

    reserva = reservas_banco.get(id_reserva)

    if not reserva:
        raise ValueError("Reserva não encontrada")

    reserva.status = StatusReserva.CANCELADA

    return {
        "id": reserva.id,
        "status": reserva.status.value,
    }


@mcp.tool()
def criar_mesa(id_restaurante: str, numero: int, capacidade: int) -> dict:
    """
    Cria uma mesa vinculada ao restaurante.

    Args:
        id_restaurante: Identificador do restaurante.
        numero: Número da mesa.
        capacidade: Capacidade da mesa.

    Returns:
        Dados da mesa criada.
    """

    mesa = Mesa(
        id=str(uuid4()),
        id_restaurante=id_restaurante,
        numero=numero,
        capacidade=capacidade,
        status=StatusMesa.LIVRE,
    )

    mesas_banco[mesa.id] = mesa

    return {
        "id": mesa.id,
        "id_restaurante": mesa.id_restaurante,
        "numero": mesa.numero,
        "capacidade": mesa.capacidade,
        "status": mesa.status.value,
    }


@mcp.tool()
def listar_mesas_livres(id_restaurante: str) -> List[dict]:
    """
    Lista as mesas livres de um restaurante.

    Args:
        id_restaurante: Identificador do restaurante.

    Returns:
        Lista de mesas livres.
    """

    return [
        {
            "id": mesa.id,
            "id_restaurante": mesa.id_restaurante,
            "numero": mesa.numero,
            "capacidade": mesa.capacidade,
            "status": mesa.status.value,
        }
        for mesa in mesas_banco.values()
        if mesa.id_restaurante == id_restaurante and mesa.status == StatusMesa.LIVRE
    ]


@mcp.tool()
def associar_mesa_reserva(id_reserva: str, id_mesa: str) -> dict:
    """
    Associa uma mesa a uma reserva.

    Args:
        id_reserva: Identificador da reserva.
        id_mesa: Identificador da mesa.

    Returns:
        Dados da reserva atualizada.
    """

    reserva = reservas_banco.get(id_reserva)
    mesa = mesas_banco.get(id_mesa)

    if not reserva:
        raise ValueError("Reserva não encontrada")

    if not mesa:
        raise ValueError("Mesa não encontrada")

    if mesa.status != StatusMesa.LIVRE:
        raise ValueError("Mesa indisponível")

    reserva.id_mesa = mesa.id
    mesa.status = StatusMesa.OCUPADA

    return {
        "id": reserva.id,
        "id_mesa": reserva.id_mesa,
        "status": reserva.status.value,
    }


@mcp.tool()
def liberar_mesa(id_mesa: str) -> dict:
    """
    Libera uma mesa ocupada.

    Args:
        id_mesa: Identificador da mesa.

    Returns:
        Dados atualizados da mesa.
    """

    mesa = mesas_banco.get(id_mesa)

    if not mesa:
        raise ValueError("Mesa não encontrada")

    mesa.status = StatusMesa.LIVRE

    return {
        "id": mesa.id,
        "status": mesa.status.value,
    }


@mcp.tool()
def obter_painel_restaurante(id_restaurante: str) -> dict:
    """
    Retorna um resumo operacional do restaurante.

    Args:
        id_restaurante: Identificador do restaurante.

    Returns:
        Métricas principais de operação.
    """

    fila_aguardando = len(
        [
            entrada
            for entrada in fila_banco.values()
            if entrada.id_restaurante == id_restaurante and entrada.status == StatusFila.AGUARDANDO
        ]
    )

    reservas_confirmadas = len(
        [
            reserva
            for reserva in reservas_banco.values()
            if reserva.id_restaurante == id_restaurante and reserva.status == StatusReserva.CONFIRMADA
        ]
    )

    mesas_ocupadas = len(
        [
            mesa
            for mesa in mesas_banco.values()
            if mesa.id_restaurante == id_restaurante and mesa.status == StatusMesa.OCUPADA
        ]
    )

    return {
        "fila_aguardando": fila_aguardando,
        "reservas_confirmadas": reservas_confirmadas,
        "mesas_ocupadas": mesas_ocupadas,
    }


@mcp.tool()
def notificar_usuario(id_usuario: str, mensagem: str) -> dict:
    """
    Envia uma notificação simulada para o usuário.

    Args:
        id_usuario: Identificador do usuário.
        mensagem: Mensagem da notificação.

    Returns:
        Dados da notificação enviada.
    """

    if id_usuario not in usuarios_banco:
        raise ValueError("Usuário não encontrado")

    return {
        "id_usuario": id_usuario,
        "mensagem": mensagem,
        "enviado_em": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    mcp.run()
