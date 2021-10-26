FROM python:3.10.0
WORKDIR /code

COPY requirements.txt .
RUN pip install --user -r requirements.txt
COPY src/ .

ENV PATH=/root/.local:$PATH

CMD [ "python", "-u", "main.py" ]
