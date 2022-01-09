from dataclasses import asdict

import pygsheets

from utils.user_info import UserInfo
from utils.daily_results import DailyResults
from typing import List


class SheetsManager:
    def __init__(self, path):
        gc = pygsheets.authorize(service_file=path)
        sheet = gc.open('bot')
        self.wks_users = sheet.worksheet('index', 0)
        self.wks_results = sheet.worksheet('index', 1)
        self.users_count = self.get_count(self.wks_users)
        self.daily_results_count = self.get_count(self.wks_results)

    @staticmethod
    def get_count(wks) -> int:
        cells = wks.get_all_values(include_tailing_empty_rows=False,
                                   include_tailing_empty=False, returnas='matrix')
        return len(cells)

    def add_user(self, user_info: UserInfo) -> None:
        user_info.interests = ", ".join(user_info.interests)
        self.wks_users = self.wks_users.insert_rows(self.users_count, number=1, values=list(asdict(user_info).values()))
        self.users_count += 1

    def add_daily_results(self, results: DailyResults) -> None:
        self.wks_results = self.wks_results.insert_rows(self.daily_results_count, number=1,
                                                        values=list(asdict(results).values()))
        self.daily_results_count += 1

    def get_today_tasks(self) -> List[str]:
        return ['Task 1', 'Task 2', 'Task 3', 'Task 4']

    def get_today_tips(self) -> List[str]:
        pass

    def check_billing(self, user_id: int) -> bool:
        pass
