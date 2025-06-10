from dataclasses import dataclass
from typing import List, Optional


@dataclass
class EmailAgentRequest:
    from_email: str
    body: str
    cc: Optional[List[str]] = None
    cco: Optional[List[str]] = None
    # attachment: Optional[str] = None  # aún no usado