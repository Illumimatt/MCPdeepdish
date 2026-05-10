# Deep Dish MCP Server

Servidor MCP (Model Context Protocol) desenvolvido em Python utilizando a biblioteca FastMCP para integração com o sistema Deep Dish.

O projeto expõe ferramentas MCP relacionadas à operação de restaurantes, filas digitais, reservas, mesas e gerenciamento operacional.

---

# Tecnologias

- Python 3.11+
- FastMCP
- Dataclasses
- Type Hints
- MCP (Model Context Protocol)

---

# Funcionalidades

## Autenticação

- Registrar usuário
- Autenticar usuário

## Restaurantes

- Criar restaurante
- Buscar restaurantes
- Obter detalhes do restaurante

## Fila Digital

- Criar entrada na fila
- Calcular posição da fila
- Obter status da fila
- Atualizar status da fila

## Reservas

- Criar reserva
- Confirmar reserva
- Cancelar reserva

## Mesas

- Criar mesa
- Listar mesas livres
- Associar mesa à reserva
- Liberar mesa

## Painel Operacional

- Obter métricas do restaurante

## Notificações

- Notificar usuário

---

# Estrutura do Projeto

```text
.
├── deep_dish_mcp_server_final.py
├── README.md
└── requirements.txt
```

---


# Exemplo de Ferramenta MCP

```python
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
```

---

# Objetivo do Projeto

O objetivo deste projeto é disponibilizar um servidor MCP para integração de agentes de IA com o sistema Deep Dish, permitindo automação e acesso estruturado às funcionalidades do restaurante.

---


# Repositório Base

Projeto original Deep Dish:

- https://github.com/eduspv/deep-dish

Backend utilizado como referência:

- https://github.com/eduspv/deep-dish/tree/main/deep-dish-backend

---

# Licença

Projeto acadêmico e educacional.
