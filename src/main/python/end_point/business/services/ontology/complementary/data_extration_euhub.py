import requests
from end_point.logging_ita import application_logger


class ExtrationData:
    """
    Class whose purpose is retrieving data from "https://cm.iti.es/api/integrations/datasets-metadata"
    """
    def __init__(self, dataset_url_path, authorization_token=None):
        self.url_path = dataset_url_path
        self.unique_secret_token = authorization_token

    def __add_element(self, property, content, base_url):
        """
        Adds the given property and content to the base_url and returns the updated base_url.

        Args:
            property (str): The property to add to the base_url.
            content (str): The content to add to the base_url.
            base_url (str): The base_url to update.

        Returns:
            str: The updated base_url.
        """
        try:
            if content:
                # Log the property and content
                application_logger.info(f'{str(property)}  - {str(content)}')

                # Update the base_url
                base_url = base_url + str(property) + '='+str(content) + '&'

        except Exception as e:
            # Log the exception and the error details
            application_logger.error(f'Exception caught: {str(e)}')
            application_logger.error(f'Error with {property}  - {content}')
            application_logger.error(e, exc_info=True)

        return base_url

        
    def __build_url(self, name=None,is_repo=None, description=None, domains=None, license=None, location=None, formats=None, privacy=None, publisher=None, language=None, issued=None, creator=None, from_augmented_time=None, from_upload_time=None, url=None, rdf_url=None, landing_page=None, spatial=None, similarity=None, source=None, team=None, is_author=None, modified=None):
        """
        Build the URL based on the given parameters.

        Args:
            name (str): The name parameter.
            is_repo (bool): The is_repo parameter.
            description (str): The description parameter.
            domains (list): The domains parameter.
            license (str): The license parameter.
            location (str): The location parameter.
            formats (list): The formats parameter.
            privacy (str): The privacy parameter.
            publisher (str): The publisher parameter.
            language (str): The language parameter.
            issued (str): The issued parameter.
            creator (str): The creator parameter.
            from_augmented_time (str): The from_augmented_time parameter.
            from_upload_time (str): The from_upload_time parameter.
            url (str): The url parameter.
            rdf_url (str): The rdf_url parameter.
            landing_page (str): The landing_page parameter.
            spatial (str): The spatial parameter.
            similarity (str): The similarity parameter.
            source (str): The source parameter.
            team (str): The team parameter.
            is_author (bool): The is_author parameter.
            modified (str): The modified parameter.

        Returns:
            str: The built URL
        """
        base_url = self.url_path

        base_url = self.__add_element('name', name, base_url)
        base_url = self.__add_element('is_repo', is_repo, base_url)
        base_url = self.__add_element('description', description, base_url)
        base_url = self.__add_element('domains', domains, base_url)
        base_url = self.__add_element('license', license, base_url)
        base_url = self.__add_element('location', location, base_url)
        base_url = self.__add_element('formats', formats, base_url)
        base_url = self.__add_element('privacy', privacy, base_url)
        base_url = self.__add_element('publisher', publisher, base_url)
        base_url = self.__add_element('language', language, base_url)
        base_url = self.__add_element('issued', issued, base_url)
        base_url = self.__add_element('creator', creator, base_url)
        base_url = self.__add_element('augmented_time', from_augmented_time, base_url)
        base_url = self.__add_element('upload_time', from_upload_time, base_url)

        base_url = self.__add_element('url', url, base_url)
        base_url = self.__add_element('rdf_url', rdf_url, base_url)
        base_url = self.__add_element('landing_page', landing_page, base_url)

        base_url = self.__add_element('spatial', spatial, base_url)
        base_url = self.__add_element('similarity', similarity, base_url)
        base_url = self.__add_element('source', source, base_url)

        base_url = self.__add_element('team', team, base_url)
        base_url = self.__add_element('is_author', is_author, base_url)

        if modified:
            base_url = base_url + 'modified=' + str(modified)

        application_logger.info(f"URL: {base_url}")

        return base_url

    def __get_response(self, name=None, is_repo=None, description=None, domains=None, location=None, license=None, formats=None, privacy=None, publisher=None, language=None, issued=None, creator=None, from_augmented_time=None, from_upload_time=None, url=None, rdf_url=None, landing_page=None, spatial=None, similarity=None, source=None, team=None, is_author=None, modified=None):
        """
        Build the URL with the given params, do a get request to this URL
        and return its response.
        :param limit: Number of datasets delivered
        :param query: Query of the data
        :param category: Code of dataset's category
        :param country: Code of dataset's country
        :param page: Number of page requested
        :return: response = requests.get(URL
        """
        response = None
        try:
            URL = self.__build_url(name, is_repo, description, domains, location, license, formats, privacy, publisher, language, issued, creator,
                                   from_augmented_time, from_upload_time, url, rdf_url, landing_page, spatial, similarity, source, team, is_author, modified)
            if self.unique_secret_token:
                headers = {"Authorization": self.unique_secret_token}
                response = requests.get(URL, verify=False, headers=headers)
            else:
                response = requests.get(URL)

        except Exception as e:
            application_logger.error(
                f'Exception caught while requesting to the URL: {str(e)}')
            application_logger.error(e, exc_info=True)
        return response


