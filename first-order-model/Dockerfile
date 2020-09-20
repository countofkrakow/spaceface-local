FROM 694126695710.dkr.ecr.us-west-2.amazonaws.com/first_order_model_base:latest

RUN pip3 install -r requirements.txt

COPY faced /app/faced
WORKDIR /app/faced
RUN python3 setup.py install

COPY . /app
WORKDIR /app

CMD ["python3", "processor.py"]
