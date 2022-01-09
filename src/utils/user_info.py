from dataclasses import dataclass
from typing import List


@dataclass
class UserInfo:
    id: int
    name: str
    surname: str
    phone: str
    email: str
    interests: List[str]
    attend_reason: str
    expectations: str
    feelings_physical: str
    feelings_emotional: str
