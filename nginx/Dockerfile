FROM nginx

RUN \
  if [-d /etc/nginx/sites-enabled/default ]; \
  then rm /etc/nginx/sites-enabled/default; \
  fi

#RUN rm /etc/nginx/sites-enabled/default

COPY sites-enabled/ /etc/nginx/sites-enabled