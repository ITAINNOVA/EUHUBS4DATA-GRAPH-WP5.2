
from __future__ import absolute_import, unicode_literals
from end_point.logging_ita import application_logger
from end_point.business.controllers.controllers import mapper
from end_point.api.api_apply_match_and_map_service import config

def controller_map_metadata(metadata):
    """
    Map metadata with the IDS vocabulary

    Args:
        request (dict): Json which contains metadata

    Returns:
        In case of working succesfully:
            {
                'uri_list': List with the uris of the created nodes.
                'url_redirect': Url where the RDF file can be downloaded
            }

    In case of failure returns:
        {
            'error': Error message
            'codestatus': Error code
        }
    """
    metadata_list = list()
    uri_list = None
    message = None
    status_code = 200
    
    if type(metadata) is list:
        metadata_list = metadata
    else:
        metadata_list.append(metadata)
    try:
        application_logger.warning(f"Let's start mapping...")
        uri_list_result = mapper.map_metadata_base(
            metadata_list, "Data resource")
        new_id_content_list = list()
        application_logger.warning(f"Let's prepare nodes...")
        for content_node in uri_list_result:
            if content_node and (not content_node in new_id_content_list):
                new_id_content_list.append(content_node)
        application_logger.warning(f"Let's create file...")
        uri_list = new_id_content_list
    except Exception as e:
        message = f" Server error, it has crashed Exception caugth: {str(e)}"
        application_logger.error(message)
        application_logger.error(e, exc_info=True)
        status_code = 500

    return uri_list, message, status_code

# -------------- TASK --------------
def controller_map_metadata_task(metadata):
    
    uri_list, message, status_code = controller_map_metadata(metadata)
    return {config.APMM_URI_LIST: uri_list, 'message': message}, status_code
