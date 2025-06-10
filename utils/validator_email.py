import re

class MailHelper:
    @staticmethod
    def is_valid_email(email: str) -> bool:
        if not email or email.strip() == "":
            return False

        pattern = r"^\w+([\-+.'']\w+)*@\w+([\-\.]\w+)*\.\w+([\-\.]\w+)*$"
        return re.match(pattern, email) is not None
