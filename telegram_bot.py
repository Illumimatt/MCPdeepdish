import asyncio
import os
import traceback
from datetime import datetime

import ollama
from mcp import ClientSession
from mcp.client.sse import sse_client
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

TELEGRAM_TOKEN = os.getenv(
    "TELEGRAM_TOKEN", "8973978548:AAFQIyjWdltFSSx3zMZJ29Q5RCJ7oEORliY"
)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:latest")

# MCP_SERVER_URL = "http://127.0.0.1:3755/mcp"
MCP_SERVER_URL = "http://127.0.0.1:3755/sse"

user_sessions = {}

_mcp_lock = asyncio.Lock()
_mcp_session: ClientSession | None = None
_mcp_tools: list[dict] | None = None
_sse_context = None


async def _get_mcp_session_and_tools():
    """Return the persistent (session, ollama-formatted tools) tuple.

    The first call establishes the SSE connection and initializes the MCP
    session. Subsequent calls reuse the same session. A lock ensures that
    concurrent requests don't race during initialization.
    """
    global _mcp_session, _mcp_tools, _sse_context

    if _mcp_session is not None:
        return _mcp_session, _mcp_tools

    async with _mcp_lock:
        # Double-check inside the lock (another waiter may have initialized it)
        if _mcp_session is not None:
            return _mcp_session, _mcp_tools

        _sse_context = sse_client(MCP_SERVER_URL)
        streams = await _sse_context.__aenter__()
        _mcp_session = ClientSession(streams[0], streams[1])
        await _mcp_session.__aenter__()
        await _mcp_session.initialize()

        mcp_tools = await _mcp_session.list_tools()
        _mcp_tools = []
        for tool in mcp_tools.tools:
            _mcp_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                }
            )

        return _mcp_session, _mcp_tools


