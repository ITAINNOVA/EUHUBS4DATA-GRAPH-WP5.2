
import requests
import json
import re
import end_point.config as config
from end_point.logging_ita import application_logger
import end_point.business.utils as utils
# https://euh4d-data-portal.vm.fedcloud.eu/organization/euhubs4data
# https://euh4d-data-portal.vm.fedcloud.eu/api/action/'

class CkanImporter():
    """
    Classed used for interacting with the CKAN instance
    """
    def __init__(self, ckan_host=config.CKAN_HOST, api_key_ckan=config.CKAN_API_KEY,organization=config.CKAN_ORGANIZATION):
        self.ckan_host = ckan_host
        self.api_key_ckan = api_key_ckan
        self.organization = organization
        # Metada CKAN JSON
        # https://docs.ckan.org/en/2.9/api/index.html#module-ckan.logic.action.create

        self.dict_ckan_mapper = {
            'name': 'title',
            'description': 'notes',
            'url': 'url',
            'license': 'license_id',
            'publisher': 'author'
        }
        self.list_key_tags = [
            'domains',
            'formats',
            'location',
            'language'
        ]

    def ckan_mapper(self, dataset_ceadar, uri_list):
        """
        Maps the content of the datasets with the CEADAR metadata format
        to CKAN metadata format
        Args:
            dataset_ceadar (dict): Contains CEADAR metadata
            uri_list (list): Contains a list of uris, theses uris are linked to CEADAR ditionary
        """
        index = 0
        id = None
        while index < len(dataset_ceadar) and index < len(uri_list):
            dataset_int = dataset_ceadar[index]
            new_dict = dict()
            new_list_tags = list()
            new_list_extras = list()

            for key, value in dataset_int.items():
                mapped_key = self.dict_ckan_mapper.get(key)
                if value is not None:
                    if mapped_key is not None:
                        if key == 'name':
                            new_dict['name'] = re.sub(
                                r'[^A-Z^a-z^1-9]+', '', value).lower()[:100]
                        new_dict[mapped_key] = value
                    else:
                        if key in self.list_key_tags:
                            value_list = utils.prepare_and_parse_ckan(value)
                            for value_txt in value_list:
                                new_list_tags.append({
                                    'name': value_txt
                                })
                        else:
                            if key == 'id':
                                key = 'id_euhubs4data'
                            
                            if key.strip().lower() !="is_author":
                                new_list_extras.append({
                                        'key': key, 'value': value
                                    }
                                )

            if new_dict is not None and new_list_extras is not None:
                uri_node = uri_list[index]
                uri_node = uri_node.replace("http://www.w3.org/ns/", "")
                new_list_extras.append(
                    {
                        'key': 'idsExtraInfo', 'value': "https://euhub4data-graphs.itainnova.es/dataset/" + str(uri_node)
                    }
                )
                new_dict['extras'] = new_list_extras
                # tags
            if new_dict is not None and new_list_tags:
                new_dict['tags'] = new_list_tags
            if new_dict is not None:
                new_dict["owner_org"] = self.organization
            index = index + 1
            id = new_dict.get('name')
            if id is not None:
                self.send_dataset_ckan(new_dict, id)

    def send_dataset_ckan(self, dict_dataset, id):
        """
        Sends a dataset to CKAN.
        Args:
            dict_dataset (dict): The dataset to be sent.
            id (int): The ID of the dataset.
        https://stackoverflow.com/questions/24642317/create-ckan-dataset-using-ckan-api-and-python-requests-library
        Use the json module to dump the dictionary to a string for posting.
        We'll use the package_create function to create a new dataset.

        """
        try:
            # Creating a dataset requires an authorization header.
            # Replace *** with your API key, from your user account on the CKAN site
            # that you're creating the dataset on.
            d_url = self.ckan_host+'/api/action/package_create'
            # Make the HTTP request.
            success_result = self.base_ckan_request(
                dict_dataset, d_url)
            if success_result:
                application_logger.info("Dataset created!")
                application_logger.info(dict_dataset)
            else:
                application_logger.warning(
                    "It could not create a new dataset! Let's try deleting it!")
                self.delete_dataset_ckan(dict_dataset, id)
                application_logger.info("Let's try it again!")
                success_result = self.base_ckan_request(
                    dict_dataset, d_url)
            # Use the json module to load CKAN's response into a dictionary
        except Exception as e:
            application_logger.error(
                f"Error while requesting dataset to CKAN: {str(e)}")
            application_logger.error(e, exc_info=True)

    def base_ckan_request(self, dict_dataset, url):
        """
        It requests the CKAN endpoint by using POST peticion in order to create a new dataset on the CKAN portal.
        Args:
            url (str): CKAN URL
            dict_dataset (dict): Dataset
        """
        dict_dataset = json.dumps(dict_dataset)
        head = {'Authorization': self.api_key_ckan}
        head['Content-Type'] = 'application/json'
        success_result = False
        response = requests.post(url, data=dict_dataset, headers=head)
        try:
            response_dict = json.loads(response.text)
            if response_dict:
                if response_dict.get('success'):
                    success_result = response_dict.get('success')
                    ckan_result = response_dict.get('result')
                    if ckan_result:
                        application_logger.info(f"New content: {str(ckan_result)}")
                else:
                    application_logger.error(f"Error from the CKAN server {str(response_dict)}")
            else:
                application_logger.error("No response from CKAN server")
        except Exception as e:
            application_logger.error(
                f"Error! \nURL: {str(url)} \nContent:{dict_dataset}\nError: {str(e)}")
            application_logger.error(e, exc_info=True)
        return success_result


    def update_dataset_ckan(self, dict_dataset, id):
        """
        Update dataset in CKAN.
        https://euh4d-data-portal.vm.fedcloud.eu

        Args:
            dict_dataset (dict): Dictionary containing dataset information.
            id (str): ID of the dataset to be updated.

        Returns:
            None
        """
        try:
            dict_dataset['id'] = id
            update_url = self.ckan_host + '/api/action/package_update'
            success_result = self.base_ckan_request(dict_dataset, update_url)
            if success_result:
                application_logger.info("Dataset updated!")
                application_logger.info(dict_dataset)
            else:
                application_logger.warning(
                    f"It could not update the dataset! Dataset id: {str(id)}")
        except Exception as e:
            application_logger.error(
                f"Error! \nID: {str(id)} \nContent:{dict_dataset}\nError: {str(e)}")
            application_logger.error(e, exc_info=True)

    def delete_dataset_ckan(self, dict_dataset, id):
        """
        Delete a dataset from CKAN.

        Args:
            dict_dataset (dict): The dataset dictionary.
            id (str): The ID of the dataset to delete.

        Returns:
            None
        """
        try:
            delete_url = self.ckan_host + '/api/action/package_delete'
            dict_dataset['id'] = id

            # Make a request to delete the dataset
            success_result = self.base_ckan_request({'id': id}, delete_url)

            if success_result:
                # Log successful dataset deletion
                application_logger.info("Dataset deleted!")
                application_logger.info(dict_dataset)
            else:
                # Log failure to delete dataset
                application_logger.warning("Failed to delete the dataset!")
                application_logger.warning(f"Dataset ID: {str(id)}")
        except Exception as e:
            # Log any exceptions that occur
            application_logger.error(
                f"Error occurred while deleting dataset! \nID: {str(id)} \nContent: {dict_dataset}\nError: {str(e)}")
            application_logger.error(e, exc_info=True)


ckan_importer = CkanImporter(
    ckan_host=config.CKAN_HOST,
      api_key_ckan=config.CKAN_API_KEY
)