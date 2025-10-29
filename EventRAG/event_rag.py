# event_rag.py

"""
generalrag.py implements EventRAG (class), a Retrieval-Augmented Generation interface over the MeTTa knowledge graph,
providing high-level methods to query event data (get_ticket_info, get_logistics, get_side_events, etc.) and
safely convert symbolic results into Python structures. It handles complex atom traversal (including ExpressionAtoms),
ensures robust string extraction, and supports dynamic knowledge expansion via add_knowledge. This module serves as
the bridge between symbolic reasoning and natural language agent responses.
"""

from hyperon import MeTTa, E, S
from hyperon.atoms import ValueAtom  # Correct import
from typing import List, Tuple, Optional, Dict, Any


class EventRAG:
    def __init__(self, metta_instance: MeTTa):
        self.metta = metta_instance

    # ================================================================
    # CORE: Robust Generic Query
    # ================================================================
    def _query_generic(self, relation: str, subject: str, var_name: str = "$value") -> List[str]:
        """Internal: robust match with full safety."""
        subject = subject.strip().strip('"')

        # Try SYMBOL
        query = f'!(match &self ({relation} {subject} {var_name}) {var_name})'
        results = self.metta.run(query)

        if results:
            extracted = []
            for r in results:
                if not r:  # Skip empty inner lists
                    continue
                atom = r[0]
                if hasattr(atom, 'get_object') and atom.get_object() is not None:
                    extracted.append(atom.get_object().value)
                else:
                    extracted.append(str(atom))
            return extracted

        # Try QUOTED STRING
        query = f'!(match &self ({relation} "{subject}" {var_name}) {var_name})'
        results = self.metta.run(query)

        if results:
            extracted = []
            for r in results:
                if not r:
                    continue
                atom = r[0]
                if hasattr(atom, 'get_object') and atom.get_object() is not None:
                    extracted.append(atom.get_object().value)
                else:
                    extracted.append(str(atom))
            return extracted

        return []

    def query(self, relation: str, subject: str) -> List[str]:
        """Query value atoms (strings, numbers)."""
        return self._query_generic(relation, subject, "$value")

    def query_symbol(self, relation: str, subject: str) -> List[str]:
        """Query symbolic atoms (non-ValueAtom)."""
        subject = subject.strip().strip('"')
        query = f'!(match &self ({relation} {subject} $sym) $sym)'
        results = self.metta.run(query)
        return [str(r[0]) for r in results] if results else []

    # ================================================================
    # FAQ: Robust Symbol-First
    # ================================================================
    def query_faq(self, question: str) -> Optional[str]:
        """Get FAQ answer — supports symbol keys."""
        question = question.strip().strip('"')

        # 1. Symbol
        results = self.metta.run(f'!(match &self (faq {question} $answer) $answer)')
        if results and results[0]:
            obj = results[0][0].get_object()
            return obj.value if obj is not None else str(results[0][0])

        # 2. Quoted
        results = self.metta.run(f'!(match &self (faq "{question}" $answer) $answer)')
        if results and results[0]:
            obj = results[0][0].get_object()
            return obj.value if obj is not None else str(results[0][0])

        return None

    # ================================================================
    # EVENT-SPECIFIC QUERIES
    # ================================================================
    def get_event_summary(self, event_key: str) -> Dict[str, Any]:
        """Full event overview."""
        fullname = self.query("event_fullname", event_key)
        name = self.query("event", event_key)
        return {
            "name": fullname[0] if fullname else (name[0] if name else event_key),
            "organizer": self.query("organiser", event_key)[0] if self.query("organiser", event_key) else None,
            "dates": self.query("date_range", event_key)[0] if self.query("date_range", event_key) else None,
            "venue": self.query("venue", event_key)[0] if self.query("venue", event_key) else None,
            "city": self.query("venue_city", event_key)[0] if self.query("venue_city", event_key) else None,
            "country": self.query("venue_country", event_key)[0] if self.query("venue_country", event_key) else None,
            "description": (
                self.query("event_description", event_key) or
                self.query("short_desc", event_key) or
                [""]
            )[0],
        }

    def get_ticket_info(self, event_key: str) -> Dict[str, Any]:
        """All ticketing details — safe and efficient."""
        tiers = self.get_ticket_tiers(event_key)
        payment = self.query("ticket_payment_methods", event_key)
        note = self.query("ticket_note", event_key)

        return {
            "tiers": tiers,
            "payment": payment[0] if payment else None,
            "note": note[0] if note else None,
        }

    def get_ticket_tiers(self, event_key: str) -> List[str]:
        return self.query("ticket_tier", event_key)

    def get_side_events(self) -> List[Tuple[str, str]]:
        """Return ALL side events safely — handles ExpressionAtoms"""
        results = self.metta.run('!(match &self (side_event $name $desc) ($name $desc))')
        events = []

        if not results:
            return events

        for result in results:
            # result is a list of ExpressionAtoms: (name, desc)
            for expr in result:
                if hasattr(expr, 'get_children') and len(expr.get_children()) == 2:
                    name_atom = expr.get_children()[0]
                    desc_atom = expr.get_children()[1]

                    name = str(name_atom)
                    desc = str(desc_atom)
                    events.append((name, desc))

        return events

    def get_speakers(self, event_key: str) -> List[str]:
        return self.query("speaker", event_key)

    def get_programs(self) -> List[Tuple[str, str]]:
        """All programs: Destino, Frens, etc."""
        results = self.metta.run('!(match &self (program $key $value) ($key $value))')
        return [
            (
                str(r[0]),
                r[1].get_object().value if hasattr(r[1], 'get_object') and r[1].get_object() is not None else str(r[1])
            )
            for r in results
        ] if results else []

    def get_pre_events(self, event_key: str) -> List[str]:
        return self.query("pre_event", event_key)

    def get_logistics(self, event_key: str) -> Dict[str, Any]:
        """Travel, transport, safety, crypto."""
        return {
            "transport_apps": self.query_symbol("transport_app", event_key),
            "neighborhoods": self.get_neighborhoods(event_key),
            "crypto_shops": self.query("crypto_in_local_shops", event_key)[0] if self.query("crypto_in_local_shops", event_key) else None,
            "crypto_map": self.query("crypto_merchant_map", event_key)[0] if self.query("crypto_merchant_map", event_key) else None,
            "emergency": {
                "police": self.query("emergency_number_police", event_key)[0] if self.query("emergency_number_police", event_key) else None,
                "ambulance": self.query("emergency_number_ambulance", event_key)[0] if self.query("emergency_number_ambulance", event_key) else None,
                "fire": self.query("emergency_number_fire", event_key)[0] if self.query("emergency_number_fire", event_key) else None,
            },
            "safety_tips": self.query("safety_tip", event_key),
            "timezone": self.query("timezone", event_key)[0] if self.query("timezone", event_key) else None,
            "currency": self.query("currency", event_key)[0] if self.query("currency", event_key) else None,
        }

    def get_neighborhoods(self, event_key: str) -> List[str]:
        return self.query("recommended_neighborhood", event_key)

    def get_visa_info(self, event_key: str) -> List[str]:
        return self.query("visa_program", event_key)

    def get_weather_info(self, event_key: str) -> List[str]:
        return self.query("avg_temp_november", event_key)

    def get_scholarships(self) -> List[str]:
        return self.query("destino_scholarship", "devconnect_destino")

    def get_frens_program(self) -> List[str]:
        return self.query("frens_eligibility", "devconnect_frens")

    # ================================================================
    # DYNAMIC KNOWLEDGE
    # ================================================================
    def add_knowledge(self, relation_type: str, subject: str, object_value: Any) -> str:
        """Add new fact dynamically."""
        obj = ValueAtom(object_value) if isinstance(object_value, str) else object_value
        self.metta.space().add_atom(E(S(relation_type), S(subject), obj))
        return f"Added {relation_type}: {subject} → {object_value}"

    # ================================================================
    # UTILITY
    # ================================================================
    def search_events(self, keyword: str) -> List[str]:
        """Fuzzy search across event names, venues, descriptions."""
        keyword = keyword.lower()
        results = []
        for event in ["devconnect_arg", "breakpoint"]:
            summary = self.get_event_summary(event)
            if any(keyword in str(v).lower() for v in summary.values() if v):
                results.append(event)
        return results