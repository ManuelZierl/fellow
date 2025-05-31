from typing import Dict, Type

from fellow.clients.Client import Client
from fellow.clients.GeminiClient import GeminiClient
from fellow.clients.OpenAIClient import OpenAIClient

ALL_CLIENTS: Dict[str, Type[Client]] = {"openai": OpenAIClient, "gemini": GeminiClient}
