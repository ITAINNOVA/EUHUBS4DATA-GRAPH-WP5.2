
FROM nginx:alpine
RUN apk update  && apk add apache2-utils
COPY ./src/main/nginx/default_cert.conf /etc/nginx/conf.d/default.conf