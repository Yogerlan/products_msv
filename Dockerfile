FROM python:3.12-alpine
WORKDIR /src
COPY ./requirements.txt /src/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt
COPY ./app /src/app
RUN pytest app -v
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
