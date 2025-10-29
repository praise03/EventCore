# utils.py
"""
utils.py provides the core query processing pipeline for the Event Assistant,
integrating MeTTa-based knowledge retrieval (via EventRAG) with ASI:One LLM for intent classification,
data formatting, and humanized response generation. It handles all event-related intents (dates, tickets, venue, logistics, side events, etc.),
ensures strict adherence to knowledge base facts, bypasses LLM for long lists like side events to prevent truncation,
and includes fallback learning for new FAQs. All responses are structured with 'Selected Question' and 'Humanized Answer'
for consistent agent output.
"""

import json
from openai import OpenAI
from event_rag import EventRAG


class LLM:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key, base_url="https://api.asi1.ai/v1")

    def create_completion(self, prompt: str, max_tokens: int = 300) -> str:
        try:
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="asi1-mini",
                max_tokens=max_tokens,
                temperature=0.3
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLM Error: {e}")
            return "Sorry, I couldn't respond right now."


def get_intent_and_keyword(query: str, llm: LLM) -> tuple[str, str]:
    prompt = f"""
You are an expert for Devconnect (Buenos Aires) and Breakpoint (Abu Dhabi).

Classify intent from: dates, venue, ticket, logistics, side_event, speakers, program, faq, unknown
Keyword: "devconnect" (La Rural, Buenos Aires), "breakpoint" (Etihad, Abu Dhabi)

Query: "{query}"

Return ONLY JSON:
{{"intent": "<intent>", "keyword": "<keyword>"}}
"""
    response = llm.create_completion(prompt, max_tokens=100)
    try:
        result = json.loads(response)
        return result.get("intent", "unknown"), result.get("keyword", "")
    except:
        return "unknown", ""


def generate_knowledge_response(query: str, intent: str, keyword: str, llm: LLM) -> str:
    prompt = f"Query: '{query}'\nAnswer in 1 short sentence about {keyword}. Be factual."
    return llm.create_completion(prompt, max_tokens=80)


def process_query(query: str, rag: EventRAG, llm: LLM) -> dict:
    intent, keyword = get_intent_and_keyword(query, llm)
    print(f"[Intent] {intent} | [Keyword] {keyword}")

    data = ""

    # ————————————————————
    # 1. DATES
    # ————————————————————
    if intent == "dates" and keyword:
        result = rag.query("date_range", keyword)
        data = result[0] if result else "Dates not announced."

    # ————————————————————
    # 2. VENUE
    # ————————————————————
    elif intent == "venue" and keyword:
        venue = rag.query("venue", keyword)[0] if rag.query("venue", keyword) else "TBD"
        city = rag.query("venue_city", keyword)[0] if rag.query("venue_city", keyword) else ""
        country = rag.query("venue_country", keyword)[0] if rag.query("venue_country", keyword) else ""
        address = rag.query("venue_address", keyword)[0] if rag.query("venue_address", keyword) else ""
        data = f"{venue}, {city}, {country}"
        if address:
            data += f" | Address: {address}"

    # ————————————————————
    # 3. TICKET
    # ————————————————————
    elif intent == "ticket" and keyword:
        info = rag.get_ticket_info(keyword)
        tiers = info["tiers"]
        payment = rag.query("ticket_payment_methods", keyword)
        note = info["note"]

        tier_str = " • ".join(tiers) if tiers else "Not announced"
        payment_str = payment[0] if payment else "Not specified"
        note_str = note or ""

        data = f"TICKETS: {tier_str}"
        if payment_str != "Not specified":
            data += f" | PAYMENT: {payment_str}"
        if note_str:
            data += f" | NOTE: {note_str}"

    # ————————————————————
    # 4. LOGISTICS
    # ————————————————————
    elif intent == "logistics" and keyword:
        logi = rag.get_logistics(keyword)
        apps = ", ".join(logi["transport_apps"]) if logi["transport_apps"] else "Uber, local taxis"
        hoods = ", ".join(logi["neighborhoods"][:3]) if logi["neighborhoods"] else "near venue"
        emergency = logi["emergency"]["police"] or "911"
        crypto = logi["crypto_shops"] or "Some shops accept crypto"
        data = f"RIDE APPS: {apps} | STAY: {hoods} | EMERGENCY: {emergency} | CRYPTO: {crypto}"

    # ————————————————————
    # 5. SIDE EVENTS
    # ————————————————————
    elif intent == "side_event":
        events = rag.get_side_events()
        if events:
            full_list = "\n".join([f"• {name}: {desc}" for name, desc in events])
            return {
                "selected_question": "What are the side events?",
                "humanized_answer": f"SIDE EVENTS:\n{full_list}"
            }
        else:
            return {
                "selected_question": "What are the side events?",
                "humanized_answer": "No side events announced yet."
            }

    # ————————————————————
    # 6. SPEAKERS
    # ————————————————————
    elif intent == "speakers" and keyword:
        speakers = rag.get_speakers(keyword)
        if speakers:
            data = f"SPEAKERS: {', '.join(speakers[:5])}"
        else:
            data = "Speakers to be announced."

    # ————————————————————
    # 7. PROGRAM
    # ————————————————————
    elif intent == "program":
        if "destino" in query.lower():
            info = rag.get_scholarships()
            data = f"DESTINO: {' | '.join(info) if info else 'Free tickets + travel support'}"
        elif "frens" in query.lower():
            info = rag.get_frens_program()
            data = f"FRENS: {' | '.join(info) if info else 'Community visibility'}"
        else:
            data = "Destino and Frens help builders attend. Check eligibility."

    # ————————————————————
    # 8. FAQ
    # ————————————————————
    elif intent == "faq":
        answer = rag.query_faq(keyword)
        if answer:
            data = answer
        else:
            new = generate_knowledge_response(query, intent, keyword, llm)
            rag.add_knowledge("faq", keyword, new)
            print(f"Learned FAQ: {keyword}")
            data = new

    # ————————————————————
    # 9. FALLBACK
    # ————————————————————
    else:
        data = "Kindly ask more descriptive questions. About dates, tickets, venue, logistics, or programs for example."

    # ————————————————————
    # Final Prompt
    # ————————————————————
    final_prompt = f"""
        USE EXACTLY THIS DATA (DO NOT CHANGE ANYTHING):
        {data}

        USER QUERY: "{query}"

        RESPOND IN THIS FORMAT ONLY:
        Selected Question: <1-line question>
        Humanized Answer: <exact data, no additions>
    """
    response = llm.create_completion(final_prompt, max_tokens=300)

    try:
        lines = [l.strip() for l in response.split("\n") if l.strip()]
        q = lines[0].split(":", 1)[1].strip() if len(lines) > 0 else query
        a = lines[1].split(":", 1)[1].strip() if len(lines) > 1 else data
        return {"selected_question": q, "humanized_answer": a}
    except:
        return {"selected_question": query, "humanized_answer": data}