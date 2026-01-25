from enum import Enum
from typing import Dict, List, Any
from pydantic import BaseModel, Field


class PolicyEffect(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"


class Policy(BaseModel):
    name: str
    action: str
    effect: PolicyEffect
    priority: int = Field(ge=0, le=1000)
    subject_rules: Dict[str, Any] = Field(default_factory=dict)
    resource_rules: Dict[str, Any] = Field(default_factory=dict)
    conditions: List[str] = Field(default_factory=list)
