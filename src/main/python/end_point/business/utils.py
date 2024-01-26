import re
import py3langid as langid
import base64
import random
import datetime
from rdflib import URIRef
from end_point.logging_ita import application_logger


def get_uriref_str(uriref):
    """
    Get the URIref in string format.
    :param uriref: The URIref.
    :return: The URIref in string format.
    """
    if type(uriref) is str:
        return uriref
    else:
        return str(uriref.toPython())


def set_uriref_str(uriref):
    """
    Sets the URIRef string.
    Args:
        uriref (str or URIRef): The URIRef string.
    Returns:
        URIRef: The URIRef object.
    """
    if type(uriref) is str:
        return URIRef(uriref)
    else:
        return uriref


def basencode54(message):
    """
    Encode the <message> in base64
    """
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message


def build_filename(basename, base_resource_path, preffix="ttl"):
    """
    Creates a random name for a file
    :param basename: Name of the file
    :param base_resource_path: preffix of the path
    """
    base_path = base_resource_path + basename + "."+preffix
    filename = basename + "." + preffix
    return base_path, filename


def create_html_from_json(json_content):
    """
    Creates an HTML string from a JSON object.

    Args:
        json_content (dict): The JSON object to convert to HTML.

    Returns:
        str: The HTML string representation of the JSON object.
    """
    html_content = ""
    for key, value in json_content.items():
        html_content = html_content + \
            f"<p>{str(delete_ontology_preffix(key))}: {value}</p>"
    return html_content


def convert_datetime_isoformat(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    else:
        return o


def delete_ontology_preffix(content_ontology):
    """
    Deletes the ontology prefix from the given content_ontology.

    Args:
        content_ontology (str): The content ontology string.

    Returns:
        str: The content ontology string without the prefix.
    """
    return content_ontology.split("/")[-1].split("#")[-1]


def delete_prefix_uri(content_uri: str, uri_prefix: str) -> str:
    """
    Remove the given URI prefix from the content URI and return the modified URI.

    Args:
        content_uri (str): The content URI to modify.
        uri_prefix (str): The URI prefix to remove from the content URI.

    Returns:
        str: The modified content URI.
    """
    # Remove trailing slash from URI prefix if present
    if uri_prefix[-1] == "/":
        uri_prefix = uri_prefix[:-1]
    
    # Remove URI prefix and "#_" from content URI
    content_uri = content_uri.replace(uri_prefix, "").replace("#_", "")
    
    return content_uri


def detect_metadata_language(metadata_text):
    """ 
    Detect the language of the metadata information.
    :param metadata_text: Metadata information.
    :return: The detected language.
    """
    lang = 'en'
    try:
        lang, conf = langid.classify(metadata_text)
    except Exception as ex:
        application_logger.error(f'Error detecting language: {str(ex)}')
        application_logger.error(ex, exc_info=True)
    return lang


def prefix_is_contain(prefix, content):
    """
    Checks if the given prefix is contained in the content.

    Args:
        prefix (str): The prefix to check for.
        content (str): The content to search in.

    Returns:
        bool: True if the prefix is found in the content, False otherwise.
    """
    return (prefix in content)


def get_random_colour():
    def r(): return random.randint(0, 255)
    return ('#%02X%02X%02X' % (r(), r(), r()))


def prepare_and_parse_ckan(value_list: str):
    """
    Split the input string by delimiters and parse the values.
    
    Args:
        value_list (str): The input string containing values separated by delimiters.
        
    Returns:
        List[str]: A list of parsed values with leading and trailing whitespaces removed.
    """
    # Split the input string by delimiters: comma, colon, semicolon, backslash, forward slash, and 'and'
    value_list = re.split(r'[,:;\\\/]|\band\b', value_list)
    
    new_values = []
    for value in value_list:
        # Check if the value is not an empty string
        if value != '':
            new_values.append(str(value).strip())
    
    return new_values


def get_name_from_url(url):
    """ Given an uri returns the last name which compose
        that uri
    Args:
        url (str): Url belonged to an ontology
    Returns:
        str Return the name of class, string.
    """
    new_name = None
    if type(url) is str:
        url_contents = url.split('/')
        new_name = url_contents[-1]
    return new_name


def transform_class_name(class_name):
    """
    Given a name composed by many words it separates then into a sentence.
    :param class_name: String with the format: DataResource,SmartDataAPP
    :return: The resultant name divide by spaces.
    """
    testing_name = ""
    if "#" in class_name:
        class_name = class_name.split("#")
        if len(class_name) > 1:
            class_name = class_name[1]
    if class_name:
        new_name = re.split("([A-Z][^A-Z][^A-Z]*)",
                            short_capitalize(class_name))
        len_name = len(new_name)
        for i in range(len_name):
            if (i == 0 or i == (len_name - 1)) and not new_name[i]:
                continue
            elif not new_name[i]:
                testing_name += ' '
            elif new_name[i]:
                testing_name += new_name[i]
    if testing_name == "" or not testing_name:
        testing_name = class_name
    return testing_name.replace("_", " ").lower()


def short_capitalize(name):
    """
    Capitalize the first letter of a string.

    Args:
        name (str): The input string.

    Returns:
        str: The input string with the first letter capitalized.
    """
    # Convert the string to a list of characters
    characters = list(name)

    # Capitalize the first character
    characters[0] = characters[0].upper()

    # Convert the list of characters back to a string
    capitalized_name = ''.join(characters)

    return capitalized_name
