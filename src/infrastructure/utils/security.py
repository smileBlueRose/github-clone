from typing import Any, Dict, List, Optional, Tuple, Union

import bleach  # type: ignore
from flask import Request, abort

JsonValue = Union[Dict[str, Any], List[Any], str, int, float, bool, None]


def sanitize_html_input(text: str) -> str:
    """
    Strips all HTML tags and attributes from a string.
    """
    if not text:
        return ""
    return str(bleach.clean(text, tags=[], attributes={}, strip=True))


def get_sanitized_data(request: Request, max_depth: int = 10) -> Tuple[Dict[str, str], Dict[str, Any]]:
    """
    Extracts and sanitizes query parameters and JSON body from a request.

    Args:
        request: The incoming Flask Request object.
        max_depth: The maximum allowed nesting level for JSON to prevent DoS.

    Returns:
        Tuple[Dict[str, str], Dict[str, Any]]:
            - A dictionary of sanitized query parameters.
            - A dictionary of sanitized JSON data.
    """

    def walk_and_sanitize(obj: JsonValue, depth: int = 0) -> JsonValue:
        """
        Recursively traverses and cleans dictionaries, lists, and strings.
        """
        if depth > max_depth:
            abort(400, description="Payload structure is too deep")

        if isinstance(obj, dict):
            return {sanitize_html_input(str(k)): walk_and_sanitize(v, depth + 1) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [walk_and_sanitize(i, depth + 1) for i in obj]
        elif isinstance(obj, str):
            return sanitize_html_input(obj)

        # Return primitives (int, float, bool, None) as they are
        return obj

    sanitized_query: Dict[str, str] = {}
    if request.args:
        for key, value in request.args.items():
            clean_key: str = sanitize_html_input(str(key))
            clean_value: str = sanitize_html_input(str(value))
            sanitized_query[clean_key] = clean_value

    sanitized_json: Dict[str, Any] = {}
    if request.is_json:
        raw_json: Optional[Any] = request.get_json(silent=True)

        if raw_json is not None:
            processed: JsonValue = walk_and_sanitize(raw_json)
            if isinstance(processed, dict):
                sanitized_json = processed
            elif isinstance(processed, list):
                sanitized_json = {"_data": processed}

    return sanitized_query, sanitized_json
