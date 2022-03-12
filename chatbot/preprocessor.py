def clean_url(text):
    """
    Remove any https from the statement text.
    """
    import re

    text = re.sub('http://\S+|https://\S+', '', text)

    return text
