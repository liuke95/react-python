import unicodedata
import re


DICT_NORM_ABBREV = {
  "Tp ": ["Tp.", "Tp:"],
  "Tt ": ["Tt.", "Tt:"],
  "Q ": ["Q.", "Q:"],
  "H ": ["H.", "H:"],
  "X ": ["X.", "X:"],
  "P ": ["P.", "P:"],
}

DICT_NORM_CITY_DASH = {
  " Ba Ria - Vung Tau ": [
      "Ba Ria Vung Tau",
      "Ba Ria-Vung Tau",
      "Brvt",
      "Br - Vt"
  ],
  " Phan Rang - Thap Cham ": [
      "Phan Rang Thap Cham",
  ],
  " Thua Thien Hue ": ["Thua Thien - Hue"],
  " Ho Chi Minh ": ["Sai Gon", "Tphcm", "Hcm", "Sg"],
  " Da Nang ": [
      "Quang Nam-Da Nang",
      "Quang Nam - Da Nang",
  ],
}

# ADDRESS_PUNCTUATIONS = ["?", "!", ":", "'"]
ADDRESS_PUNCTUATIONS = ['.', ',', '!', '?', ';', ':', '-', '_', '(', ')', '"', "'"]

SPECIAL_ENDING = r"[g.;,\s]"


def init_cap_words(text: str) -> str:
    """
    Capitalize the first letter of each word in the string.

    Args:
        text (str): Input string.

    Returns:
        str: String with each word capitalized.
    """
    if not isinstance(text, str):
        raise ValueError("The input must be a string")

    return " ".join(word.capitalize() for word in text.split()) if text else text


def remove_accent(text: str) -> str:
    """
    Remove Vietnamese diacritics from the string.

    Args:
        text (str): Input string with diacritics.

    Returns:
        str: String with diacritics removed.
    """
    if not isinstance(text, str):
        raise ValueError("The input must be a string")

    # Normalize Unicode and remove diacritic marks
    text = unicodedata.normalize("NFD", text)
    text = re.sub(r"[\u0300-\u036f]", "", text)

    # Replace accented characters with non-accented versions
    replacements = {
        "a": "àáạảãâầấậẩẫăằắặẳẵ",
        "A": "ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ",
        "e": "èéẹẻẽêềếệểễ",
        "E": "ÈÉẸẺẼÊỀẾỆỂỄ",
        "o": "òóọỏõôồốộổỗơờớợởỡ",
        "O": "ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ",
        "i": "ìíịỉĩ",
        "I": "ÌÍỊỈĨ",
        "u": "ùúụủũưừứựửữ",
        "U": "ƯỪỨỰỬỮÙÚỤỦŨ",
        "y": "ỳýỵỷỹ",
        "Y": "ỲÝỴỶỸ",
        "d": "đ",
        "D": "Đ",
    }

    for non_accent, accents in replacements.items():
        for accent in accents:
            text = text.replace(accent, non_accent)

    return text


def clean_dash_address(text: str, dict_norm_city_dash: dict) -> str:
    """
    Standardize dash-separated elements in an address by replacing synonyms.

    Args:
        text (str): Input address string.
        dict_norm_city_dash (dict): Dictionary containing word replacements.

    Returns:
        str: Standardized address string.
    """
    if not isinstance(text, str):
        raise ValueError("Input text must be a string")

    if not isinstance(dict_norm_city_dash, dict):
        raise ValueError("DICT_NORM_CITY_DASH must be a dictionary")

    for key, synonyms in dict_norm_city_dash.items():
        pattern = r"\b|\b".join(map(re.escape, synonyms))
        text = re.sub(pattern, key, text, flags=re.IGNORECASE)

    return text


def clean_abbrev_address(text: str, dict_norm_abbrev: dict) -> str:
    """
    Standardize abbreviations in an address by replacing them according to a predefined dictionary.

    Args:
        text (str): Input address string.
        dict_norm_abbrev (dict): Dictionary containing abbreviations and their full forms.

    Returns:
        str: Standardized address string.
    """
    if not isinstance(text, str):
        raise ValueError("Input text must be a string")

    if not isinstance(dict_norm_abbrev, dict):
        raise ValueError("DICT_NORM_ABBREV must be a dictionary")

    for key, synonyms in dict_norm_abbrev.items():
        pattern = r"(" + "|".join(map(re.escape, synonyms)) + r")"

        def replacement(match):
            return key.capitalize()

        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    text = re.sub(r"\s+", " ", text).strip()
    
    return text


