FROM nginx:1.19.2-alpine

RUN \
  if [ -d /etc/nginx/sites-enabled/default ]; \
  then rm /etc/nginx/sites-enabled/default; \
  fi

RUN \
  if [ -d /etc/nginx/conf.d/default.conf ]; \
  then rm /etc/nginx/conf.d/default.conf; \
  fi

# set timezone
RUN apk add tzdata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY nginx.conf /etc/nginx/conf.d