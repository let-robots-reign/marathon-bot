from utils.user_info import UserInfo
from typing import List


class SheetsManager:
    def __init__(self):
        pass

    def create_users_table(self) -> None:
        pass

    def add_user(self, user_info: UserInfo) -> None:
        # add new user
        print(user_info)
        pass

    def add_daily_results(self) -> None:
        pass

    def get_today_tasks(self) -> List[str]:
        return ['Task 1', 'Task 2', 'Task 3', 'Task 4']

    def check_billing(self, user_id: int) -> bool:
        pass
