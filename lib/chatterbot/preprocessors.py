"""
Statement pre-processors.
"""


def clean_whitespace(statement):
    """
    Remove any consecutive whitespace characters from the statement in_response_to.
    """
    import re

    # Replace linebreaks and tabs with spaces
    statement.in_response_to = statement.in_response_to.replace(
        '\r', ' ').replace('\t', ' ')

    # Remove any leeding or trailing whitespace
    statement.in_response_to = statement.in_response_to.strip()

    # Remove consecutive spaces
    statement.in_response_to = re.sub(' +', ' ', statement.in_response_to)

    return statement


def unescape_html(statement):
    """
    Convert escaped html characters into unescaped html characters.
    For example: "&lt;b&gt;" becomes "<b>".
    """
    import html

    statement.in_response_to = html.unescape(statement.in_response_to)

    return statement


def convert_to_ascii(statement):
    """
    Converts unicode characters to ASCII character equivalents.
    For example: "på fédéral" becomes "pa federal".
    """
    import unicodedata

    in_response_to = unicodedata.normalize('NFKD', statement.in_response_to)
    in_response_to = in_response_to.encode('ascii', 'ignore').decode('utf-8')

    statement.in_response_to = str(in_response_to)
    return statement
