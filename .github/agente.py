import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class DeepDishAgent:
    def __init__(self):
        # Caminho correto do servidor MCP
        self.server_parameters = StdioServerParameters(
            command=sys.executable,
            args=["deep-dish-server/mcp_server.py"],
            env=None
        )

    async def processar_comando(self, mensagem_usuario: str):
        print(f"[Agente] Recebido do WhatsApp: '{mensagem_usuario}'")

        # Conecta ao servidor MCP
        async with stdio_client(self.server_parameters) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as sessao:

                # Inicializa a sessão
                await sessao.initialize()

                # Lógica simples do agente
                if (
                    "reservar" in mensagem_usuario.lower()
                    or "mesa" in mensagem_usuario.lower()
                ):
                    print("[Agente] Identificado: Intenção de Reserva.")

                    resposta_mcp = await sessao.call_tool(
                        name="create_reservation",
                        arguments={
                            "phone_number": "5511999999999",
                            "date_time": "2026-05-19T20:00:00",
                            "party_size": 2
                        }
                    )

                    return f"Ação concluída! Detalhes: {resposta_mcp.content}"

                elif "cancelar" in mensagem_usuario.lower():
                    print("[Agente] Identificado: Cancelamento.")
                    return "Processando cancelamento..."

                else:
                    return "Desculpe, não entendi o pedido."


# Teste local
if __name__ == "__main__":
    agent = DeepDishAgent()

    comando_teste = "Gostaria de reservar uma mesa para duas pessoas"

    resultado = asyncio.run(
        agent.processar_comando(comando_teste)
    )

    print(resultado)