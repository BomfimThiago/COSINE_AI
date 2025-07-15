import logging
import requests
import time
import os
import traceback

SLACK_WEBHOOK_URL = os.environ.get("SLACK_ALERT_WEBHOOK")

def log_error(message, extra=None, alert=True):
    """
    Log error in structured way and optionally send alert to Slack.
    """
    logging.basicConfig(level=logging.ERROR)
    error_payload = {
        "level": "ERROR",
        "message": message,
        "extra": extra or {},
    }
    logging.error(error_payload)
    if alert and SLACK_WEBHOOK_URL:
        try:
            slack_payload = {
                "text": f":rotating_light: *Backend Error Alert*\n\n*Message:* {message}\n*Extra:* ```{extra}```"
            }
            requests.post(SLACK_WEBHOOK_URL, json=slack_payload, timeout=5)
        except Exception as e:
            logging.error(f"Failed to send Slack alert: {e}")

def network_guard(max_retries=3, backoff_factor=0.75):
    """
    Decorator to wrap network calls with try/catch, exponential backoff retries (for 429/5xx), and structured logging+alerting.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries <= max_retries:
                try:
                    response = func(*args, **kwargs)
                    # Check for requests.Response object and HTTP error codes
                    if hasattr(response, "status_code") and response.status_code in [429, 500, 502, 503, 504]:
                        raise Exception(f"Received HTTP {response.status_code}: {getattr(response, 'text', '')[:200]}")
                    return response
                except Exception as e:
                    tb = traceback.format_exc()
                    log_error(
                        f"Exception in network call {func.__name__}: {str(e)}",
                        extra={"traceback": tb, "args": args, "kwargs": kwargs},
                        alert=True
                    )
                    if retries < max_retries:
                        sleep_time = backoff_factor * (2 ** retries)
                        time.sleep(sleep_time)
                        retries += 1
                        continue
                    else:
                        raise
        return wrapper
    return decorator