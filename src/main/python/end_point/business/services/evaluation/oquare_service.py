

import xmltodict
from end_point.logging_ita import application_logger
import os


class OQuareMetrics:
    def build_json_from_cache(self, db_cache):
        """
        Builds a JSON object from the given database cache.

        Args:
            db_cache (DBCache): The database cache object.

        Returns:
            dict: The JSON object built from the cache.
        """
        # Log the start of building the JSON object
        application_logger.info("Building base ontology metrics JSON")

        # Get the metrics ontology array
        json_core = db_cache.get_metrics_ontology_array()

        # Add Oquare metrics to the JSON object
        json_core['oquare_structural'] = db_cache.get_oquare_structural_metrics()
        json_core['oquare_adequacy'] = db_cache.get_oquare_adequacy()
        json_core['oquare_compatibility'] = db_cache.get_oquare_compatibility()
        json_core['oquare_maintainbility'] = db_cache.get_oquare_maintainbility()
        json_core['oquare_operability'] = db_cache.get_oquare_operability()
        json_core['oquare_reliability'] = db_cache.get_oquare_reliability()
        json_core['oquare_transferability'] = db_cache.get_oquare_transferability()

        # Log the completion of adding Oquare metrics to the JSON object
        application_logger.info("Added Oquare metrics to the JSON object")

        # Add score list and value list to the JSON object
        json_core['score_list'] = db_cache.get_score_list()
        json_core['value_list'] = db_cache.get_value_list()

        return json_core

    def request_metrics_cache(self, db_cache=None, ontology_path=None, local_xml_data_saved=None, java_path=None):
        """
        Request metrics cache by generating an XML file from an ontology file using a Java program.

        Args:
            db_cache (dict, optional): The database cache.
            ontology_path (str, optional): The path to the ontology file.
            local_xml_data_saved (str, optional): The path to save the generated XML data.
            java_path (str, optional): The path to the Java program.

        Raises:
            Exception: If there is an error while saving the XML file.

        """

        try:
            try:
                # Create a temporary copy of the local XML data file
                os.system(f'cp -f {str(local_xml_data_saved)} {str(local_xml_data_saved)}_tmp.xml')
                # Remove the original local XML data file
                os.system(f'rm -f {str(local_xml_data_saved)}')
                # Generate the XML data file from the ontology file using the Java program
                os.system(f'java -jar {str(java_path)}oquare-versions.jar --ontology {str(ontology_path)}  --outputFile {str(local_xml_data_saved)} --reasoner ELK')
            except Exception as ex:
                # Restore the original local XML data file from the temporary copy
                os.system(f'cp -f {str(local_xml_data_saved)}_tmp.xml {str(local_xml_data_saved)}')

            # Open the file and read the contents
            self.read_file_to_cache(local_xml_data_saved, db_cache)

        except Exception as ex:
            # Log the error if there is an error while saving the XML file
            application_logger.error(f"Error while saving xml file: {str(ex)}")
            application_logger.error(ex, exc_info=True)

    def read_file_to_cache(self, local_xml_data_saved, db_cache=None):
        """
        Reads the XML file from the specified path and adds the parsed metrics and values to the cache.

        Args:
            local_xml_data_saved (str): The path to the XML file.
            db_cache (object, optional): The cache object to store the metrics and values. Defaults to None.
        """
        try:
            with open(local_xml_data_saved, 'r', encoding='utf-8') as file:
                my_xml = file.read()

            # Use xmltodict to parse and convert the XML document
            my_dict = xmltodict.parse(my_xml)

            oquare_dict = my_dict.get("oquare")
            oquare_metrics = oquare_dict.get("oquareMetrics")
            oquare_metrics_scale = oquare_dict.get("oquareMetricsScaled")
            
            # Add basic metrics to the cache
            if db_cache:
                db_cache.add_metrics_ontology({
                    "scores": oquare_metrics_scale,
                    "values": oquare_metrics
                })

            scores_list = list()
            values_list = list()
            
            # Extract scores and values lists from the metrics dictionaries
            for k, v in oquare_metrics_scale.items():
                scores_list.append(v)

            for k, v in oquare_metrics.items():
                values_list.append(v)

            oquare_model_dict = oquare_dict.get("oquareModel")
            
            # Extract specific metrics from the model dictionary
            oquare_compatibility = oquare_model_dict.get("oquareModelCompatibility")
            oquare_adequacy = oquare_model_dict.get("oquareModelFunctionalAdequacy")
            oquare_maintainability = oquare_model_dict.get("oquareModelMaintainability")
            oquare_operability = oquare_model_dict.get("oquareModelOperability")
            oquare_reliability = oquare_model_dict.get("oquareModelReliability")
            oquare_structural = oquare_model_dict.get("oquareModelStructural")
            oquare_transferability = oquare_model_dict.get("oquareModelTransferability")

            if db_cache:
                application_logger.warning("Add metrics to cache db")

                # Add specific metrics to the cache
                db_cache.add_oquare_structural_metrics(oquare_structural)
                db_cache.add_oquare_adequacy(oquare_adequacy)
                db_cache.add_oquare_compatibility(oquare_compatibility)
                db_cache.add_oquare_maintainbility(oquare_maintainability)
                db_cache.add_oquare_operability(oquare_operability)
                db_cache.add_oquare_reliability(oquare_reliability)
                db_cache.add_oquare_transferability(oquare_transferability)

                # Add scores and values lists to the cache
                db_cache.add_score_list(scores_list)
                db_cache.add_value_list(values_list)

        except Exception as ex:
            application_logger.error(f"Error while reading xml file: {str(ex)}")
            application_logger.error(ex, exc_info=True)



