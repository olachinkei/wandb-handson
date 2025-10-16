from dataclasses import dataclass
from typing import Callable, List


@dataclass
class EvalResult:
    correct_final_output: bool
    correct_tool_calls: bool
    correct_agent_routing: bool
    appropriate_steps: bool

    def total_score(self) -> float:
        criteria = [
            self.correct_final_output,
            self.correct_tool_calls,
            self.correct_agent_routing,
            self.appropriate_steps,
        ]
        return sum(criteria) / len(criteria) * 100

    def __str__(self) -> str:
        return (
            f"Final Output: {'✅' if self.correct_final_output else '❌'}\n"
            f"Tool Calls: {'✅' if self.correct_tool_calls else '❌'}\n"
            f"Agent Routing: {'✅' if self.correct_agent_routing else '❌'}\n"
            f"Step Count: {'✅' if self.appropriate_steps else '❌'}\n"
            f"Total Score: {self.total_score()}%"
        )


@dataclass
class ExpectedBehavior:
    final_output_validator: Callable[[str], bool]
    expected_tool_calls: List[str]
    expected_agent_sequence: List[str]
    min_steps: int
    max_steps: int


# Individual Agent Tests
FLIGHT_AGENT_TESTS = [
    (
        "I am Din. Book a one way flight to Ireland tomorrow. My phone number is 1234567890.",
        ExpectedBehavior(
            final_output_validator=lambda x: all(
                term.lower() in x.lower() for term in ["ireland", "flight"]
            ),
            expected_tool_calls=["search_flights"],
            expected_agent_sequence=["Flight Booking Agent"],
            min_steps=2,
            max_steps=4,
        ),
    ),
    (
        "Need a flight from London to Paris on 2024-06-15",
        ExpectedBehavior(
            final_output_validator=lambda x: all(
                term.lower() in x.lower() for term in ["london", "paris", "fl"]
            ),
            expected_tool_calls=["search_flights"],
            expected_agent_sequence=["Flight Booking Agent"],
            min_steps=2,
            max_steps=4,
        ),
    ),
    (
        "Looking for flights between New York and Tokyo for next week",
        ExpectedBehavior(
            final_output_validator=lambda x: all(
                term.lower() in x.lower() for term in ["new york", "tokyo", "fl"]
            ),
            expected_tool_calls=["search_flights"],
            expected_agent_sequence=["Flight Booking Agent"],
            min_steps=2,
            max_steps=4,
        ),
    ),
]

HOTEL_AGENT_TESTS = [
    (
        "I am Ana. Book a hotel in Tokyo for 3 nights. My phone number is 1234567890. The checkin date is 2025-05-01",
        ExpectedBehavior(
            final_output_validator=lambda x: "hotel foo, hotel bar" in x.lower(),
            expected_tool_calls=["search_hotels"],
            expected_agent_sequence=["Hotel Booking Agent"],
            min_steps=2,
            max_steps=4,
        ),
    ),
    (
        "Need accommodation in Paris for 5 nights starting 2024-07-01",
        ExpectedBehavior(
            final_output_validator=lambda x: all(
                term.lower() in x.lower() for term in ["paris", "hotel"]
            ),
            expected_tool_calls=["search_hotels"],
            expected_agent_sequence=["Hotel Booking Agent"],
            min_steps=2,
            max_steps=4,
        ),
    ),
    (
        "Looking for a hotel in London for 2 nights from tomorrow",
        ExpectedBehavior(
            final_output_validator=lambda x: all(
                term.lower() in x.lower() for term in ["london", "hotel"]
            ),
            expected_tool_calls=["search_hotels"],
            expected_agent_sequence=["Hotel Booking Agent"],
            min_steps=2,
            max_steps=4,
        ),
    ),
]

