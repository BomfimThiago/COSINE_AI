import os
from langchain_openai import ChatOpenAI

def get_llm():
    """
    Returns a configured ChatOpenAI instance using env vars.
    """
    return ChatOpenAI(
        temperature=0,
        model_name="gpt-4o-mini",
        openai_api_key=os.environ.get("OPENAI_API_KEY")
    )

def get_github_token():
    """
    Returns the GitHub API token from environment variables.
    """
    return os.environ.get("GITHUB_TOKEN")