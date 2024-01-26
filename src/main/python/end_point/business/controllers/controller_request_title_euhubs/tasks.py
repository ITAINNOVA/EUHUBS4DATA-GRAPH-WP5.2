from __future__ import absolute_import, unicode_literals

from end_point.logging_ita import application_logger
from end_point.business.controllers.controllers import request_metadata_euhubs


def controller_request_title_euhubs(name=None, is_repo=None, description=None, domains=None, location=None,license=None, formats=None, privacy=None, publisher=None, language=None, issued=None, creator=None, from_augmented_time=None, from_upload_time=None, url=None, rdf_url=None, landing_page=None, spatial=None, similarity=None, source=None, team=None, is_author=None, modified=None):
    """
    This function takes in various parameters and returns a list of dataset titles, 
    along with a message and status code.
    Args:
        name (str): The name of the dataset.
        is_repo (bool): Whether the dataset is a repository.
        description (str): The description of the dataset.
        domains (list): The domains associated with the dataset.
        location (str): The location of the dataset.
        license (str): The license of the dataset.
        formats (list): The formats of the dataset.
        privacy (str): The privacy level of the dataset.
        publisher (str): The publisher of the dataset.
        language (str): The language of the dataset.
        issued (str): The date the dataset was issued.
        creator (str): The creator of the dataset.
        from_augmented_time (str): The starting date for augmented datasets.
        from_upload_time (str): The starting date for uploaded datasets.
        url (str): The URL of the dataset.
        rdf_url (str): The RDF URL of the dataset.
        landing_page (str): The landing page of the dataset.
        spatial (str): The spatial information of the dataset.
        similarity (float): The similarity score of the dataset.
        source (str): The source of the dataset.
        team (str): The team associated with the dataset.
        is_author (bool): Whether the user is the author of the dataset.
        modified (str): The date the dataset was modified.
    Returns:
        title_list (list): A list of dataset titles.
        message (str): A message indicating the status of the request.
        status_code (int): The status code of the request.
    """
    message = None
    title_list = None
    status_code = 200
    try:
        metadata_list = request_metadata_euhubs(name, is_repo, description, domains, location,license, formats, privacy, publisher, language, issued, creator, from_augmented_time, from_upload_time, url, rdf_url, landing_page, spatial, similarity, source, team, is_author, modified) 
        if len(metadata_list) < 1:
            message = "No datasets have been found 400"
            status_code = 400

    except Exception as e:
        message = f" Error with datasets provider 503 Exception caugth: {str(e)}"
        application_logger.error(e, exc_info=True)
        application_logger.error(message)
        status_code = 500

    title_list = list()
    for dataset in metadata_list:
        application_logger.warning(dataset)
        if dataset.get("name"):
            dataset["dataset_name"] = dataset.get("name")
            title_list.append(dataset)
    application_logger.warning("Listing names done!")
    return title_list, message, status_code

# -------------- TASK --------------
def controller_request_title_task(name=None, is_repo=None, description=None, domains=None, location=None,license=None, formats=None, privacy=None, publisher=None, language=None, issued=None, creator=None, from_augmented_time=None, from_upload_time=None, url=None, rdf_url=None, landing_page=None, spatial=None, similarity=None, source=None,  team=None, is_author=None, modified=None):
    
    title_list, message, status_code = controller_request_title_euhubs(name, is_repo, description, domains, location,license, formats, privacy, publisher, language, issued, creator, from_augmented_time, from_upload_time,url, rdf_url, landing_page, spatial, similarity, source,  team, is_author, modified) 
    return {"dataset_list": title_list, 'message': message}, status_code

