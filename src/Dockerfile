FROM python:3.8

RUN python3 -m venv .venv

RUN .venv/bin/python3 -m pip install --upgrade pip

COPY requirements.txt app/requirements.txt
RUN .venv/bin/pip3 install -r app/requirements.txt

COPY app ./app

CMD [".venv/bin/uvicorn", "app.main:app", "--host=0.0.0.0" ]
# CMD ["tail", "-f", "/dev/null"]
