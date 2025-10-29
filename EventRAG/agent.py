"""
This script sets up an AI-powered event assistant agent using the uAgents framework that leverages
a Retrieval-Augmented Generation (RAG) system. It initializes an agent that listens for chat
messages, processes event-related queries using a knowledge graph (MeTTa) and a large language
model (LLM), and returns contextually accurate answers. The agent acknowledges incoming messages,
logs user interactions, and handles errors gracefully. The workflow involves parsing user queries,
retrieving relevant event information from the knowledge base, generating responses, and sending
formatted replies back to the sender effectively functioning as an intelligent, autonomous event
Q&A assistant.
"""

from datetime import datetime, timezone
from uuid import uuid4
import json
import os
from dotenv import load_dotenv
from uagents import Context, Model, Protocol, Agent
from hyperon import MeTTa

from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)

# Import components from separate files
from event_rag import EventRAG
from knowledge import initialize_knowledge_graph
from utils import LLM, process_query

# Load environment variables
load_dotenv()

# Initialize agent
agent = Agent(name="Event Assistant RAG", port=8005, mailbox=True, publish_agent_details=True)


class GeneralQuery(Model):
    query: str
    intent: str
    keyword: str


def create_text_chat(text: str) -> ChatMessage:
    """Create a text chat message."""
    content = [TextContent(type="text", text=text)]
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=content,
    )


# Initialize global components
metta = MeTTa()
initialize_knowledge_graph(metta)
rag = EventRAG(metta)
llm = LLM(api_key=os.getenv("ASI1_API_KEY"))

# Protocol setup
chat_proto = Protocol(spec=chat_protocol_spec)


@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages and process Fetch.ai/uAgents queries."""
    ctx.storage.set(str(ctx.session), sender)
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(timezone.utc), acknowledged_msg_id=msg.msg_id),
    )

    for item in msg.content:
        if isinstance(item, StartSessionContent):
            ctx.logger.info(f"Got a start session message from {sender}")
            continue
        elif isinstance(item, TextContent):
            user_query = item.text.strip()
            ctx.logger.info(f"Got a general event query from {sender}: {user_query}")

            try:
                # Process the query using the general assistant logic
                response = process_query(user_query, rag, llm)

                # Format the response
                if isinstance(response, dict):
                    answer_text = f"**{response.get('selected_question', user_query)}**\n\n{response.get('humanized_answer', 'I apologize, but I could not process your query.')}"
                else:
                    answer_text = str(response)

                # Send the response back
                await ctx.send(sender, create_text_chat(answer_text))

            except Exception as e:
                ctx.logger.error(f"Error processing Fetch.ai/uAgents query: {e}")
                await ctx.send(
                    sender,
                    create_text_chat(
                        "I apologize, but I encountered an error processing your. Please try again.")
                )
        else:
            ctx.logger.info(f"Got unexpected content from {sender}")


@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle chat acknowledgements."""
    ctx.logger.info(f"Got an acknowledgement from {sender} for {msg.acknowledged_msg_id}")


# Register the protocol
agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()