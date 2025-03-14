import os
import requests
from twilio.rest import Client
from dotenv import find_dotenv, load_dotenv
import datetime as dt

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

stock_api = os.getenv("STOCK_API_KEY")
news_api = os.getenv("NEWS_API_KEY")
twilio_sid = os.getenv("TWILIO_SID")
twilio_api = os.getenv("TWILIO_API_KEY")

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

title_list = []
description_list = []

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

stock_query = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "outputsize": "full",
    "apikey": stock_api
}

news_query = {
    "apiKey": news_api,
    "q": COMPANY_NAME,
}

sign = "🔺 "

response = requests.get(STOCK_ENDPOINT, params=stock_query)
response.raise_for_status()
data = response.json()

def get_news():
    response = requests.get(NEWS_ENDPOINT, params=news_query)
    response.raise_for_status()
    data = response.json()

    articles = data["articles"]

    for article in articles[:3]:
        title_list.append(article["title"])
        description_list.append(article["description"])

stock_data = data["Time Series (Daily)"]
stock_list = list(stock_data)

yesterday = stock_list[0]
day_before_yesterday = stock_list[1]

y_close = float(stock_data[yesterday]["4. close"])
dby_close = float(stock_data[day_before_yesterday]["4. close"])

diff = y_close - dby_close
average = (y_close + dby_close)/2
percentage = (diff / average) * 100

if diff < 0:
    sign = "🔻 "
    percentage *= -1

percentage = round(percentage, 2)
if percentage > 0:
    get_news()

    message_sms = f"{STOCK_NAME}: {sign}{percentage}%"
    message_news = f"Headline: {title_list[0]}\nBrief: {description_list[0]}"

    # Print the message to be sent via Twilio for debugging
    print("Message to be sent via Twilio")

    try:
        client = Client(twilio_sid, twilio_api)
        message = client.messages.create(
            from_="+16319864093",
            body=message_sms,
            to="+919842852121"
        )
        print(f"Message overview status: {message.status}")

        client = Client(twilio_sid, twilio_api)
        message = client.messages.create(
            from_="+16319864093",
            body=message_news,
            to="+919842852121"
        )
        print(f"Message news status: {message.status}")
    except Exception as e:
        print(f"An error occurred while sending the message: {e}")