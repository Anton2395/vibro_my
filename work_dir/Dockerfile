FROM python:3.7

WORKDIR /code

COPY . /code
COPY ./requiremens.txt /code/requiremens.txt
RUN apt-get update
RUN pip3 install --upgrade pip
RUN pip3 install -r /code/requiremens.txt

EXPOSE 5000
CMD ["python", "main.py"]