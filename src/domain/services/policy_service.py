from typing import Any, Dict, List

from domain.value_objects.policy import ConditionOperator, ConditionVO, Policy, PolicyEffect


class PolicyEngine:
    def __init__(self, policies: List[Policy]):
        self._policies = sorted(policies, key=lambda x: x.priority, reverse=True)

    def can(self, action: str, subject: Dict[str, Any], resource: Dict[str, Any]) -> bool:
        context = {"subject": subject, "resource": resource}

        for policy in self._policies:
            if policy.action != action:
                continue

            if not self._match_dict(policy.subject_rules, subject):
                continue

            if not self._match_dict(policy.resource_rules, resource):
                continue

            if not self._eval_conditions(policy.conditions, context):
                continue

            return policy.effect == PolicyEffect.ALLOW

        return False  # Default Deny

    def _match_dict(self, rules: Dict[str, Any], data: Dict[str, Any]) -> bool:
        return all(data.get(k) == v for k, v in rules.items())

    def _eval_conditions(self, conditions: List[ConditionVO], context: Dict[str, Any]) -> bool:
        for condition in conditions:
            sub_val = context["subject"].get(condition.subject_field)
            res_val = context["resource"].get(condition.resource_field)

            if condition.operator == ConditionOperator.EQUALS:
                if not (sub_val == res_val):
                    return False

            elif condition.operator == ConditionOperator.NOT_EQUALS:
                if not (sub_val != res_val):
                    return False

        return True
