from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class PolicyEffect(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"


class ConditionOperator(str, Enum):
    EQUALS = "=="
    NOT_EQUALS = "!="


class ConditionVO(BaseModel):
    subject_field: str
    operator: ConditionOperator
    resource_field: str


class Policy(BaseModel):
    name: str
    action: str
    effect: PolicyEffect
    priority: int = Field(ge=0, le=1000)
    subject_rules: Dict[str, Any] = Field(default_factory=dict)
    resource_rules: Dict[str, Any] = Field(default_factory=dict)
    conditions: List[ConditionVO] = Field(default_factory=list)
