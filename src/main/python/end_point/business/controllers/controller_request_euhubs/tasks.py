
from __future__ import absolute_import, unicode_literals
from end_point.logging_ita import application_logger
from end_point.business.controllers.controllers import request_metadata_euhubs, mapper


def controller_request_euhubs(name=None, is_repo=None, description=None, domains=None, location=None,license=None, formats=None, privacy=None, publisher=None, language=None, issued=None, creator=None, from_augmented_time=None, from_upload_time=None, url=None, rdf_url=None, landing_page=None, spatial=None, similarity=None, source=None, team=None, is_author=None, modified=None) :
    """
    Request to the URL 'https://joyce2.ucd.ie/get_json/?'the datasets
    according to the given parameters. (Check '/api/docs' for more details).
    Returns a json file with the mapped datasets, in case of failure returns:
        {
            'error': Error message
            'codestatus': Error code
        }

    """
    metadata_list = {}
    message=None
    uri_list = None
    status_code = 200
    try:
        metadata_list = request_metadata_euhubs(name, is_repo, description, domains, location,license, formats, privacy, publisher, language, issued, creator, from_augmented_time, from_upload_time, url, rdf_url, landing_page, spatial, similarity, source, team, is_author, modified) 
        if len(metadata_list) < 1:
            message = "No datasets have been found: 400"
            application_logger.error(message)
            status_code = 400

    except Exception as e:
        message =f"Exception caugth: {str(e)} Error with datasets provider 503"
        application_logger.error(e, exc_info=True)
        application_logger.error(message)
        status_code = 500

    try:
        application_logger.warning(f"Let's start mapping...")
        uri_list_result = mapper.map_metadata_dcat(metadata_list, "Dataset")
        new_id_content_list = list()

        application_logger.warning(f"Let's prepare nodes...")
        for content_node in uri_list_result:
            if content_node and (not content_node in new_id_content_list):
                new_id_content_list.append(content_node)
        application_logger.warning(f"Let's create file...")
        uri_list = new_id_content_list

    except Exception as e:
        message = f"Server error, it has crashed 500 Exception caugth: {str(e)}"
        application_logger.error(message)
        application_logger.error(e, exc_info=True)
        status_code = 500
    return uri_list, message, status_code

# -------------- TASK --------------
def controller_request_euhubs_task(name=None, is_repo=None, description=None, domains=None, location=None,license=None, formats=None, privacy=None, publisher=None, language=None, issued=None, creator=None, from_augmented_time=None, from_upload_time=None, url=None, rdf_url=None, landing_page=None, spatial=None, similarity=None, source=None, team=None, is_author=None, modified=None):
    uri_list, message, status_code = controller_request_euhubs(name, is_repo, description, domains, location,license, formats, privacy, publisher, language, issued, creator, from_augmented_time, from_upload_time, url, rdf_url, landing_page, spatial, similarity, source, team, is_author, modified) 
    return {"uri_list": uri_list,'message': message}, status_code