def clean_digit_district(text: str) -> str:
    """
    Standardize the district format in an address:
    - Convert "q 1", "Q 1", "quan 1" to "Q1"
    - Remove leading zeros in district numbers (e.g., Q01 -> Q1)

    Args:
        text (str): Input address string.

    Returns:
        str: Standardized address string.
    """
    # Normalize "Quan" (District) to "Q"
    text = re.sub(r"\b(q|quan)\s*(\d+)\b", r"Q\2", text, flags=re.IGNORECASE)

    # Remove leading zeros in district numbers (e.g., Q01 -> Q1, Q002 -> Q2)
    text = re.sub(r"\bQ0+(\d+)\b", r"Q\1", text)

    return text


def clean_digit_ward(text: str) -> str:
    """
    Standardize the ward format in an address:
    - Convert "p 1", "P 1", "phuong 1", "Phuong 1" to "P1"
    - Convert "F1", "f1" to "P1"
    - Remove leading zeros in ward numbers (P01 -> P1)

    Args:
        text (str): Input address string.

    Returns:
        str: Standardized address string.
    """
    # Normalize "Phuong" (Ward) to "P"
    text = re.sub(r"\b(p|phuong)\s*(\d+)\b", r"P\2", text, flags=re.IGNORECASE)

    # Replace "F" or "f" with "P" (e.g., F1 -> P1, f02 -> P2)
    text = re.sub(r"\b[Ff](\d+)\b", r"P\1", text)

    # Remove unnecessary leading zeros (P01 -> P1, P002 -> P2)
    text = re.sub(r"\bP0+(\d+)\b", r"P\1", text)

    return text


def remove_spare_space(text: str) -> str:
    """
    Remove extra spaces in a string.

    - Trim leading and trailing spaces.
    - Convert multiple spaces into a single space.

    Args:
        text (str): Input string.

    Returns:
        str: String with extra spaces removed.
    """
    return re.sub(r'\s+', ' ', text.strip())


def remove_punctuation(text: str, punctuations: list) -> str:
    """
    Remove all punctuation marks listed in `punctuations`.

    - Uses `re.escape()` to avoid issues with special regex characters.
    - Joins punctuation marks into a regex pattern for efficient matching.
    - Replaces all occurrences with an empty string.
    - Finally, normalizes spaces.

    Args:
        text (str): Input string.
        punctuations (list): List of punctuation marks to remove.

    Returns:
        str: String with punctuation removed and spaces normalized.
    """
    if not punctuations:
        return remove_spare_space(text)

    pattern = f"[{''.join(map(re.escape, punctuations))}]"
    text = re.sub(pattern, '', text)

    return remove_spare_space(text)


def add_space_separator(text: str) -> str:
    """
    Standardize spacing by adding appropriate spaces around special characters.

    - Ensures a single space after commas, but no space before them.
    - Converts periods, hyphens, and underscores into spaces.
    - Normalizes multiple spaces.
    - Capitalizes the first letter of each word.

    Args:
        text (str): Input string.

    Returns:
        str: Standardized string with proper spacing and capitalization.
    """
    text = re.sub(r"\s*,\s*", ", ", text)  # Ensure exactly one space after commas
    text = re.sub(r"[._-]", " ", text)  # Replace dots, hyphens, and underscores with spaces
    text = re.sub(r"\s+", " ", text).strip()  # Normalize spaces

    return init_cap_words(text)  # Capitalize first letters of words


def last_index_of_regex(text: str, pattern: str) -> int:
    """
    Find the last occurrence of a regex pattern in a string.

    Args:
        text (str): Input string.
        pattern (str): Regular expression pattern.

    Returns:
        int: The starting index of the last match, or -1 if not found.
    """
    if not pattern:
        return -1

    matches = list(re.finditer(pattern, text))
    return matches[-1].start() if matches else -1


def replace_last_occurrences(target_str: str, substr: str, replacement: str) -> str:
    """
    Replace the last occurrence of a substring in a given string.

    Args:
        target_str (str): Input string.
        substr (str): Substring to replace.
        replacement (str): Replacement string.

    Returns:
        str: Updated string with the last occurrence of `substr` replaced.
    """
    if not substr:
        return target_str

    last_index = target_str.rfind(substr)
    if last_index == -1:
        return target_str

    return target_str[:last_index] + replacement + target_str[last_index + len(substr):]


