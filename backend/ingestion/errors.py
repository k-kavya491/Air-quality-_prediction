class ExternalAPIError(Exception):
    """Raised when an outside data provider fails. The message is safe to show users."""