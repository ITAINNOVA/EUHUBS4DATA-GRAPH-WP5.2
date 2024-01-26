# set base image (host OS)
FROM ubuntu:20.04
ENV APP_ROOT="/root/"
ENV JAVA_PATH_JAR /root/java/
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/

RUN apt-get update -y && apt-get install -y software-properties-common unzip && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get install openjdk-8-jdk -y && apt-get install python3-pip -y && export JAVA_HOME \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip
WORKDIR ${APP_ROOT}
# Volume which contains Huggingface models
# it is used just to save time restarting the application
RUN mkdir -p ${APP_ROOT}resources ${APP_ROOT}java ${APP_ROOT}templates ${APP_ROOT}static ${APP_ROOT}models ${APP_ROOT}.cache/huggingface
# USER root
ENV PATH="${APP_ROOT}.local/bin:${PATH}"
ENV PYTHONPATH=.:$PYTHONPATH

ENV PARAPHRASE_XML_MODEL="${APP_ROOT}models/paraphrase-xlm-r-multilingual-v1/"
ADD ./src/main/resources/models/paraphrase-xlm-r-multilingual-v1.zip .
RUN unzip paraphrase-xlm-r-multilingual-v1.zip -d ${APP_ROOT}models/
RUN rm paraphrase-xlm-r-multilingual-v1.zip

ENV BERT_BASE_SPANISH_MODEL="${APP_ROOT}models/bert-base-spanish-wwm-uncased/"
ADD ./src/main/resources/models/bert-base-spanish-wwm-uncased.zip .
RUN unzip bert-base-spanish-wwm-uncased.zip -d ${APP_ROOT}models/
RUN rm bert-base-spanish-wwm-uncased.zip

# bert-base-uncased
ENV BERT_BASE_UNCASED_MODEL="${APP_ROOT}models/bert-base-uncased/"
ADD ./src/main/resources/models/bert-base-uncased.zip .
RUN unzip bert-base-uncased.zip -d ${APP_ROOT}models/
RUN rm bert-base-uncased.zip

# #xlm-roberta-large-finetuned-conll03-english
ENV XML_ROBERTA_LARGE_ENGLISH_MODEL="${APP_ROOT}models/xlm-roberta-large-finetuned-conll03-english/"
ADD ./src/main/resources/models/xlm-roberta-large-finetuned-conll03-english.zip .
RUN unzip xlm-roberta-large-finetuned-conll03-english.zip -d ${APP_ROOT}models/
RUN rm xlm-roberta-large-finetuned-conll03-english.zip

RUN pip install --upgrade pip && pip3 install nltk
ENV DIR_WORDNET_SPA="${APP_ROOT}nltk_data/corpora/wordnet_spa"

# Install NLTK
RUN python3 -c "import nltk;nltk.download('wordnet')"
# Import file which is required to have the wordnet in Spanish
RUN mkdir ${APP_ROOT}nltk_data/corpora/wordnet_spa
RUN unzip ${APP_ROOT}nltk_data/corpora/wordnet.zip -d ${APP_ROOT}nltk_data/corpora
ADD ./src/main/resources/data/wordnet_spa.tar.gz ${APP_ROOT}nltk_data/corpora/wordnet_spa

COPY ./src/main/python/ ${APP_ROOT}
COPY ./src/main/java/ ${APP_ROOT}java/
COPY ./src/main/templates/ ${APP_ROOT}templates/
COPY ./src/main/static/ ${APP_ROOT}static/

RUN pip3 install https://github.com/overhangio/py2neo/releases/download/2021.2.3/py2neo-2021.2.3.tar.gz
RUN pip3 install -r ${APP_ROOT}requirements.txt

CMD ["/usr/bin/python3.8"]