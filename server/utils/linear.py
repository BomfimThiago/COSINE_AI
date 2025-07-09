import os

def get_linear_api_key():
    """
    Returns the Linear API key from environment variables, supporting multiple possible variable names.
    Priority: LINEAR_SECRET_KEY > LINEAR_DEVELOPER_TOKEN > LINEAR_API_KEY
    """
    key = (
        os.environ.get("LINEAR_DEVELOPER_TOKEN")
    )
    masked = (key[-4:] if key else None)
    print(f"[Linear] get_linear_api_key called. Key ends with: {masked}")
    return key

def get_linear_api_url():
    print("[Linear] get_linear_api_url called.")
    return "https://api.linear.app/graphql" 