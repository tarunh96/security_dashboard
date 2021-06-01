FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /finding_platform
WORKDIR /finding_platform
ADD requirements.txt /finding_platform/
RUN pip install --upgrade pip && pip install -r requirements.txt
ADD . /finding_platform/
