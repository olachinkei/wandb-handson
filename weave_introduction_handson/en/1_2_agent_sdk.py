"""
1_2: OpenAI Agent SDK - Building agents

What you'll learn in this script:
================================
1. Basic usage of OpenAI Agent SDK
2. Defining tools with function_tool
3. Tracing with WeaveTracingProcessor

Where to look after running:
================================
- Traces tab: Agent execution and tool calls
- Code tab: Tracked functions and Agent SDK integration
"""

import os
import asyncio
from dotenv import load_dotenv
import weave
from agents import Agent, Runner, function_tool, set_trace_processors
from weave.integrations.openai_agents.openai_agents import WeaveTracingProcessor

# Load environment variables
load_dotenv()

# Initialize Weave
# Initialize with weave.init("entity/project")
weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")

# Set WeaveTracingProcessor to enable tracing
set_trace_processors([WeaveTracingProcessor()])


# =============================================================================
# 1. Agent with Multiple Tools
# =============================================================================
print("\n" + "=" * 60)
print("1. Agent with Multiple Tools")
print("=" * 60)


@function_tool
def search_database(query: str) -> list:
    """Search the database for relevant information."""
    # Mock database search
    return [
        {"id": 1, "title": f"Result 1 for: {query}", "score": 0.95},
        {"id": 2, "title": f"Result 2 for: {query}", "score": 0.87},
    ]


@function_tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to a recipient."""
    # Mock email sending
    return f"Email sent to {to} with subject: {subject}"


research_agent = Agent(
    name="ResearchAssistant",
    instructions="""You are a research assistant. You can:
    - Search the database for information
    - Send emails with findings
    Help the user with their research tasks.""",
    tools=[search_database, send_email],
)


@weave.op()
async def run_research(input: str) -> str:
    """Run Research Agent"""
    response = await Runner.run(research_agent, input)
    return response.final_output


result = asyncio.run(run_research("Search for information about machine learning and email the results to user@example.com"))
print(f"Result: {result[:100]}...")


print("\n" + "=" * 60)
print("Agent SDK Demo Complete!")
print("=" * 60)
print("""
Summary:
- Define Agent SDK tools with @function_tool
- Create an agent with Agent() and run it with Runner.run()
- Record agent execution in Weave with WeaveTracingProcessor

Check in Weave UI:
- Use the Traces tab to inspect agent execution and tool calls
- Use Inputs/Outputs to inspect each tool call
""")
