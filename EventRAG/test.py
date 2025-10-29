# Import components from separate files
from event_rag import EventRAG
from knowledge import initialize_knowledge_graph
from utils import LLM, process_query, get_intent_and_keyword
from hyperon import MeTTa, E, S, ValueAtom

# Initialize global components
metta = MeTTa()
initialize_knowledge_graph(metta)
rag = EventRAG(metta)
llm = LLM("")

query = "Can I bring my laptop?"

# print(f"\nQUERY: {query}")
# result = process_query(query, rag, llm)
#
# print(f"\nRESULT:")
# print(f"Selected Question: {result['selected_question']}")
# print(f"Humanized Answer: {result['humanized_answer']}")

# def query(self, relation: str, subject: str):
#     if not subject:
#         return []
#     results = self.metta.run(f'!(match &self ({relation} {subject} $value) $value)')
#     return [str(r[0]) for r in results if r and len(r) > 0]

# test_unknown_reuse.py
query = "How much are breakpoint tickets"

result1 = process_query(query, rag, llm)
print(result1['humanized_answer'])  # → LLM answer

# Second time
# result2 = process_query(query, rag, llm)
# print(result2['humanized_answer'])  # → SAME answer, NO LLM CALL

# queries = [
#     "When is Devconnect?",
#     "Tickets for Breakpoint?",
#     "Where is the venue for breakpoint?",
#     "What are side events for breakpoint?",
#     "How do I get to La Rural?",
#     "Who is speaking at devconnect?",
#     "Is there a FAQ?",
#     "Random nonsense question"
# ]
#
# for q in queries:
#     intent, kw = get_intent_and_keyword(q, llm)
#     print(f"{q} → ({intent}, {kw})")