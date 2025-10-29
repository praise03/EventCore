
![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)


[Chat with Event Assistant 🤖](https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8005&address=agent1qg927dsj0llmc2e4yyr23fq5s7dwqjgg737hly75y6uu4r5dm04vwnvyced/profile)

# EventCore — Event Assistant RAG 🗺️🎟️

## 🏡 Project Overview

**EventCore** is a modular, AI-powered event assistant that merges symbolic reasoning with 
retrieval-augmented generation. Built on **Hyperon/MeTTa** and **Fetch.ai’s uAgents**, it 
fuses an event knowledge graph with real-time data APIs to answer questions about schedules, 
tickets, venues, and travel.

---

## 🧩 Key Components

1. **`knowledge.py`** — Builds the MeTTa knowledge graph with structured atoms for events, venues, tickets, logistics, perks, and useful travel facts (airports, temps, neighborhoods, emergency numbers, etc.). This is the *single source of truth* for the RAG layer.  
2. **`event_rag.py`** — `EventRAG` class: simple, robust retrieval API over the MeTTa graph. Methods include `get_event_summary`, `get_ticket_info`, `get_side_events`, `get_logistics`, `query_faq`, and `add_knowledge`. 
3. **`utils.py`** — Orchestration and LLM glue. Contains the `LLM` wrapper for ASI:One, intent classification prompt, `process_query()` pipeline, and fallback learning logic for missing FAQs. Produces structured output: `{"selected_question": "...", "humanized_answer": "..."}`.  
4. **`agent.py`** — Agent runtime using uAgents: mailbox setup, chat protocol handlers, MeTTa initialization, and wiring of `EventRAG` + `utils.process_query` to respond to messages. Configured for mailbox mode (mailbox=True) so it can run as a hosted/offline agent on Agentverse.  
5. **Tools / integrations (including `currency-converter.py`, `weather.py`, `hotels.py`, `flights.py`) ** — helpers for flights, hotels, weather and currency (quering APIs like Open‑Meteo, Amadeus... for real time accurate results). These are essential modules used by a the event assistant that coordinates to provide crucial information to users.

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
