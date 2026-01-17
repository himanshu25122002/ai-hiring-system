from pydantic import BaseModel, Field
from typing import List, Literal

class JobInput(BaseModel):
    role: str = Field(..., example="Backend Engineer")
    required_skills: List[str] = Field(..., example=["Python", "FastAPI", "SQL"])
    experience_level: Literal["fresher", "junior", "mid", "senior"]
    culture_traits: List[str] = Field(default=[])
