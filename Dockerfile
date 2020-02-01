FROM python:3.7

RUN mkdir /bot

ADD . /bot

RUN pip install -r /bot/requirements.txt
WORKDIR "/bot"

CMD ["python", "./bot.py"]