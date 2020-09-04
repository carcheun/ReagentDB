# pull python base image from https://hub.docker.com/_/python
FROM python:3.7-alpine

# set work directory
#WORKDIR C:\\Users\\engineer\\source\\repos\\ReagentDB\\web

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apk update
RUN python -m pip install --upgrade pip
COPY requirements.txt .
RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 python -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

# copy project
COPY . .