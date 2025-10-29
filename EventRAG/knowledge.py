# knowledge.py
# Extracted knowledge from Devconnect ARG and Breakpoint UAE websites (site + subpages)
# Sources used: https://devconnect.org/, https://devconnect.org/calendar,
# https://devconnect.org/calendar?event=ethday, https://devconnect.org/perks,
# https://devconnect.org/destino, https://solana.com/breakpoint

# This file builds a MeTTa knowledge graph (hyperon) with concise atoms
# representing events, ticket rules, venue, perks and destination support info.

from hyperon import MeTTa, E, S, ValueAtom


def initialize_knowledge_graph(metta: MeTTa):
    """
    Initialize the MeTTa knowledge graph with facts parsed from Devconnect ARG pages.
    """

    # ----------------------------
    # General: Events & Identity
    # ----------------------------
    metta.space().add_atom(E(S("event"), S("devconnect"), S("Devconnect Argentina")))
    metta.space().add_atom(E(S("event_fullname"), S("devconnect"), S("Ethereum World Fair (Devconnect Argentina)")))
    metta.space().add_atom(E(S("organiser"), S("devconnect"), S("Ethereum Foundation")))

    metta.space().add_atom(E(S("event"), S("breakpoint"), S("Solana Breakpoint")))
    metta.space().add_atom(E(S("event_fullname"), S("breakpoint"), S("Breakpoint 2025")))
    metta.space().add_atom(E(S("organiser"), S("breakpoint"), S("Solana Foundation")))

    # ----------------------------
    # Dates & Venues
    # ----------------------------
    # Devconnect ARG (La Rural / Buenos Aires): calendar shows events across Nov 17-22, 2025
    metta.space().add_atom(E(S("date_range"), S("devconnect"), ValueAtom("2025-11-17 to 2025-11-22")))

    metta.space().add_atom(E(S("venue"), S("devconnect"), S("La Rural")))
    metta.space().add_atom(E(S("venue_address"), S("devconnect"),
                             ValueAtom("Av. Sarmiento 2704, Palermo, C1425 Cdad. Autónoma de Buenos Aires")))
    metta.space().add_atom(E(S("ticket_required"), S("devconnect"), ValueAtom(
        "World's Fair ticket required to enter La Rural; some side events may require separate registration or tickets")))

    # Breakpoint 2025 — Etihad Arena, Abu Dhabi (11-13 Dec 2025)
    metta.space().add_atom(E(S("date_range"), S("breakpoint"), ValueAtom("2025-12-11 to 2025-12-13")))

    metta.space().add_atom(E(S("venue"), S("breakpoint"), S("Etihad Arena")))
    metta.space().add_atom(E(S("venue_city"), S("breakpoint"), S("Abu Dhabi")))
    metta.space().add_atom(E(S("venue_country"), S("breakpoint"), S("United Arab Emirates")))
    metta.space().add_atom(E(S("short_desc"), S("breakpoint"), ValueAtom(
        "Breakpoint unites founders, developers, and creators for product keynotes, team vs team debates and fireside chats.")))

    # ----------------------------
    # Ticketing / Pricing (sourced from pages)
    # ----------------------------
    metta.space().add_atom(E(S("ticket_tier"), S("breakpoint"), ValueAtom("general_admission:$500")))
    metta.space().add_atom(E(S("ticket_tier"), S("breakpoint"), ValueAtom("developer:$250")))
    metta.space().add_atom(E(S("ticket_tier"), S("breakpoint"), ValueAtom("artist:$250")))
    metta.space().add_atom(E(S("ticket_tier"), S("breakpoint"), ValueAtom("student:$100")))

    # Devconnect ticketing notes
    metta.space().add_atom(E(S("ticket_tier"), S("devconnect"), ValueAtom("General: USD 120, ARG Local Discount: USD 20, "
                                                                          "LATAM Discount: USD 60, Academic / Student: USD 20, "
                                                                          "Youth (under 18): Free, Core Dev / Protocol Guild: Free")))
    # metta.space().add_atom(E(S("ticket_tier"), S("devconnect"), ValueAtom("ARG Local Discount: USD 20")))
    # metta.space().add_atom(E(S("ticket_tier"), S("devconnect"), ValueAtom("LATAM Discount: USD 60")))
    # metta.space().add_atom(E(S("ticket_tier"), S("devconnect"), ValueAtom("Academic / Student: USD 20")))
    # metta.space().add_atom(E(S("ticket_tier"), S("devconnect"), ValueAtom("Youth (under 18): Free")))
    # metta.space().add_atom(E(S("ticket_tier"), S("devconnect"), ValueAtom("Core Dev / Protocol Guild: Free")))

    metta.space().add_atom(E(S("ticket_payment_methods"), S("devconnect"),
                             ValueAtom("Crypto Payment via Daimo Pay or Fiat via Stripe")))
    metta.space().add_atom(E(S("ticket_note"), S("devconnect"), ValueAtom(
        "World's Fair ticket gating applies for on-site La Rural activities; many side events may require additional sign-up or ticketing.")))

    # ----------------------------
    # Calendar Highlights / Side Events (Devconnect)
    # ----------------------------
    # (include representative side events listed on the calendar)
    metta.space().add_atom(
        E(S("side_event"), S("staking_summit"), ValueAtom("Nov 15-16 — Staking Summit (tickets required)")))
    metta.space().add_atom(
        E(S("side_event"), S("hyperliquid_hackathon"), ValueAtom("Nov 15-16 — Hyperliquid Hackathon (looping 24h)")))
    metta.space().add_atom(
        E(S("side_event"), S("crecimiento_startup_worldcup"), ValueAtom("Nov 15-16 — Crecimiento Startup Worldcup")))
    metta.space().add_atom(E(S("side_event"), S("governance_day"), ValueAtom("Nov 15 — Governance Day (Main)")))

    # Ethereum Day mention (Devconnect site has an Ethereum Day page)
    metta.space().add_atom(E(S("related_day"), S("devconnect"), S("ethereum_day")))

    # ----------------------------
    # Destino / Access & Scholarships (Devconnect)
    # ----------------------------
    metta.space().add_atom(E(S("program"), S("devconnect_destino"), S("Destino Support")))
    metta.space().add_atom(E(S("destino_goal"), S("devconnect_destino"), ValueAtom(
        "Support local builders, organizers and communities to attend the Ethereum World Fair")))
    metta.space().add_atom(E(S("destino_offering"), S("devconnect_destino"), ValueAtom(
        "Free tickets, discounts, scholarships, and travel/transport assistance for communities and initiatives")))
    metta.space().add_atom(E(S("destino_scholarship"), S("devconnect_destino"), ValueAtom(
        "Scholarship funding available (limited budget) — up to USD 1,000 of support is referenced for community initiatives)")))
    metta.space().add_atom(E(S("destino_apply"), S("devconnect_destino"), ValueAtom(
        "Applications for support and tickets are time-limited; application deadlines are posted on the Destino page")))

    # Devconnect Frens program
    metta.space().add_atom(E(S("program"), S("devconnect_frens"), ValueAtom(
        "Community advocacy program to gain visibility and support attendance (free tickets, discounts, on-chain certificate)")))
    metta.space().add_atom(E(S("frens_eligibility"), S("devconnect_frens"), ValueAtom(
        "Universities, startups, communities, organizers, hacker houses and cowork groups")))

    # ----------------------------
    # Perks & Logistics (Devconnect)
    # ----------------------------
    metta.space().add_atom(E(S("perks_note"), S("devconnect"), ValueAtom(
        "Perks, code of conduct and official support resources maintained by Ethereum Foundation; see Devconnect perks page for curated offerings")))
    metta.space().add_atom(E(S("contact"), S("devconnect"), ValueAtom(
        "Contact links and policies available: Code of Conduct, Terms & Conditions, Privacy on official site")))

    # ----------------------------
    # Breakpoint: Themes, Format, & Highlights
    # ----------------------------
    metta.space().add_atom(E(S("breakpoint_theme"), S("breakpoint"), ValueAtom("Two themes: Revenue and Returns")))
    metta.space().add_atom(E(S("breakpoint_format"), S("breakpoint"), ValueAtom(
        "No panels; product keynotes, team vs team debates, fireside chats, and react-style interviews")))
    metta.space().add_atom(E(S("breakpoint_attendees"), S("breakpoint"), ValueAtom(
        "Audience: builders, investors, operators; historically 6000+ attendees from 100+ countries")))

    # ----------------------------
    # Breakpoint: Participation & Calls
    # ----------------------------
    metta.space().add_atom(E(S("how_to_participate"), S("breakpoint"), ValueAtom(
        "Speak (applications closed), sponsor (limited brand activations), press & content creator application links available")))
    metta.space().add_atom(E(S("breakpoint_travel_guide"), S("breakpoint"), ValueAtom(
        "Official travel guide and resources for Abu Dhabi (travel, hotels, local events)")))

    # ----------------------------
    # Speakers / Notable People (sample)
    # ----------------------------
    # Breakpoint notable speaker examples (page lists many — include representative entries)
    metta.space().add_atom(E(S("speaker"), S("breakpoint"), ValueAtom("Lily Liu — President, Solana Foundation")))
    metta.space().add_atom(E(S("speaker"), S("breakpoint"), ValueAtom("Anatoly Yakovenko — Co-Founder/CEO, Solana")))
    metta.space().add_atom(
        E(S("speaker"), S("breakpoint"), ValueAtom("Raj Gokal — Co-Founder/COO, Solana / Solana Labs")))

    # Devconnect: organizer / community leads (representative)
    metta.space().add_atom(E(S("speaker"), S("devconnect"), ValueAtom(
        "Community leads, Ethereum Foundation organizers and invited speakers across program tracks")))

    # ----------------------------
    # Practical facts for agent usage
    # ----------------------------
    metta.space().add_atom(E(S("faq"), S("how_to_enter_la_rural"), ValueAtom(
        "You need a Devconnect World’s Fair ticket to enter La Rural; some hosted side events may require separate sign-up or tickets.")))
    metta.space().add_atom(E(S("faq"), S("devconnect_dates"), ValueAtom(
        "Devconnect Argentina event window spans mid-November 2025 (Nov 15-22) across world fair and side events.")))
    metta.space().add_atom(E(S("faq"), S("breakpoint_dates"),
                             ValueAtom("Breakpoint 2025 runs 11-13 December 2025 at Etihad Arena, Abu Dhabi.")))
    metta.space().add_atom(E(S("faq"), S("breakpoint_prices"), S("see_ticket_tiers")))
    metta.space().add_atom(E(S("faq"), S("devconnect_ticket_pricing"), ValueAtom(
        "General admission USD120; local ARG USD20; LATAM USD60; academic USD20; youth or core dev may be free."))
                           )

    metta.space().add_atom(E(S("faq"), S("devconnect_ticket_inclusions"), ValueAtom(
        "World’s Fair access (17-22 Nov), Cowork & Community Hubs, Ethereum Day; many side-events still require separate signup or ticket."
    )))

    # ----------------------------
    # Sponsorship / Activation Notes
    # ----------------------------
    metta.space().add_atom(E(S("sponsorship_status"), S("breakpoint"), ValueAtom(
        "Arena sponsorships sold out; limited brand activations and closing celebration spots remain.")))
    metta.space().add_atom(E(S("sponsorship_status"), S("devconnect"), ValueAtom(
        "Sponsors and partners coordinate with Ethereum Foundation for World Fair activations; official sponsor & perks pages contain details.")))

    # ----------------------------
    # Frequently Asked Questions (short, actionable)
    # ----------------------------
    metta.space().add_atom(E(S("faq"), S("what_is_devconnect"), ValueAtom(
        "Devconnect is a regional Ethereum-focused event series culminating in an Ethereum World Fair in Buenos Aires in Nov 2025.")))
    metta.space().add_atom(E(S("faq"), S("what_is_breakpoint"), ValueAtom(
        "Breakpoint is Solana's flagship conference for builders, creators and investors; 2025 edition in Abu Dhabi.")))
    metta.space().add_atom(E(S("faq"), S("are_sessions_recorded"), S("check_event_faqs")))
    metta.space().add_atom(E(S("faq"), S("how_to_apply_scholarship"), S("apply_via_destino_or_event_forms")))

    # ----------------------------
    # Utility / Source Pointers (helpful to the agent)
    # ----------------------------
    metta.space().add_atom(
        E(S("source"), S("devconnect"), ValueAtom("https://devconnect.org/ (calendar, perks, destino pages)")))
    metta.space().add_atom(E(S("source"), S("breakpoint"), ValueAtom("https://solana.com/breakpoint")))

    # ----------------------------
    # Example solutions / agent actions
    # ----------------------------
    # metta.space().add_atom(E(S("solution"), S("find_nearest_hotels"), ValueAtom(
    #     "Query venue geo and filter hotels within walking distance; use Amadeus hotel list and haversine for ranking")))
    # metta.space().add_atom(E(S("solution"), S("get_weather_for_event"), ValueAtom(
    #     "Fetch 3-day forecast from Open-Meteo; for event dates beyond forecast, use trend-based prediction or call longer-range services")))

    # --- Devconnect Argentina: Additional Travel & Logistics Facts ---
    metta.space().add_atom(E(S("event_attendance_estimate"), S("devconnect"), ValueAtom("15000")))
    metta.space().add_atom(E(S("event_description"), S("devconnect"),
                              ValueAtom("The first Ethereum World’s Fair arrives in Buenos Aires: six days of hands-on Ethereum showcase from stablecoins & on-chain ID to DeFi, social, art and games.")))
    metta.space().add_atom(E(S("why_location"), S("devconnect"),
                              ValueAtom("Argentina sees nearly 5 million daily digital-asset users and 118% inflation in 2024; local crypto communities are highly active.")))

    # Airport & Transport
    metta.space().add_atom(E(S("airport_intl"), S("devconnect"), S("EZE")))
    metta.space().add_atom(E(S("airport_dom"), S("devconnect"), S("AEP")))
    metta.space().add_atom(E(S("currency"), S("devconnect"), S("ARS")))
    metta.space().add_atom(E(S("timezone"), S("devconnect"), S("UTC-3")))
    metta.space().add_atom(E(S("avg_temp_november"), S("devconnect"), ValueAtom("16-26°C (61-79°F)")))
    metta.space().add_atom(E(S("water_safety"), S("devconnect"), ValueAtom("Tap water in Buenos Aires generally potable")))
    metta.space().add_atom(E(S("power_supply"), S("devconnect"), ValueAtom("220 V, plugs type C & I (Euro two-pin works)")))
    metta.space().add_atom(E(S("tipping_standard"), S("devconnect"), ValueAtom("10% standard at restaurants")))

    # Visa & Accommodation
    metta.space().add_atom(E(S("visa_program"), S("devconnect"), ValueAtom("Special visa programme for Devconnect participants; ticket must be secured and visa form completed.")))
    metta.space().add_atom(E(S("recommended_neighborhood"), S("devconnect"), ValueAtom("Palermo Soho/Hollywood/Botánico – 0-1 km from La Rural; nightlife, cafés, bars.")))
    metta.space().add_atom(E(S("recommended_neighborhood"), S("devconnect"), ValueAtom("Las Cañitas – ~1.5 km; foodie district around Báez St.; safe and laid-back.")))
    metta.space().add_atom(E(S("recommended_neighborhood"), S("devconnect"), ValueAtom("Palermo Chico – ~1 km; calm/green high-end residential.")))
    metta.space().add_atom(E(S("recommended_neighborhood"), S("devconnect"), ValueAtom("Recoleta – ~3 km; 10 min taxi or 15 min subway; classic architecture, cafés.")))
    metta.space().add_atom(E(S("recommended_neighborhood"), S("devconnect"), ValueAtom("Belgrano – ~3 km; family-friendly restaurants; train Mitre access.")))
    metta.space().add_atom(E(S("recommended_neighborhood"), S("devconnect"), ValueAtom("Villa Crespo/Colegiales – ~2 km; quieter, affordable; emerging food·crypto hub.")))

    # Getting Around & Ride-Apps
    metta.space().add_atom(E(S("transport_app"), S("devconnect"), S("Cabify")))
    metta.space().add_atom(E(S("transport_app"), S("devconnect"), S("Didi")))
    metta.space().add_atom(E(S("transport_app"), S("devconnect"), S("Uber")))
    metta.space().add_atom(E(S("tips_transport"), S("devconnect"), ValueAtom(
        "Use pre-booked remis or Tienda León bus from EZE to city; subway + buses accept contactless payment.")))

    # Crypto and payments
    metta.space().add_atom(E(S("crypto_in_local_shops"), S("devconnect"),
                              ValueAtom("100+ cafés & shops accept USDT/DAI via QR; look for 'Cripto accepted' signs.")))
    metta.space().add_atom(E(S("crypto_merchant_map"), S("devconnect"),
                              ValueAtom("https://www.google.com/maps/d/u/0/viewer?mid=1knsvDBZKn-GIx_HADBmjAoVX3i8YJTe8kA36a54?ll=-34.5900847,-58.4504032&z=13")))

    # Safety & Emergency
    metta.space().add_atom(E(S("emergency_number_police"), S("devconnect"), ValueAtom("911")))
    metta.space().add_atom(E(S("emergency_number_ambulance"), S("devconnect"), ValueAtom("107")))
    metta.space().add_atom(E(S("emergency_number_fire"), S("devconnect"), ValueAtom("100")))
    metta.space().add_atom(E(S("safety_tip"), S("devconnect"), ValueAtom(
        "Avoid phone use near subway/bus doors; keep bags forward; at night move in groups; avoid Constitución/Once/Microcentro alone.")))

    # Pre-event & Regional Signals
    metta.space().add_atom(E(S("pre_event"), S("devconnect"), ValueAtom("Edge City Patagonia: Oct 18-Nov 15, 2025 – 20% off with Devconnect ticket")))
    metta.space().add_atom(E(S("pre_event"), S("devconnect"), ValueAtom("Invisible Garden – Buenos Aires: Oct 27-Nov 16, 2025")))
    metta.space().add_atom(E(S("pre_event"), S("devconnect"), ValueAtom("ETH Latam – São Paulo: Nov 8-9, 2025")))
    metta.space().add_atom(E(S("pre_event"), S("devconnect"), ValueAtom("Ethereum Chile: Oct 24-25, 2025")))

    # City / Venue Info
    metta.space().add_atom(E(S("venue_city"), S("devconnect"), S("Buenos Aires")))
    metta.space().add_atom(E(S("venue_country"), S("devconnect"), S("Argentina")))


    # ----------------------------
    # Closing helpful pointers
    # ----------------------------
    metta.space().add_atom(E(S("note"), S("devconnect_local"), ValueAtom(
        "La Rural is the primary World Fair venue; many community side events occur across Buenos Aires — check calendar filters for side-event locations")))
    metta.space().add_atom(E(S("note"), S("breakpoint_local"), ValueAtom(
        "Breakpoint sits alongside Abu Dhabi Finance Week and Formula 1 during the same week — plan travel accordingly")))

    return "✅ Devconnect + Breakpoint knowledge graph initialized"
