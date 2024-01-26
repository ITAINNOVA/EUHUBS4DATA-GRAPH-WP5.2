
import threading

class CacheDB():
    """
    Class used with the purpose of ease the access to data retrieved from the database
    """

    def __init__(self):
        # Some resourses are accessed by functions from more than one thread
        # so in order to avoid misreading or miswriting information a mutex is
        # required
        self.mutex = threading.Lock()

        self.prediction_class_map = {}
        self.class_prediction_map = {}
        self.title_uri_map = {}
        self.objectype_class = {}
        self.datatype_class = {}
        self.object_metadata_map = {}
        self.class_color = {}
        self.entity_prediction = {}
        self.tmp_class_color = list()

        self.scores_list = list()
        self.values_list = list()
        self.ontology_score_array = list()

        self.oquare_structural = {}
        self.oquare_adequacy = {}
        self.oquare_compatibility = {}
        self.oquare_maintainbility = {}
        self.oquare_operability = {}
        self.oquare_reliability = {}
        self.oquare_transferability = {}

    def get_class_of_prediction(self, prediction):
        return self.prediction_class_map.get(prediction)

    def get_uri_of_title(self, title_entity):
        return self.title_uri_map.get(title_entity)

    def get_prediction_of_class(self, class_enttity):
        return self.class_prediction_map.get(class_enttity)

    def get_class_objecttype_properties(self, class_entity):
        return self.objectype_class.get(class_entity)

    def get_class_datatype_properties(self, class_entity):
        return self.datatype_class.get(class_entity)

    def get_map_metadata(self, original_meta):
        return self.object_metadata_map.get(original_meta)

    def get_color_class(self, class_name):
        return self.class_color.get(class_name)

    def get_all_color_class(self):
        return self.tmp_class_color

    def get_entity_prediction(self, entity):
        return self.entity_prediction.get(entity)

    def get_entity_prediction_dict(self):
        return self.entity_prediction

    def get_metrics_ontology_array(self):
        return self.ontology_score_array

    def get_oquare_structural_metrics(self):
        return self.oquare_structural

    def get_oquare_adequacy(self):
        return self.oquare_adequacy

    def get_oquare_compatibility(self):
        return self.oquare_compatibility

    def get_oquare_maintainbility(self):
        return self.oquare_maintainbility

    def get_oquare_operability(self):
        return self.oquare_operability

    def get_oquare_reliability(self):
        return self.oquare_reliability

    def get_oquare_transferability(self):
        return self.oquare_transferability

    def get_score_list(self):
        return self.scores_list

    def get_value_list(self):
        return self.values_list

    def add_oquare_structural_metrics(self, oquare_structural):
        self.mutex.acquire()
        self.oquare_structural = oquare_structural
        self.mutex.release()

    def add_oquare_adequacy(self, oquare_adequacy):
        self.mutex.acquire()
        self.oquare_adequacy = oquare_adequacy
        self.mutex.release()

    def add_oquare_compatibility(self, oquare_compatibility):
        self.mutex.acquire()
        self.oquare_compatibility = oquare_compatibility
        self.mutex.release()

    def add_oquare_maintainbility(self, oquare_maintainbility):
        self.mutex.acquire()
        self.oquare_maintainbility = oquare_maintainbility
        self.mutex.release()

    def add_oquare_operability(self, oquare_operability):
        self.mutex.acquire()
        self.oquare_operability = oquare_operability
        self.mutex.release()

    def add_oquare_reliability(self, oquare_reliability):
        self.mutex.acquire()
        self.oquare_reliability = oquare_reliability
        self.mutex.release()

    def add_oquare_transferability(self, oquare_transferability):
        self.mutex.acquire()
        self.oquare_transferability = oquare_transferability
        self.mutex.release()

    def add_metrics_ontology(self, metrics_score_array):
        self.mutex.acquire()
        self.ontology_score_array = metrics_score_array
        self.mutex.release()

    def add_new_prediction_class(self, prediction, class_ontology):
        self.mutex.acquire()
        self.prediction_class_map[prediction] = class_ontology
        self.class_prediction_map[class_ontology] = prediction
        self.mutex.release()

    def add_new_title_uri(self, title_entity, uri_entity):
        self.mutex.acquire()
        self.title_uri_map[title_entity] = uri_entity
        self.mutex.release()

    def add_new_datatypes_class(self, class_entity, datatype_list):
        self.mutex.acquire()
        self.datatype_class[class_entity] = datatype_list
        self.mutex.release()

    def add_new_objectype_class(self, class_entity, object_list):
        self.mutex.acquire()
        self.objectype_class[class_entity] = object_list
        self.mutex.release()

    def add_new_map_metadata(self, original_meta, mapped_meta):
        self.mutex.acquire()
        self.object_metadata_map[original_meta] = mapped_meta
        self.mutex.release()

    def add_class_color(self, color, class_name):
        self.mutex.acquire()
        self.class_color[class_name] = color
        self.mutex.release()

    def add_entity_prediction(self, entity, prediction):
        self.mutex.acquire()
        self.entity_prediction[entity] = prediction
        self.mutex.release()

    def new_tmp_class_color(self):
        self.mutex.acquire()
        self.tmp_class_color = list()
        self.mutex.release()

    def add_temp_class_color(self, classcolor):
        self.mutex.acquire()
        self.tmp_class_color.append(classcolor)
        self.mutex.release()

    def add_score_list(self, scores_list):
        self.mutex.acquire()
        self.scores_list = scores_list
        self.mutex.release()

    def add_value_list(self, values_list):
        self.mutex.acquire()
        self.values_list = values_list
        self.mutex.release()
