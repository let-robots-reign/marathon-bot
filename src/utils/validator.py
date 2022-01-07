import re

EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

class Validator:
    @staticmethod
    def validate_digit(text: str) -> bool:
        return text.isdigit() and 0 <= int(text) < 10

    @staticmethod
    def validate_email(email: str) -> bool:
        return re.fullmatch(EMAIL_REGEX, email)
