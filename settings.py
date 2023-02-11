from os import getenv

ACCEPTABLE_LOG_LEVELS = ("debug", "info", "warning", "error", "critical")
LOG_LEVEL = getenv("LOG_LEVEL", "warning").lower()
if LOG_LEVEL not in ACCEPTABLE_LOG_LEVELS:
    raise ValueError(f"Environment variable LOG_LEVEL must be one of {repr(ACCEPTABLE_LOG_LEVELS)}.")
