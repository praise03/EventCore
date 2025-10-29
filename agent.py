"""
This script defines the main event assistant agent that processes chat messages, classifies user
prompts into categories (weather, flight, hotel, currency, or generic), and routes them to the
correct handler. It uses the uAgents framework with a chat protocol for structured messaging,
calling helper functions or external APIs to fetch data like weather forecasts, hotel listings,
or exchange rates.

Generic event-related questions are forwarded to a connected EventRAG agent powered by Metta knowledge graphs.

The agent maintains session context, logs activity, handles acknowledgements, and manages responses
back to users, serving as the central coordinator for all user interactions.
"""

from datetime import datetime
from uuid import uuid4

from uagents import Agent, Context, Protocol, Model, Field
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)
from helpers import categorize_prompt, extract_flight_routes, extract_hotel_data, extract_weather_data
from currency_converter import fetch_exchange_rates
from flights import fetch_offers
from hotels import fetch_hotels_by_proximity
from weather import get_weather_forecast
import json

class CurrencyResponse(Model):
    conversion: str = Field(
        description="Currency Conversion Agent Response",
    )


def create_text_chat(text: str, end_session: bool = False) -> ChatMessage:
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent(type="end-session"))
    return ChatMessage(timestamp=datetime.utcnow(), msg_id=uuid4(), content=content)


agent = Agent()
chat_proto = Protocol(spec=chat_protocol_spec)

##Event_RAG_AGENT
event_RAG_agent = "agent1qg927dsj0llmc2e4yyr23fq5s7dwqjgg737hly75y6uu4r5dm04vwnvyced"

# test-agent://agent1qg927dsj0llmc2e4yyr23fq5s7dwqjgg737hly75y6uu4r5dm04vwnvyced

@chat_proto.on_message(ChatMessage)
async def handle_chat(ctx: Context, sender: str, msg: ChatMessage):
    if sender == event_RAG_agent:
        ctx.logger.info("Received response from EventRAG agent, forwarding to user...")
        initial_sender = ctx.storage.get(str(ctx.session))
        if not initial_sender:
            ctx.logger.error("No original user found to forward message to.")
            return

        for item in msg.content:
            if isinstance(item, TextContent):
                await ctx.send(initial_sender, create_text_chat(item.text))
        return

    # Store the sender's address in the session storage using the session ID as the key
    ctx.storage.set(str(ctx.session), sender)

    for item in msg.content:
        # Check if the content item indicates the start of a new session
        if isinstance(item, StartSessionContent):
            # Log the initiation of a new session
            ctx.logger.info(f"Got a start session message from {sender}")
            continue  # Move to the next content item

        # Check if the content item is textual
        elif isinstance(item, TextContent):
            # Log the received text message
            ctx.logger.info(f"Got 1 message from {sender}: {item.text}")

            # Store the sender's address again in the session storage (may be redundant)
            ctx.storage.set(str(ctx.session), sender)

            try:
                # function to extract and classify command from user prompt
                prompt_output = await categorize_prompt(str(item.text))
                prompt_data = json.loads(prompt_output["choices"][0]["message"]["content"])
                ctx.logger.info(json.loads(prompt_output["choices"][0]["message"]["content"])["type"])

                match prompt_data["type"]:
                    case "weather":
                        data = await get_weather_forecast(prompt_data["event"])
                        response = extract_weather_data(data, prompt_data["prompt"])["choices"][0]["message"]["content"]
                        await ctx.send(sender, create_text_chat(response))
                    case "flight":
                        try:
                            offers = await fetch_offers(prompt_data["from"], prompt_data["to"], prompt_data["date"])
                            response = extract_flight_routes(offers)["choices"][0]["message"]["content"]
                            ctx.logger.info(response)
                            await ctx.send(sender, create_text_chat(response))
                        except Exception as e:
                            await ctx.send(sender, create_text_chat("Could not find any flight with those parameters, Please cross check the State Codes and Date"))

                    case "hotel":
                        try:
                            ctx.logger.info(prompt_data["event"])
                            hotels = await fetch_hotels_by_proximity(prompt_data["event"])
                            response = extract_hotel_data(hotels)["choices"][0]["message"]["content"]
                            await ctx.send(sender, create_text_chat(response))
                        except Exception as e:
                            await ctx.send(sender, create_text_chat("I'm sorry. I can only fetch hotels at the Devconnect or Breakpoint Venues"))

                    case "currency":
                        response = fetch_exchange_rates(prompt_data["base_code"], prompt_data["target_code"], 1)
                        ctx.logger.info(response)
                        await ctx.send(sender, create_text_chat(response))

                    case "generic":
                        #EventRAG
                        await ctx.send(event_RAG_agent, create_text_chat(prompt_data["prompt"]))

                    case _:
                        await ctx.send(sender, create_text_chat("Sorry, I couldn't understand your request type."))


            except Exception as e:
                ctx.logger.error(f"Error processing message: {e}")
                await ctx.send(sender, create_text_chat(
                    "An error occurred while processing your request. Please try again later."))
        else:
            # Log any unexpected content types received
            ctx.logger.info(f"Got unexpected content from {sender}")



@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(
        f"Got an acknowledgement from {sender} for {msg.acknowledged_msg_id}"
    )


# Include protocol to your agent
agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()