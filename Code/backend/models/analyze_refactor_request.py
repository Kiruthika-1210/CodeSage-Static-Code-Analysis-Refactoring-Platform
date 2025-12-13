from pydantic import BaseModel

class AnalyzeRefactorRequest(BaseModel):
    code: str
    session_id: str
