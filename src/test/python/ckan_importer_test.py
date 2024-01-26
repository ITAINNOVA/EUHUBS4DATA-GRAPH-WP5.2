import os
from end_point.business.services.ckan_updater.ckan_importer import CkanImporter
dict_tag = {'license_id': 'Open Data Commons Open Database License\xa0(ODbL-1.0)', 'name': 'smartpointsofinterest',
             'title': 'Smart Points of Interest', 'author': 'Plan4all', 'url': 'https://hub.plan4all.eu/spoi',
               'notes': 'Smart Points of Interest is an open dataset published as Linked Open Data. It contains more than 33 million points of interest over the whole world.',
                 'extras': [{'key': 'creator', 'value': 'Plan4all'},
                             {'key': 'issued', 'value': '2015'}, {'key': 'landing_page', 'value': 'https://sdi4apps.eu/spoi/'}, {'key': 'modified', 'value': '2021'},
                               {'key': 'privacy', 'value': 'No personal data'}, {'key': 'team', 'value': 'Plan4all'},
                                 {'key': 'id_euhubs4data', 'value': '843ec861fac9ff6eee495f4b84ace652be268920b3a9322e0de09c4ac5295231_UCSGN7FPQCVD6T6KNRQMX62CSTYFCIOASFCYQBECROSS32EDTPIXRE5K'},
                                   {'key': 'idsExtraInfo', 'value': 'https://euhub4data-graphs.itainnova.es/dataset/dcat#Dataset_3294acf1-d329-4e60-a334-092c4ecf37c2'}],
    'tags': [{'name': 'Agriculture'}, {'name': ' Fisheries'}, {'name': ' Forestry '}, {'name': ' Food'},
              {'name': 'Education'}, {'name': ' Culture '}, {'name': ' Sport'},
                {'name': 'Environment'}, {'name': 'Energy'}, {'name': 'Regions '},
                  {'name': ' Cities'}, {'name': 'Government '},
                    {'name': ' Public Sector'}, {'name': 'Health'},
                      {'name': 'Population '}, {'name': ' Society'},
                        {'name': 'Science '}, {'name': ' Technology'},
                          {'name': 'Transport'}, {'name': 'RDF'}, {'name': 'English'},
                            {'name': 'EU-wide'}], 'id': 'smartpointsofinterest'}
ckan_importer = CkanImporter(
    "https://euh4d-data-portal.vm.fedcloud.eu/", os.environ.get('CKAN_API_KEY'))
ckan_importer.send_dataset_ckan(dict_tag, 'smartpointsofinterest')