CLAIMS_AGENT_TESTS = [
    (
        "I need to file a claim for my delayed flight FL123 from yesterday",
        ExpectedBehavior(
            final_output_validator=lambda x: all(
                term.lower() in x.lower() for term in ["fl123", "clm-0001"]
            ),
            expected_tool_calls=["submit_flight_claim"],
            expected_agent_sequence=["Claims Agent"],
            min_steps=2,
            max_steps=5,
        ),
    ),
    (
        "My flight FL456 was cancelled last week, need to submit a claim",
        ExpectedBehavior(
            final_output_validator=lambda x: all(
                term.lower() in x.lower() for term in ["fl456", "clm"]
            ),
            expected_tool_calls=["submit_flight_claim"],
            expected_agent_sequence=["Claims Agent"],
            min_steps=2,
            max_steps=5,
        ),
    ),
    (
        "Lost baggage on flight FL789 today, need compensation",
        ExpectedBehavior(
            final_output_validator=lambda x: all(
                term.lower() in x.lower() for term in ["fl789", "clm"]
            ),
            expected_tool_calls=["submit_flight_claim"],
            expected_agent_sequence=["Claims Agent"],
            min_steps=2,
            max_steps=5,
        ),
    ),
]

FAQ_AGENT_TESTS = [
    (
        "What is your baggage allowance policy?",
        ExpectedBehavior(
            final_output_validator=lambda x: "8 kg" in x.lower(),
            expected_tool_calls=["get_faq"],
            expected_agent_sequence=["FAQ Agent"],
            min_steps=2,
            max_steps=3,
        ),
    ),
    (
        "How long do refunds take to process?",
        ExpectedBehavior(
            final_output_validator=lambda x: "5-7 days" in x.lower(),
            expected_tool_calls=["get_faq"],
            expected_agent_sequence=["FAQ Agent"],
            min_steps=2,
            max_steps=3,
        ),
    ),
    (
        "Tell me about the checked baggage limit",
        ExpectedBehavior(
            final_output_validator=lambda x: "23 kg" in x.lower(),
            expected_tool_calls=["get_faq"],
            expected_agent_sequence=["FAQ Agent"],
            min_steps=2,
            max_steps=3,
        ),
    ),
]

