from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class RefactorRequest(BaseModel):
    code : str
    issues : Optional[List[Dict[str, Any]]] = None