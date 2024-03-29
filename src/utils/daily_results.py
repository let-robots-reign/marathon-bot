from dataclasses import dataclass


@dataclass
class DailyResults:
    user_id: int
    is_completed: str
    completed_task: str
    feelings_physical: str
    feelings_emotional: str
    feelings_fear: str
    link: str
