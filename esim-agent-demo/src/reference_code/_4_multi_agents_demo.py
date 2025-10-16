import asyncio

import weave
from agents import Agent, Runner, function_tool, set_trace_processors
from openai import OpenAI
import config

from weave.integrations.openai_agents.openai_agents import WeaveTracingProcessor
set_trace_processors([WeaveTracingProcessor()])

weave.init(project_name=config.WEAVE_PROJECT)


@function_tool
def search_flights(origin: str, destination: str, date: str):
    return f"Flights {origin}->{destination} on {date}: FL123, FL456"


@function_tool
def search_hotels(city: str, checkin: str, nights: int):
    return f"Hotels in {city} from {checkin} for {nights} nights: Hotel Foo, Hotel Bar"


@function_tool
def submit_flight_claim(flight_number: str, date: str, issue: str):
    return f"Claim submitted for {flight_number} on {date} ({issue}). Ref CLM‑0001"


@function_tool
def get_faq(topic: str):
    data = {
        "baggage": "Carry‑on 8 kg, checked 23 kg.",
        "refund": "Refunds processed in 5‑7 days.",
    }
    return data.get(topic.lower(), "No FAQ available for that topic.")


flight_booking_agent = Agent(
    name="Flight Booking Agent",
    instructions=(
        "1. greet user\n"
        "2. use search_flights to fetch options\n"
        "3. ask user to choose one\n"
        "4. confirm booking and give ref\n"
        "5. offer further help"
    ),
    tools=[search_flights],
    model="gpt-4.1",
)

hotel_booking_agent = Agent(
    name="Hotel Booking Agent",
    instructions=(
        "1. greet user\n"
        "2. use search_hotels to fetch options\n"
        "3. ask user to choose one\n"
        "4. confirm booking and give ref\n"
        "5. offer further help"
    ),
    tools=[search_hotels],
    model="gpt-4.1",
)

claims_agent = Agent(
    name="Claims Agent",
    instructions=(
        "1. greet user\n"
        "2. ask flight number\n"
        "3. ask flight date\n"
        "4. ask for issue description\n"
        "5. ask for supporting docs\n"
        "6. use submit_flight_claim\n"
        "7. confirm claim ref"
    ),
    tools=[submit_flight_claim],
    model="gpt-4.1",
)

faq_agent = Agent(
    name="FAQ Agent",
    instructions=(
        "1. greet user\n"
        "2. ask what info they need\n"
        "3. call get_faq\n"
        "4. give answer\n"
        "5. offer further help"
    ),
    tools=[get_faq],
    model="gpt-4.1",
)


booking_router_agent = Agent(
    name="Booking Router Agent",
    instructions=(
        "1. greet user\n"
        "2. ask name, phone, trip type (flight/hotel), origin/dest & dates\n"
        "3. if flight → hand off to flight_booking_agent\n"
        "4. if hotel → hand off to hotel_booking_agent\n"
        "5. confirm hand‑off"
    ),
    handoffs=[flight_booking_agent, hotel_booking_agent],
    model="gpt-4.1",
)


triage_agent = Agent(
    name="Triage Agent",
    instructions=(
        "1. greet user\n"
        "2. decide: booking, claim, or info\n"
        "3. booking → booking_router_agent\n"
        "4. claim → claims_agent\n"
        "5. info → faq_agent"
    ),
    handoffs=[booking_router_agent, claims_agent, faq_agent],
    model="gpt-4.1",
)


@weave.op()
async def run_agent(prompt: str):
    response = await Runner.run(triage_agent, prompt)
    return response.final_output


@weave.op()
async def multi_agents():
    previous_response_id = None
    cur_agent = triage_agent
    while True:
        user_in = input("> ")
        response = await Runner.run(
            cur_agent, user_in, previous_response_id=previous_response_id
        )
        previous_response_id = response.last_response_id
        cur_agent = response.last_agent
        print(f"[{cur_agent.name}] {response.final_output}")


if __name__ == "__main__":
    asyncio.run(multi_agents())
