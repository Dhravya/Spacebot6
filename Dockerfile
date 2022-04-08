FROM python:3.9-slim
RUN apt-get update && apt-get install -y git

COPY ./requirements.txt .
RUN pip install -r requirements.txt

RUN pip uninstall -y discord
RUN pip uninstall -y py-cord
RUN pip install git+https://github.com/pycord-development/pycord

COPY ./src ./src
COPY .env .env 
CMD ["python", "src/main.py"]