#####################################################################

#   MAIN FUNCTION

#####################################################################

    # Initial function which starts everything

    def search_default_datasets(self, name=None, is_repo=None, description=None, domains=None, location=None, license=None, formats=None, privacy=None, publisher=None, language=None, issued=None, creator=None, from_augmented_time=None, from_upload_time=None, url=None, rdf_url=None, landing_page=None, spatial=None, similarity=None, source=None, team=None, is_author=None, modified=None):
        """
        Search for datasets based on various parameters.

        Args:
            name (str): Name of the dataset.
            is_repo (bool): Whether the dataset is a repository.
            description (str): Description of the dataset.
            domains (list): List of domains the dataset belongs to.
            location (str): Location of the dataset.
            license (str): License of the dataset.
            formats (list): List of formats the dataset is available in.
            privacy (str): Privacy level of the dataset.
            publisher (str): Publisher of the dataset.
            language (str): Language of the dataset.
            issued (str): Date the dataset was issued.
            creator (str): Creator of the dataset.
            from_augmented_time (str): Dataset created from this time.
            from_upload_time (str): Dataset uploaded from this time.
            url (str): URL of the dataset.
            rdf_url (str): RDF URL of the dataset.
            landing_page (str): Landing page of the dataset.
            spatial (str): Spatial information of the dataset.
            similarity (str): Similarity score of the dataset.
            source (str): Source of the dataset.
            team (str): Team responsible for the dataset.
            is_author (bool): Whether the user is the author of the dataset.
            modified (str): Date the dataset was last modified.

        Returns:
            list: List of datasets matching the search criteria.
        """
        datasets_result = list()

        # Get the first url which contains the information of the number
        # of datasets related to the query
        response = self.__get_response(name, is_repo, description, domains, location, license, formats, privacy, publisher, language, issued,
                                    creator, from_augmented_time, from_upload_time, url, rdf_url, landing_page, spatial, similarity, source, team, is_author, modified)

        # Everything goes well
        application_logger.info("Getting response from dataset repository...")
        try:

            if response.status_code == 200:
                try:
                    json_response = response.json()
                    json_response = json_response.get('data')
                    if json_response:
                        # Number of datasets available
                        for key, dataset in json_response.items():
                            if dataset:
                                datasets_result.append(dataset)
                        # In case there are more than the requested just ignore them

                except Exception as e:
                    application_logger.error(f'Exception caught: {str(e)}')
                    application_logger.error(
                        'Exception caught while setting everything up')
                    application_logger.error(e, exc_info=True)

            else:
                application_logger.error(
                    f"Error getting access to {response.url}")
                application_logger.error(
                    f"Http status result: {str(response.status_code)}")
        except Exception as e:
            application_logger.error(
                f'Exception caught while searching for datasets: {str(e)}')
            application_logger.error(e, exc_info=True)

        return datasets_result
