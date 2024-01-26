from __future__ import absolute_import, unicode_literals

from end_point.logging_ita import application_logger
import json
from flask import Response, send_from_directory
from end_point import config as settings


def controller_get_rdf(rdf_filename):
    """
    Returns the file with the name <rdf_filename>, this file must be in the folder <config.APP_ONTOLOGY>
    In case of failure:
            {
                'error': Error message
                'codestatus': Error code
            }

    """
    try:
        application_logger.info(f"Lets try to send the file! {str(rdf_filename)}")
        return send_from_directory(directory=settings.APP_ONTOLOGY, path=rdf_filename, as_attachment=True)
    except Exception as e:
        application_logger.error(f"Server error, File not found: {str(e)}")
        application_logger.error(e, exc_info=True)
        return Response(json.dumps({"error": "Server error, File not found", "codestatus": 404, "exception": str(e)}), 404, mimetype='application/json')




