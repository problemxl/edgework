import re


def validate_season_format(season: str) -> int:
    """
    Validate a season string and convert it to the NHL integer format.

    This is the single shared season-normalization helper; clients and models
    should reuse it instead of inlining ``YYYY-YYYY`` conversions.

    Args:
        season (str): Season string in format "YYYY-YYYY" (e.g., "2023-2024")

    Returns:
        int: Season as integer in format YYYYYYYY (e.g., 20232024)

    Raises:
        ValueError: If season format is invalid
    """
    if not isinstance(season, str):
        raise ValueError("Invalid season format. Expected 'YYYY-YYYY'")

    if not re.match(r"^\d{4}-\d{4}$", season):
        raise ValueError("Invalid season format. Expected 'YYYY-YYYY'")

    try:
        first_year_str, second_year_str = season.split("-")
        first_year = int(first_year_str)
        second_year = int(second_year_str)
    except ValueError:
        raise ValueError("Invalid season format. Expected 'YYYY-YYYY'")

    if second_year != first_year + 1:
        raise ValueError("Invalid season format. Expected 'YYYY-YYYY'")

    return first_year * 10000 + second_year


def camel_to_snake(name):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def dict_camel_to_snake(data):
    if isinstance(data, dict):
        new_dict = {}
        for k, v in data.items():
            new_key = camel_to_snake(k)
            new_dict[new_key] = (
                dict_camel_to_snake(v) if isinstance(v, (dict, list)) else v
            )
        return new_dict
    elif isinstance(data, list):
        return [dict_camel_to_snake(item) for item in data]
    else:
        return data
