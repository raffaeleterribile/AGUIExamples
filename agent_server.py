"""AG-UI server with backend tool rendering."""

import os
from typing import Annotated, Any

from agent_framework import Agent, tool
from agent_framework.openai import OpenAIChatCompletionClient
from agent_framework_ag_ui import add_agent_framework_fastapi_endpoint
from azure.identity import AzureCliCredential
from fastapi import FastAPI
from pydantic import Field


# Define function tools
@tool
def get_weather(
    location: Annotated[str, Field(description="The city")],
) -> str:
    """Get the current weather for a location."""
    # Simulated weather data
    return f"The weather in {location} is sunny with a temperature of 22°C."


@tool
def search_restaurants(
    location: Annotated[str, Field(description="The city to search in")],
    cuisine: Annotated[str, Field(description="Type of cuisine")] = "any",
) -> dict[str, Any]:
    """Search for restaurants in a location."""
    # Simulated restaurant data
    return {
        "location": location,
        "cuisine": cuisine,
        "results": [
            {"name": "The Golden Fork", "rating": 4.5, "price": "$$"},
            {"name": "Bella Italia", "rating": 4.2, "price": "$$$"},
            {"name": "Spice Garden", "rating": 4.7, "price": "$$"},
        ],
    }


# Read required configuration
endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
deployment_name = os.environ.get("AZURE_OPENAI_CHAT_COMPLETION_MODEL")

if not endpoint:
    raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")
if not deployment_name:
    raise ValueError("AZURE_OPENAI_CHAT_COMPLETION_MODEL environment variable is required")

chat_client = OpenAIChatCompletionClient(
    model=deployment_name,
    azure_endpoint=endpoint,
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    credential=AzureCliCredential(),
)

# Create agent with tools
agent = Agent(
    name="TravelAssistant",
    instructions="You are a helpful travel assistant. Use the available tools to help users plan their trips.",
    client=chat_client,
    tools=[get_weather, search_restaurants],
)

# Create FastAPI app
app = FastAPI(title="AG-UI Travel Assistant")
add_agent_framework_fastapi_endpoint(app, agent, "/")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8888)
