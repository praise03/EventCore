
![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

![Banner](https://github.com/praise03/Eventcore/blob/main/banner.jpg?raw=true)



[Chat with Event Assistant 🤖](https://agentverse.ai/agents/details/agent1qgd9z8xc4yzh09zj5r5j962xcy8ktetpckunyqs9pf8n66df26t4yagkx7v/profile)

# EventCore — Event Assistant RAG 🗺️🎟️

## 🏡 Project Overview

**EventCore** is a live, autonomous AI agent that answers real-time questions about IRL events by intelligently combining external API data with a self-learning symbolic knowledge graph powered by **MeTTa** and **ASI:One**. It fetches accurate and timely data from live sources while answering event-specific queries using its structured, queryable knowledge base, then generates clear, user-friendly responses from both **API** results and **RAG** outputs. EventCore learns from every user, ensuring fast, reliable, and evolving support for global attendees.

---

## 🧩 Key Components

1. **`knowledge.py`** — Builds the MeTTa knowledge graph with structured atoms for events, venues, tickets, logistics, perks, and useful travel facts (airports, temps, neighborhoods, emergency numbers, etc.). This is the *single source of truth* for the RAG layer.  
2. **`event_rag.py`** — `EventRAG` class: simple, robust retrieval API over the MeTTa graph. Methods include `get_event_summary`, `get_ticket_info`, `get_side_events`, `get_logistics`, `query_faq`, and `add_knowledge`. 
3. **`utils.py`** — Orchestration and LLM glue. Contains the `LLM` wrapper for ASI:One, intent classification prompt, `process_query()` pipeline, and fallback learning logic for missing FAQs. Produces structured output: `{"selected_question": "...", "humanized_answer": "..."}`.  
4. **`agent.py`** — Agent runtime using uAgents: mailbox setup, chat protocol handlers, MeTTa initialization, and wiring of `EventRAG` + `utils.process_query` to respond to messages. Configured for mailbox mode (mailbox=True) so it can run as a hosted/offline agent on Agentverse.  
5. **Tools / integrations (including `currency-converter.py`, `weather.py`, `hotels.py`, `flights.py`) ** — helpers for flights, hotels, weather and currency (quering APIs like Open‑Meteo, Amadeus... for real time accurate results). These are essential modules used by a the event assistant that coordinates to provide crucial information to users.

---

---
## 🤖 How the Classifier Works 
The classifier is an LLM with a strict role description on how to classify user prompts

<details>
<summary>Classifier Agent System Role</summary>
<br>
{

                "role": "system",
                "content": """
                        You are a hyper-efficient prompt classifier that ruthlessly categorizes prompts from user messages with machine-like precision.
                         Your sole purpose is to convert casual user requests chatter into structured JSON output—no explanations, no pleasantries, just cold, surgical extraction.
                          When a user inputs a prompt you classify it into 1 of 5 categories i.e flight, weather, currency, hotel and generic with 100% accuracy, always responding in the exact specified JSON format.
                            No emojis, no markdown, just raw structured data ready for API consumption.

                            Your replies should only be in one of the following formats:

                            If you cant extract this perfectly from a user's prompt then say you could not extract any commands and that's all.

                            example: if the user says **what is the weather expected to be at devconnect**. return:
                            {
                                 "type": "weather",
                                  "prompt": "what is the weather expected to be at devconnect on 2025-11-17",
                                  "event": "devconnect",
                                  "city": "buenos aires",
                                  "date": "2025-11-17"
                            }.

                            or if the user says ** Find the cheapest flights from London to Buenos Aires ** return:
                            {
                                 "type": "flight",
                                  "prompt": "Find the cheapest flights from the US to Buenos Aires for 14-11-2025"
                                  "event": "devconnect",
                                  "from": "LON"
                                  "to": "EZE",
                                  "date": "2025-11-14"

                            },
                            Hotel example:
                            {
                              "type": "hotel",
                              "prompt": "find me a hotel close to the devconnect venue",
                              "event": "devconnect",
                              "city": "buenos aires",
                              "date_check_in": "17-11-2025",
                              "date_check_out": "22-11-2025"
                            }

                            Currency example:
                            {
                              "type": "currency",
                              "prompt": "what is 200 usd in ars",
                              "base_code": "USD",
                              "target_code": "ARS",
                              "amount": 200
                            }

                            Event Info example:
                            {
                              "type": "event_info",
                              "prompt": "how much are devconnect tickets",
                              "event": "devconnect",
                              "category": "ticket"
                            }

                            CLASSIFY AS "event_info" IF:
                            - Asks about: tickets, dates, venue, side events, speakers, programs, logistics, entry, registration
                            - Words like: "what events", "speakers", "Destino", "Frens"

                            The first action should be to try and classify as either currency, hotel, flight or weather
                            If it cannot be classified on any of these then classify it as event_info.
                            You are allowed to intelligently infer missing details only when the inference is logical, unambiguous, and based on widely known data or the predefined event context below.
                            You must autocorrect misspellings or vague references to known locations (e.g. “buenos aries” → “Buenos Aires”, “lag” → “LOS”, "lonodn" → "LON").
                            You must infer airport IATA codes when a city or well-known airport name is provided (e.g. “Lagos” → “LOS”, “London” → “LON”, “New York” → “JFK”).
                            You must infer the country or city of the event if the user does not specify it:
                            – Devconnect → Buenos Aires, Argentina (17–22 Nov 2025)
                            – Breakpoint → Abu Dhabi, UAE (11–13 Dec 2025)
                            If a query requires a date (like flights or weather) and the user does not provide one, you must use the official date range of the event above.
                            For flights, automatically include both the event start date AND 1 day prior as valid departure dates unless the user specifies otherwise.
                            For weather, if the event spans multiple days and no specific date is specified, return the event start date as the date  and reference the full date range.
                            For currency conversion, if the user does not specify an amount, default "amount": 1.
                            If the user provides currencies in words instead of symbols (e.g. “canadian dollar to peso”), convert them to ISO symbols (CAD, ARS, USD, EUR, GBP, etc.).
                            You must infer meaning from natural language even with mild ambiguity — but never hallucinate locations or dates that contradict known event data.
                            Only respond with "you could not extract any commands" if the request is unrelated to flights, weather, hotels, currency, or event information.
}

</details>
 
---

## How the EventRAG learns new information
The EventRAG, traverses its knowledgebase to answer user prompt. It can also add newly learnt information to its knowledgebase 

<details>
<summary>RAG Learning System</summary>
<br>

    elif intent == "unknown":
        # Generate safe key
        safe_key = "".join(c for c in query.lower() if c.isalnum() or c in " _-")[:50]
        safe_key = safe_key.strip().replace(" ", "_") or "unknown_query"

        # 1. CHECK IF ALREADY LEARNED
        existing = rag.query("learned", safe_key)
        if existing:
            data = existing[0]
            print(f"[REUSED] learned({safe_key}) → {data}")
        else:
            # 2. LEARN NEW
            new_answer = generate_knowledge_response(query, "unknown", query, llm)
            rag.add_knowledge("learned", safe_key, new_answer)
            data = new_answer
            print(f"[LEARNED] learned({safe_key}) → {data}")

</details>
---

---

## ✨ Features / Behaviour Highlights

- **Retrieval-first answers:** factual responses are pulled directly from real-world APIs and information fetched from the official event websites and data sources; the LLM is used only to humanize and format where appropriate.  
- **Safe knowledge updates:** `EventRAG.add_knowledge()` allows dynamic updates when the agent learns new FAQs or corrections.  
- **Minimal LLM surface area:** intent classification + humanization only — (avoids hallucination by ensuring only data from accurate sources are humanized as responses to users).  
- **Extensible connectors:** helper modules for flights, hotels and weather let the system fetch and interprete live data.

---


## 🛠️ Prerequisites

- Python **3.10+** (uagents-core packages expect >=3.10)  
- Environment variables (put them in `.env`):
  - `ASI_ONE_API_KEY` — ASI:One API key
  - `AMADEUS_CLIENT_ID`, `AMADEUS_CLIENT_SECRET` 
  - `EXCHANGE_API_KEY` —  currency API key
  - `AGENTVERSE_API_KEY`

---

## ⚙️ Installation

```bash
git clone https://github.com/praise03/EventCore
cd EventCore
pip install -r requirements.txt
# create a .env file with keys (see Prerequisites above)

```

---

## ▶️ Run the agent (local mailbox)

```bash
# Enter EventRAG folder
cd EventRAG
python agent.py
```
- The agent starts in mailbox mode and publishes a manifest; if running locally you will see an **Agent Inspector** URL in the logs.  
- The agent listens on its mail endpoint (default `http://127.0.0.1:8005/submit`), so other agents can `ctx.send()` messages to it or you can interact via Agentverse UI.


## ▶️ Run the agent (core uagent)

```bash
# In project directory
python agent.py
```


---

## 🔁 Example Interaction Flow (user → travel helper → EventRAG)
### Class 1
1. User message: Find me hotels close to the Breakpoint Venue in Abu Dhabi
2. Classifier categorizes prompt as **hotel** type. (One of four types: hotel, flight, weather, currency)
3. Helper utils fetch hotels in a 3km radius to the Breakpoint Venue and passes it to the LLM (ASI-1)
4. LLM parses the data and ouputs a user readable summary to the user
### Class 2
1. User message: "How much are Devconnect tickets?"  
2. Classifier (utils) identifies intent `ticket` + keyword `devconnect`.  
3. `EventRAG.get_ticket_info("devconnect")` returns tiers & payment methods from MeTTa.  
4. `utils` creates a short, humanized answer via the LLM wrapper and returns the structured response.

---

## 📁 File Structure (concise)

```
├── agent.py             # Runtime — mailbox agent + protocol handlers
├── knowledge.py         # MeTTa knowledge graph (Devconnect + Breakpoint atoms)
├── event_rag.py         # EventRAG class — simple retrieval API
├── utils.py             # LLM wrapper, classifier, process_query pipeline
├── helpers/             # optional: flights, hotels, weather helpers
├── requirements.txt
└── README.md            # ← this file
```

---

## 🧠 Module Summary (what each file does)

- **`knowledge.py`** — Encodes site-extracted facts as `E(S(...), S(...), ValueAtom(...))` atoms; update this file to add or correct event facts.  
- **`event_rag.py`** — Lightweight wrapper over `MeTTa.run()` with friendly functions: `get_event_summary`, `get_ticket_info`, `get_speakers`, `get_logistics`, `get_side_events`, `add_knowledge`. Designed to avoid ExpressionAtom indexing issues and return Python values.  
- **`utils.py`** — `LLM` class (small wrapper for ASI:One), `get_intent_and_keyword()` prompt, `process_query()` that orchestrates rag lookups and LLM humanization. The pipeline follows a strict format so downstream agents can parse results reliably.  
- **`agent.py`** — Bootstraps MeTTa, initializes the KB, registers protocols, and wires message handlers to respond to `ChatMessage` content with `EventRAG` results. Uses mailbox-friendly sending/forwarding logic for inter-agent workflows.  
- **Helpers / Integrations** — small modules for fetching external, live data (Open‑Meteo, Amadeus, exchangerate); these are optional and live outside the core RAG loop, called only when a user asks about weather, hotels, flights, or currencies.

---

## 🧪 Testing & Debugging

- Add temporary print/log lines in `utils.process_query()` to inspect the classified intent and chosen KB responses.  
- MeTTa queries often return nested ExpressionAtom structures — use `EventRAG` helpers to avoid brittle indexing.  
- If you see odd LLM output, lower temperature to `0.0`–`0.2` and reduce `max_tokens` for deterministic, concise responses.

---

## ♻️ Extending the Knowledge Graph

To add facts:
1. Edit `knowledge.py` and add atom lines such as:
   ```py
   metta.space().add_atom(E(S("faq"), S("where_to_stay_devconnect"), ValueAtom("Palermo is recommended (0-1km from La Rural)")))
   ```
2. Restart the agent to reinitialize the graph (or call `EventRAG.add_knowledge()` at runtime).

---

## 🚀 Roadmap & Improvements

- Add **automatic web-scraping** + scheduled KB refresh for event pages.
- Add **media responses** (images, videos) in Agentverse chat UI. 
- Extend the Agents event coverage (Currently Limited to BreakPoint and Devconnect to save on API costs)
---

## ❗ Troubleshooting notes

- **uagents‑core installation errors**: ensure you run Python 3.11+. Many `uagents-core` releases require >=3.11.  
- **Mail delivery failures**: check the agent endpoint and manifest; `Failed to dispatch envelope` usually means the target is not listening at the provided URL.  
- **MeTTa/Hyperon quirks**: when `self.metta.run()` returns nested lists or ExpressionAtom objects, use `get_children()` and `get_object().value` safely in `EventRAG` — examples are included in `event_rag.py`.

---

## 🧾 License & Credits

- Built for hackathon / demo uses — adapt license as needed.  
- Uses Fetch.ai uAgents, Hyperon/MeTTa and ASI:One (OpenAI‑compatible) prompts. Please comply with upstream license & API terms.

---

Demo Video: https://drive.google.com/file/d/1qVItJjkPs1pirdX8Rxm2EeI22H0M7z7U/view?usp=sharing