# Multi-agent System Tests
MULTI_AGENT_TESTS = {
    "Booking Flows": [
        (
            "I am Din. Book a one way flight to Ireland tomorrow. My phone number is 1234567890.",
            ExpectedBehavior(
                final_output_validator=lambda x: all(
                    term.lower() in x.lower() for term in ["ireland", "flight"]
                ),
                expected_tool_calls=["search_flights"],
                expected_agent_sequence=[
                    "Triage Agent",
                    "Booking Router Agent",
                    "Flight Booking Agent",
                ],
                min_steps=3,
                max_steps=6,
            ),
        ),
        (
            "I am Ana. Book a hotel in Tokyo for 3 nights. My phone number is 1234567890. The checkin date is 2025-05-01",
            ExpectedBehavior(
                final_output_validator=lambda x: all(
                    term.lower() in x.lower() for term in ["tokyo", "hotel"]
                ),
                expected_tool_calls=["search_hotels"],
                expected_agent_sequence=[
                    "Triage Agent",
                    "Booking Router Agent",
                    "Hotel Booking Agent",
                ],
                min_steps=3,
                max_steps=6,
            ),
        ),
        (
            "Book a flight from NYC to LA next week",
            ExpectedBehavior(
                final_output_validator=lambda x: all(
                    term.lower() in x.lower() for term in ["nyc", "la", "flight"]
                ),
                expected_tool_calls=["search_flights"],
                expected_agent_sequence=[
                    "Triage Agent",
                    "Booking Router Agent",
                    "Flight Booking Agent",
                ],
                min_steps=3,
                max_steps=6,
            ),
        ),
    ],
    "Customer Service": [
        (
            "Need to submit a claim for a cancelled flight FL456",
            ExpectedBehavior(
                final_output_validator=lambda x: all(
                    term.lower() in x.lower() for term in ["fl456", "clm"]
                ),
                expected_tool_calls=["submit_flight_claim"],
                expected_agent_sequence=["Triage Agent", "Claims Agent"],
                min_steps=3,
                max_steps=6,
            ),
        ),
        (
            "Lost luggage claim for flight FL789",
            ExpectedBehavior(
                final_output_validator=lambda x: all(
                    term.lower() in x.lower() for term in ["fl789", "clm"]
                ),
                expected_tool_calls=["submit_flight_claim"],
                expected_agent_sequence=["Triage Agent", "Claims Agent"],
                min_steps=3,
                max_steps=6,
            ),
        ),
        (
            "What's the policy on refunds?",
            ExpectedBehavior(
                final_output_validator=lambda x: "5-7 days" in x.lower(),
                expected_tool_calls=["get_faq"],
                expected_agent_sequence=["Triage Agent", "FAQ Agent"],
                min_steps=2,
                max_steps=4,
            ),
        ),
    ],
    "Complex Routing": [
        (
            "I need a hotel in Paris and information about baggage limits",
            ExpectedBehavior(
                final_output_validator=lambda x: all(
                    term.lower() in x.lower() for term in ["paris", "hotel", "kg"]
                ),
                expected_tool_calls=["search_hotels", "get_faq"],
                expected_agent_sequence=[
                    "Triage Agent",
                    "Booking Router Agent",
                    "Hotel Booking Agent",
                    "FAQ Agent",
                ],
                min_steps=4,
                max_steps=8,
            ),
        ),
        (
            "Need to book a flight and file a claim for my previous flight FL123",
            ExpectedBehavior(
                final_output_validator=lambda x: all(
                    term.lower() in x.lower() for term in ["flight", "fl123", "clm"]
                ),
                expected_tool_calls=["search_flights", "submit_flight_claim"],
                expected_agent_sequence=[
                    "Triage Agent",
                    "Booking Router Agent",
                    "Flight Booking Agent",
                    "Claims Agent",
                ],
                min_steps=4,
                max_steps=8,
            ),
        ),
        (
            "What's the refund policy and baggage allowance?",
            ExpectedBehavior(
                final_output_validator=lambda x: all(
                    term.lower() in x.lower() for term in ["5-7 days", "kg"]
                ),
                expected_tool_calls=["get_faq", "get_faq"],
                expected_agent_sequence=["Triage Agent", "FAQ Agent"],
                min_steps=3,
                max_steps=5,
            ),
        ),
    ],
}

