from datetime import datetime


# async def schedule_meeting(
#     attendees: list[str], date: str, time: str, topic: str
# ) -> str:
#     """Schedules a meeting with specified attendees at a given time and date.

#     Args:
#         attendees: List of participant email addresses or names.
#         date: Meeting date in YYYY-MM-DD format (e.g., '2026-07-29').
#         time: Meeting time in HH:MM format (e.g., '15:00').
#         topic: The subject or topic of the meeting.
#     """
#     # Parse strings into actual datetime objects INSIDE the function if needed
#     parsed_date = datetime.strptime(date, "%Y-%m-%d").date()

    

#     return f"Meeting successfully scheduled on {parsed_date} at {time} about '{topic}' with {len(attendees)} attendees."

async def schedule_meeting(
    attendees: list[str], date: str, time: str, topic: str
) -> str:
    parsed_date = datetime.strptime(date, "%Y-%m-%d").date()

    if "kush" in [a.lower() for a in attendees]:
        raise ValueError("Kush's calendar is not accessible right now.")

    return f"Meeting successfully scheduled on {parsed_date} at {time} about '{topic}' with {len(attendees)} attendees."