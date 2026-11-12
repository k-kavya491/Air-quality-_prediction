import requests

from ingestion.errors import ExternalAPIError


def get_json(provider, url, params=None, headers=None, timeout=15, bad_request_message=None):
    """GET a JSON response. Failures become ExternalAPIError with a message that
    is safe to show users (it never contains the URL, so keys can't leak)."""
    try:
        r = requests.get(url, params=params, headers=headers, timeout=timeout)
    except requests.Timeout:
        raise ExternalAPIError(f"{provider} timed out")
    except requests.RequestException:
        raise ExternalAPIError(f"{provider} is unreachable")

    if r.status_code in (401, 403):
        raise ExternalAPIError(f"{provider} rejected the API key")
    if r.status_code == 429:
        raise ExternalAPIError(f"{provider} rate limit reached, try again later")
    if r.status_code == 400 and bad_request_message:
        raise ExternalAPIError(bad_request_message)
    if r.status_code != 200:
        raise ExternalAPIError(f"{provider} returned an error ({r.status_code})")
    try:
        return r.json()
    except ValueError:
        raise ExternalAPIError(f"{provider} returned an unreadable response")