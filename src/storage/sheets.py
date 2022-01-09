from dataclasses import asdict

import pygsheets

from utils.user_info import UserInfo
from utils.daily_results import DailyResults
from typing import List


class SheetsManager:
    def __init__(self, path):
        gc = pygsheets.authorize(service_file=path)
        sheet = gc.open('Пользователи')
        self.wks = sheet.sheet1
        self.users_count = self.get_users_count()

    def get_users_count(self) -> int:
        cells = self.wks.get_all_values(include_tailing_empty_rows=False,
                                        include_tailing_empty=False, returnas='matrix')
        return len(cells)

    def add_user(self, user_info: UserInfo) -> None:
        user_info.interests = ", ".join(user_info.interests)
        self.wks = self.wks.insert_rows(self.users_count, number=1, values=list(asdict(user_info).values()))
        self.users_count += 1
        pass

    def add_daily_results(self, results: DailyResults) -> None:
        pass

    def get_today_tasks(self) -> List[str]:
        return ['Task 1', 'Task 2', 'Task 3', 'Task 4']

    def get_today_tips(self) -> List[str]:
        pass

    def check_billing(self, user_id: int) -> bool:
        pass