def clean_full_address(text: str) -> str:
    """
    Standardize an address by handling capitalization, accent removal, district/ward normalization,
    punctuation removal, and space formatting.

    Args:
        text (str): Input address string.

    Returns:
        str: Standardized address.
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string")

    text = init_cap_words(text)
    text = remove_accent(text)
    text = clean_abbrev_address(text, DICT_NORM_ABBREV)
    text = remove_spare_space(text)
    text = clean_digit_district(text)
    text = clean_digit_ward(text)
    text = clean_dash_address(text, DICT_NORM_CITY_DASH)
    text = remove_punctuation(text, ADDRESS_PUNCTUATIONS)
    text = add_space_separator(text)

    text = clean_digit_district(text)
    text = clean_digit_ward(text)

    return text


def parse_address(input_address, db_provinces, db_districts, db_wards, special_ending):
    
    # Preprocess the address
    address = clean_full_address(input_address) + ','

    founded_province = ""
    founded_district = ""
    founded_ward = ""

    choose_word = ""
    largest_index = -1

    # Extract Province/City
    for province, province_data in db_provinces.items():
        for word in province_data['words']:
            # Select the closest component (province, district, ward) from the right of the address
            last_index = address.rfind(word)
            # If two components have the same index, prioritize the longer string
            if (
                (last_index > largest_index) or 
                (
                    (last_index == largest_index) and 
                    (largest_index > -1) and 
                    (len(word) > len(choose_word))
                )
            ):
                founded_province = province
                choose_word = word
                largest_index = last_index

    # If a Province/City is found, remove it from the address (only the last occurrence)
    if founded_province:
        address = replace_last_occurrences(address, choose_word, "")
    
    if address.endswith("Thanh Pho ,"):
        address = address.replace("Thanh Pho ,", "")

    choose_word = ""
    largest_index = -1

    # Extract District after extracting Province/City
    if founded_province:
        for district in db_provinces[founded_province]['district']:
            for word in db_districts[district]['words']:
                reg_word = re.compile(fr"{word}{special_ending}")
                last_index = last_index_of_regex(address, reg_word)
                if (
                    (last_index > largest_index) or 
                    (
                        (last_index == largest_index) and 
                        (largest_index > -1) and 
                        (len(word) > len(choose_word))
                    )
                ):
                    founded_district = district
                    choose_word = word
                    largest_index = last_index
    else:
        # Extract District when Province/City is not present in the address 
        # (Inferring Province/City from the District)
        for district, district_data in db_districts.items():
            for word in district_data['words']:
                reg_word = re.compile(fr"{word}")
                last_index = last_index_of_regex(address, reg_word)
                if (
                    (last_index > largest_index) or 
                    (
                        (last_index == largest_index) and 
                        (largest_index > -1) and 
                        (len(word) > len(choose_word))
                    )
                ):
                    founded_district = district
                    choose_word = word
                    largest_index = last_index

    if founded_district:
        address = replace_last_occurrences(address, choose_word, "")
        if not founded_province:
            province_id = db_districts[founded_district]['province']
            founded_province = next((key for key, value in db_provinces.items() if value['id'] == province_id), "")

    largest_index = -1
    choose_word = ""

    # Extract Ward/Commune
    if founded_district:
        for ward in db_districts[founded_district]['ward']:
            for word in db_wards[ward]['words']:
                reg_word = re.compile(fr"{word}{special_ending}")
                last_index = last_index_of_regex(address, reg_word)
                if (
                    (last_index > largest_index) or 
                    (
                        (last_index == largest_index) and 
                        (largest_index > -1) and 
                        (len(word) > len(choose_word))
                    )
                ):
                    founded_ward = ward
                    choose_word = word
                    largest_index = last_index
        if founded_ward:
            address = replace_last_occurrences(address, choose_word, "")

    # Map results to Province, District, and Ward names
    founded_province = db_provinces.get(founded_province, {}).get('name', "")
    founded_district = db_districts.get(founded_district, {}).get('name', "")
    founded_ward = db_wards.get(founded_ward, {}).get('name', "")

    modified_address = address + " " + founded_ward + ", " + founded_district + ", " + founded_province
    return modified_address
