
from transformers import AutoModelForTokenClassification, AutoTokenizer
from transformers import pipeline
from end_point.logging_ita import application_logger
import os

class EntityNerPredictor:
    """
    Python class that uses Huggingface API in order to return the entities of an input String from the NER prediction
    """

    def __init__(self):
        
        model_path = os.environ.get("XML_ROBERTA_LARGE_ENGLISH_MODEL","xlm-roberta-large-finetuned-conll03-english")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForTokenClassification.from_pretrained(model_path)
        self.token_classifier = pipeline(
            "token-classification",
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy="first",
        )

        self.predictions_map_ner = {
            "LOC": "Location",
            "NUMBER": "MeasureProperty",
            "TIME": "Time",
            "PER": "Person",
            "DUR": "MeasureProperty",
            "MISC": "Product",
            "PERSON": "Person",
            "NORP": "Organization",
            "FACILITY": "Location",
            "FAC": "Location",
            "ORG": "Organization",
            "GPE": "Location",
            "PRODUCT": "Product",
            "EVENT": "Event",
            "WORK_OF_ART": "CreativeWork",
            "LAW": "Law",
            "LANGUAGE": "Language",
            "DATE": "Time",
            "PERCENT": 'MeasureProperty',
            "MONEY": "Money",
            "QUANTITY": "MeasureProperty",
            "ORDINAL": 'MeasureProperty',
            "CARDINAL": "MeasureProperty",
        }

    def ner_predict(self, sentence):
        """
        Function which uses transformer models to predict
        """
        entities_list = list()
        try:
            sentence = sentence.strip()

            application_logger.info("NER is starting")

            prediction_list = self.token_classifier(sentence)
            for token_classification in prediction_list:
                try:
                    end = token_classification.get('end')
                    start = token_classification.get('start')
                    word_extracted = sentence[start:end]
                    prediction = token_classification.get('entity_group')
                    new_prediction = self.predictions_map_ner.get(prediction)

                    entities_list.append(
                        (word_extracted, new_prediction)
                    )
                except Exception as ex:
                    error_message=f"""
                    Error detecting entities: {str(ex)}
                    token_classification: {str(token_classification)}
                    sentence: {str(sentence)}
                    """
                    application_logger.error(error_message)
                    application_logger.error(ex, exc_info=True)

            if len(entities_list) > 0:
                application_logger.info(f"Entities detected: {str(entities_list)}")
            else:
                application_logger.error("No entities detected.")
        except Exception as ex:
            application_logger.error(f"Sentence erorr: {str(sentence)} Error:{str(ex)}")
            application_logger.error(ex, exc_info=True)
        return entities_list
