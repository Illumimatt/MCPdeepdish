import os
import traceback

import ollama
from mcp import ClientSession

# Import the Stdio Client instead of SSE for easier local integration,
# or you could configure SSE. We'll use stdio for a direct subprocess approach here,
# or you can switch to sse_client("http://127.0.0.1:3755/sse") if the server is already running.
from mcp.client.sse import sse_client
from telegram import Update
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

# Store session memory for Ollama per user
user_sessions = {}


async def process_chat(phone_number: str, user_message: str):
    if phone_number not in user_sessions:
        user_sessions[phone_number] = [
            {
                "role": "system",
                "content": "Você é um assistente de reservas de restaurante. Responda em português. Seja educado, conciso e prestativo. Use as ferramentas disponíveis para gerenciar reservas e usuários.",
            }
        ]

    user_sessions[phone_number].append({"role": "user", "content": user_message})

    # Connect to MCP Server via SSE
    async with sse_client(MCP_SERVER_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()

            # Retrieve available tools from MCP server
            mcp_tools = await session.list_tools()

            # Map MCP tools to Ollama tool format
            ollama_tools = []
            for tool in mcp_tools.tools:
                ollama_tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema,
                        },
                    }
                )

            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=user_sessions[phone_number],
                tools=ollama_tools,
                keep_alive=-1,
            )

            user_sessions[phone_number].append(response["message"])

            # Check if the model decided to call a tool
            if response["message"].get("tool_calls"):
                for tool_call in response["message"]["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    tool_args = tool_call["function"]["arguments"]

                    # Call the actual MCP tool
                    tool_response = await session.call_tool(tool_name, tool_args)

                    # Add tool response back to the session
                    user_sessions[phone_number].append(
                        {
                            "role": "tool",
                            "name": tool_name,
                            "content": str(
                                tool_response.content[0].text
                                if tool_response.content
                                else tool_response
                            ),
                        }
                    )

                # Get the final response from the model after tool execution
                final_response = ollama.chat(
                    model=OLLAMA_MODEL,
                    messages=user_sessions[phone_number],
                    tools=ollama_tools,
                )
                user_sessions[phone_number].append(final_response["message"])
                return final_response["message"]["content"]

            return response["message"]["content"]


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
        await update.message.reply_text(reply_text)
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
