FROM python:latest

ADD requirements.txt /

RUN pip install -r requirements.txt

ADD closeNotes.py .

CMD [ "python3", "closeNotes.py" ]