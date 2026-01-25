from pathlib import Path

import yaml  # type: ignore

from domain.services.policy_service import PolicyEngine
from domain.value_objects.policy import Policy


class PolicyLoader:
    @staticmethod
    def load_from_yaml(file_path: Path) -> PolicyEngine:
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)

        policies = [Policy(**p) for p in data.get("policies", [])]

        return PolicyEngine(policies)
