from typing import Any

from domain.exceptions.common import MissingRequiredFieldException


def get_required_field(data: dict[str, Any], field_name: str) -> Any:
    """:raises MissingRequiredFieldException:"""

    try:
        return data[field_name]
    except KeyError as e:
        raise MissingRequiredFieldException(f"Field '{field_name}' is required") from e