# First, define the instruction variants
AGENT_INSTRUCTIONS = {
    "flight": {
        "standard": (
            "1. greet user\n"
            "2. use search_flights to fetch options\n"
            "3. ask user to choose one\n"
            "4. confirm booking and give ref\n"
            "5. offer further help"
        ),
        "concierge": (
            "1. warmly welcome the traveler\n"
            "2. gather travel preferences (class, timing)\n"
            "3. use search_flights for personalized options\n"
            "4. provide detailed flight comparisons\n"
            "5. assist with selection and confirm\n"
            "6. offer additional travel tips"
        ),
    },
    "hotel": {
        "standard": (
            "1. greet user\n"
            "2. use search_hotels to fetch options\n"
            "3. ask user to choose one\n"
            "4. confirm booking and give ref\n"
            "5. offer further help"
        ),
        "luxury": (
            "1. provide VIP welcome\n"
            "2. understand preferences (amenities, location)\n"
            "3. use search_hotels for luxury options\n"
            "4. detail unique features of each property\n"
            "5. handle booking with premium care\n"
            "6. offer concierge services"
        ),
    },
    "claims": {
        "standard": (
            "1. greet user\n"
            "2. ask flight number\n"
            "3. ask flight date\n"
            "4. ask for issue description\n"
            "5. ask for supporting docs\n"
            "6. use submit_flight_claim\n"
            "7. confirm claim ref"
        ),
        "empathetic": (
            "1. express understanding of situation\n"
            "2. gently gather incident details\n"
            "3. acknowledge inconvenience\n"
            "4. collect flight number and date\n"
            "5. guide through documentation\n"
            "6. use submit_flight_claim\n"
            "7. provide clear next steps\n"
            "8. offer additional support"
        ),
    },
    "faq": {
        "standard": (
            "1. greet user\n"
            "2. ask what info they need\n"
            "3. call get_faq\n"
            "4. give answer\n"
            "5. offer further help"
        ),
        "educational": (
            "1. welcome and establish context\n"
            "2. understand specific query\n"
            "3. call get_faq\n"
            "4. explain policy with examples\n"
            "5. anticipate follow-up questions\n"
            "6. provide related information\n"
            "7. ensure full understanding"
        ),
    },
    "booking_router": {
        "standard": (
            "1. greet user\n"
            "2. ask name, phone, trip type (flight/hotel), origin/dest & dates\n"
            "3. if flight → hand off to flight_booking_agent\n"
            "4. if hotel → hand off to hotel_booking_agent\n"
            "5. confirm hand‑off"
        )
    },
    "triage": {
        "standard": (
            "1. greet user\n"
            "2. decide: booking, claim, or info\n"
            "3. booking → booking_router_agent\n"
            "4. claim → claims_agent\n"
            "5. info → faq_agent"
        )
    },
}


def create_agents(instruction_style="standard"):
    """
    Create all agents with specified instruction style.
    Args:
        instruction_style: Either "standard" or "enhanced" ("enhanced" uses concierge/luxury/empathetic/educational variants)
    Returns:
        Tuple containing all agents in order: (flight, hotel, claims, faq, booking_router, triage)
    """
    from agents import Agent

    from _4_multi_agents import (
        get_faq,
        search_flights,
        search_hotels,
        submit_flight_claim,
    )

    # For booking_router and triage, always use standard as they don't have variants
    style = (
        "standard"
        if instruction_style == "standard"
        else {
            "flight": "concierge",
            "hotel": "luxury",
            "claims": "empathetic",
            "faq": "educational",
        }
    )

    # Create base agents
    flight_agent = Agent(
        name="Flight Booking Agent",
        instructions=AGENT_INSTRUCTIONS["flight"][
            style if isinstance(style, str) else style["flight"]
        ],
        tools=[search_flights],
        model="gpt-4o-mini",
    )

    hotel_agent = Agent(
        name="Hotel Booking Agent",
        instructions=AGENT_INSTRUCTIONS["hotel"][
            style if isinstance(style, str) else style["hotel"]
        ],
        tools=[search_hotels],
        model="gpt-4o-mini",
    )

    claims_agent = Agent(
        name="Claims Agent",
        instructions=AGENT_INSTRUCTIONS["claims"][
            style if isinstance(style, str) else style["claims"]
        ],
        tools=[submit_flight_claim],
        model="gpt-4o-mini",
    )

    faq_agent = Agent(
        name="FAQ Agent",
        instructions=AGENT_INSTRUCTIONS["faq"][
            style if isinstance(style, str) else style["faq"]
        ],
        tools=[get_faq],
        model="gpt-4o-mini",
    )

    # Create routing agents
    booking_router_agent = Agent(
        name="Booking Router Agent",
        instructions=AGENT_INSTRUCTIONS["booking_router"]["standard"],
        handoffs=[flight_agent, hotel_agent],
        model="gpt-4o-mini",
    )

    triage_agent = Agent(
        name="Triage Agent",
        instructions=AGENT_INSTRUCTIONS["triage"]["standard"],
        handoffs=[booking_router_agent, claims_agent, faq_agent],
        model="gpt-4o-mini",
    )

    return (
        flight_agent,
        hotel_agent,
        claims_agent,
        faq_agent,
        booking_router_agent,
        triage_agent,
    )
