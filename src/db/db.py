from utils.user_info import UserInfo


class Database:
    def __init__(self):
        # connection, cursor
        pass

    def create_users_table(self):
        pass

    def add_user(self, user_info: UserInfo):
        # add new user
        print(user_info)
        pass

    def close(self):
        # close cursor and conn
        pass
