from pydantic import BaseModel
from typing import Optional, List, Dict

class AIRequest(BaseModel):
    code: str
    issues: Optional[List] = None
    complexity: Optional[Dict] = None
    quality: Optional[Dict] = None
