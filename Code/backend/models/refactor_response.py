from pydantic import BaseModel
from typing import List

class RefactorResponse(BaseModel):
    refactored_code : str
    explanation : str
    test_cases : List[str]