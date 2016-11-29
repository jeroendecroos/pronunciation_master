

def _map_language_to_hermitdave_code(language):
    """ hermitdave probably uses ISO 639:1
    for the moment not doing anything smart
    Returns code for hermitdave
    """
    language = language.lower()
    codes = {'dutch':'nl'}
    if language not in codes:
        raise ValueError("Language '{}' is not known".format(language))
    return codes[language]



