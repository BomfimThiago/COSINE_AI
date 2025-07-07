import os
from langchain_openai import ChatOpenAI

def get_llm():
    """
    Returns a configured ChatOpenAI instance using env vars.
    """
    return ChatOpenAI(
        temperature=0,
        model_name="gpt-3.5-turbo-0125",
        openai_api_key=os.environ.get("OPENAI_API_KEY")
    )