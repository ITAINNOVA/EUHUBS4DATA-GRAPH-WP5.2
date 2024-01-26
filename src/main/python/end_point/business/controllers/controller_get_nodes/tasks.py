from __future__ import absolute_import, unicode_literals

from end_point.logging_ita import application_logger
from end_point.business.controllers.controllers import wrapper
from end_point.api.api_get_nodes_service import config


def controller_get_nodes(ontology, classnode):
    """
    Returns all the nodes related to a class from an ontology.
    Returns a json file with the nodes, in case of failure it
    just returns {}
    """
    response_content = {}
    application_logger.info(f"Getting all nodes for the request...")
    message = None
    status_code = 200
    try:

        if ontology[-1] != '/':
            ontology = ontology + '/'

        application_logger.info(f"{str(ontology)}{str(classnode)}")
        response_dict = wrapper.database_conector.request_all_instances_class(
            str(ontology)+str(classnode))

        for key, value in response_dict:
            response_content[key] = dict(value)
    except Exception as e:
        application_logger.error(e, exc_info=True)
        application_logger.error(f"Exception caugth: {str(e)}")
        application_logger.error(
            f"It was not possible to request all nodes which belongs to the class: {str(ontology)} {str(classnode)}")
        message = f"It was not possible to request all nodes which belongs to the class: {str(ontology)} {str(classnode)}"
        status_code = 500
    return response_content, message, status_code

# -------------- TASK --------------

def controller_get_nodes_task(ontology, classnode):

    response_content, message, status_code = controller_get_nodes(ontology, classnode)
    return {config.GET_NODE_DICT_NODE: response_content, 'message': message}, status_code
