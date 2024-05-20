FROM python:3.10-alpine

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN apk add --no-cache gcc musl-dev linux-headers python3-dev libpq-dev
RUN pip install -r requirements.txt

COPY . .

CMD python3 bot.py
