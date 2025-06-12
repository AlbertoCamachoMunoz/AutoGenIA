from application.enums.status_code import StatusCode

class AgentAppRequest:
    def __init__(self, input_data: str, status: StatusCode = StatusCode.SUCCESS, message: str = "OK"):
        self.input_data = input_data
        self.status = status
        self.message = message