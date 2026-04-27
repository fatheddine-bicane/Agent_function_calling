from datetime import datetime
import zoneinfo

def fn_get_current_time(timezone: str) -> str:
    """
    Retrieves the current local time and date for a specific timezone.
    Expects standard IANA timezone database names (e.g., 'America/New_York', 'Europe/Paris').
    """
    try:
        # Initialize the timezone object
        tz = zoneinfo.ZoneInfo(timezone)

        # Retrieve the current time, localized to the requested timezone
        current_time = datetime.now(tz)

        # Format the time into a clean, human-readable string
        # Example format: 2026-04-26 23:12:34 CET
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S %Z")

        return formatted_time

    except zoneinfo.ZoneInfoNotFoundError:
        return f"Error: The timezone '{timezone}' is invalid. Please use an IANA timezone name (e.g., 'UTC', 'Asia/Tokyo')."
    except Exception as e:
        return f"An unexpected error occurred: {e}"
