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
        self.wks_billing = sheet.worksheet('index', 2)
        self.wks_info = sheet.worksheet('index', 3)
        self.users_count = self.get_count(self.wks_users)
        self.daily_results_count = self.get_count(self.wks_results)

    @staticmethod
    def get_count(wks) -> int:
        cells = wks.get_all_values(include_tailing_empty_rows=False,
                                   include_tailing_empty=False, returnas='matrix')
        return len(cells)

    def add_user(self, user_info: UserInfo) -> None:
        user_info.interests = ", ".join(user_info.interests)
        self.wks_users = self.wks_users.insert_rows(self.users_count, number=1,
                                                    values=list(asdict(user_info).values()))
        self.users_count += 1

    def add_daily_results(self, results: DailyResults) -> None:
        self.wks_results = self.wks_results.insert_rows(self.daily_results_count, number=1,
                                                        values=list(asdict(results).values()))
        self.daily_results_count += 1

    def __get_column_for_date(self, date: str) -> List[str]:
        dates = self.wks_info.get_row(1, include_tailing_empty=False)
        col_index = dates.index(date)
        col = self.wks_info.get_col(col_index + 1, include_tailing_empty=False)
        return col

    def get_topic_for_date(self, date: str) -> str:
        return self.__get_column_for_date(date)[1]

    def get_tasks_for_date(self, date: str) -> List[str]:
        return self.__get_column_for_date(date)[3].split('\n')[1:]

    def get_tips_for_date(self, date: str) -> List[str]:
        return self.__get_column_for_date(date)[2].split('\n')

    def check_billing(self, user_id: int) -> bool:
        pass