async def process_chat(phone_number: str, user_message: str):
    if phone_number not in user_sessions:
        agora = datetime.now()
        data_hora = agora.strftime("%A, %d de %B de %Y, %H:%M")
        # Traduz dias da semana para português
        dias = {
            "Monday": "segunda-feira",
            "Tuesday": "terça-feira",
            "Wednesday": "quarta-feira",
            "Thursday": "quinta-feira",
            "Friday": "sexta-feira",
            "Saturday": "sábado",
            "Sunday": "domingo",
        }
        meses = {
            "January": "janeiro",
            "February": "fevereiro",
            "March": "março",
            "April": "abril",
            "May": "maio",
            "June": "junho",
            "July": "julho",
            "August": "agosto",
            "September": "setembro",
            "October": "outubro",
            "November": "novembro",
            "December": "dezembro",
        }
        for en, pt in {**dias, **meses}.items():
            data_hora = data_hora.replace(en, pt)

        user_sessions[phone_number] = [
            {
                "role": "system",
                "content": (
                    "Você é Bento, recepcionista do restaurante Deep-Dish. "
                    "Você é educado, direto e natural — como uma pessoa de verdade, não um robô animado.\n\n"
                    f"HOJE É {data_hora}.\n\n"
                    "REGRAS DE USO DAS FUNÇÕES:\n"
                    "- Quando o cliente pede para VER, CONSULTAR, FAZER, ALTERAR ou CANCELAR uma reserva: "
                    "CHAME a função IMEDIATAMENTE. Não diga 'deixa eu ver' ou 'vou conferir'. Apenas chame.\n"
                    "- Se o cliente pergunta 'quais são minhas reservas?', chame get_user_reservations AGORA.\n"
                    "- Se o cliente quer fazer uma reserva mas você não sabe se ele é cadastrado, "
                    "chame get_user primeiro. Se não for, chame create_user antes de create_reservation.\n"
                    "- NUNCA invente informações. Se a função retornou 'Nenhuma reserva encontrada', "
                    "diga isso de forma simples e ofereça ajuda para marcar uma nova.\n\n"
                    "REGRAS DE LINGUAGEM:\n"
                    "- Seja DIRETO. Máximo 2 ou 3 frases curtas por resposta. Nada de textos longos.\n"
                    "- NUNCA use emojis. Nunca.\n"
                    "- NUNCA faça comentários sobre os planos do cliente ('que legal', 'vai ser animado', etc). "
                    "Apenas resolva o que ele pediu.\n"
                    "- NUNCA mencione termos técnicos: 'phone_number', 'ISO 8601', 'ferramentas', 'ID', 'sistema'.\n"
                    "- NUNCA mostre o número de telefone do cliente.\n"
                    "- Ao perguntar data/horário: 'que dia e horário?' ou 'qual horário?'\n"
                    "- Ao perguntar quantas pessoas: 'quantas pessoas?'\n"
                    "- Ao pedir o nome: 'qual o seu nome?'\n\n"
                    "EXEMPLOS de como responder:\n"
                    "- Cliente: 'quero reservar para quarta, 6 pessoas'\n"
                    "  Você: 'Certo. Qual horário?'\n"
                    "- Cliente: 'quais minhas reservas?'\n"
                    "  Você: [chama get_user_reservations] 'O senhor não tem nenhuma reserva no momento. Quer fazer uma?'\n"
                    "- Cliente: 'cancelar minha reserva'\n"
                    "  Você: [chama get_user_reservations, depois cancel_reservation] 'Reserva cancelada, senhor.'\n\n"
                    f"INFO INTERNA: telefone do cliente = '{phone_number}'. "
                    "Use ao chamar funções. NUNCA mostre ao cliente."
                ),
            }
        ]

    user_sessions[phone_number].append({"role": "user", "content": user_message})

    session, ollama_tools = await _get_mcp_session_and_tools()
    ollama_client = ollama.AsyncClient()

    response = await ollama_client.chat(
        model=OLLAMA_MODEL,
        messages=user_sessions[phone_number],
        tools=ollama_tools,
    )

    while response["message"].get("tool_calls"):
        user_sessions[phone_number].append(response["message"])

        for tool_call in response["message"]["tool_calls"]:
            tool_name = tool_call["function"]["name"]
            tool_args = tool_call["function"]["arguments"]

            try:
                tool_response = await session.call_tool(tool_name, tool_args)
                tool_text = str(
                    tool_response.content[0].text
                    if tool_response.content
                    else tool_response
                )
            except Exception as e:
                tool_text = f"Error executing tool: {e}"

            user_sessions[phone_number].append(
                {
                    "role": "tool",
                    "name": tool_name,
                    "content": tool_text,
                }
            )

        response = await ollama_client.chat(
            model=OLLAMA_MODEL,
            messages=user_sessions[phone_number],
            tools=ollama_tools,
        )

    user_sessions[phone_number].append(response["message"])

    final_text = response["message"].get("content", "").strip()

    if not final_text:
        return "Entendido!"

    return final_text


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Olá! Sou o assistente de reservas do Deep-Dish. Como posso ajudar você hoje?"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Received message from {update.message.from_user.id}: {update.message.text}")
    # Use the Telegram user ID as the "phone number" equivalent for tool calls
    user_id = str(update.message.from_user.id)
    user_message = update.message.text

    await update.message.reply_chat_action(action="typing")

    try:
        reply_text = await process_chat(user_id, user_message)
        await update.message.reply_text(reply_text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        print(f"Error processing message: {e}")
        traceback.print_exc()
        await update.message.reply_text(
            "Desculpe, ocorreu um erro ao processar sua solicitação."
        )


def main() -> None:
    global TELEGRAM_TOKEN
    TELEGRAM_TOKEN = (
        input("Please enter your Telegram Bot Token: ")
        if TELEGRAM_TOKEN == "YOUR_TELEGRAM_TOKEN_HERE"
        else TELEGRAM_TOKEN
    )

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("Starting Telegram Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
