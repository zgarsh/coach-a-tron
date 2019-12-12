import os
import schedule
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

twilio_account_sid = os.environ['TWILIO_ACCOUNT_SID']
twilio_auth_token = os.environ['TWILIO_AUTH_TOKEN']
twilio_number = os.environ['TWILIO_NUMBER']
my_number = os.environ['MY_NUMBER']

client = Client(twilio_account_sid, twilio_auth_token)

app = Flask(__name__)

def send_sms():

    body = "it's nine thirty eight!"

    to = my_number,
    client.messages.create(
        to,
        from_=twilio_number,
        body=body)


schedule.every().day.at("22:06").do(send_sms)

while True:
    schedule.run_pending()


if __name__ == '__main__':
    app.run()