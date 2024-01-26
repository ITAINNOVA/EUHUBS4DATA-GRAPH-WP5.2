
from __future__ import absolute_import, unicode_literals
from end_point.logging_ita import application_logger
from end_point.business.controllers.controllers import matchAndmap
from end_point.api.api_apply_match_and_map_service import config


def controller_match_and_map(textarea):
    """
    Given a plain text through the requests object
    applies the algorithm Match&Map to this plain text,
    mapping the result triplets in the database.
    Returns a json dictionary with the following format:
        In case of working succesfully:
            {
                'uri_list': List with the uris of the created nodes.,
                'message': Error message

            }
    """
    uri_list = list()
    message = None
    nodes_list = list()
    status_code = 200
    try:

        if textarea:
            plain_text = textarea
            if plain_text:
                nodes_list = matchAndmap.apply_mama_pipe(
                    plain_text)
                application_logger.warning("Let's see the nodes: ")    

                new_id_content_list = list()
                result_dict = dict()

                for content_node in nodes_list:
                    if content_node.get('id') and (not content_node.get('id') in new_id_content_list):
                        new_id_content_list.append(content_node.get('id'))

                result_dict['uri_list'] = new_id_content_list
                uri_list = new_id_content_list
            else:
                message = "Missing textarea argument, it has to be a string with the text to be mapped"
                status_code= 400

        else:
            message = "No request provided"
    except Exception as e:
        application_logger.error(
            f"Exception caugth while applying Match and Map: {str(e)}")
        application_logger.error(e, exc_info=True)
        message =  f"Exception caugth while applying Match and Map: {str(e)} Server message, message while mapping triplets"
        status_code = 500

    return uri_list, message,status_code 


# -------------- TASK --------------
def controller_match_and_map_task(textarea):
    
    uri_list, message, status_code  = controller_match_and_map(textarea=textarea)
    return {config.APMM_URI_LIST: uri_list, 'message': message}, status_code
