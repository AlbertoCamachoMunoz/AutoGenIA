from application.enums.status_code import StatusCode

class PlannerAppResponse:
    def __init__(self, content: str, status: StatusCode, message: str = "OK"):
        self.content = content
        self.status = status
        self.message = message