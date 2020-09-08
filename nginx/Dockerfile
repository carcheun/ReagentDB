FROM nginx:1.19.2-alpine

RUN \
  if [ -d /etc/nginx/sites-enabled/default ]; \
  then rm /etc/nginx/sites-enabled/default; \
  fi

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d