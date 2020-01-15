# -*- coding: utf-8 -*-
import os
from datetime import datetime, timedelta
# import schedule
# import logging

from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

# set env variables
twilio_account_sid = os.environ['TWILIO_ACCOUNT_SID']
twilio_auth_token = os.environ['TWILIO_AUTH_TOKEN']
twilio_number = os.environ['TWILIO_NUMBER']
my_number = os.environ['MY_NUMBER']

# create twilio client object
client = Client(twilio_account_sid, twilio_auth_token)

dt = datetime

# convert from GMT to PST
def get_time():
    current_time = dt.now() - timedelta(hours=8)
    return current_time

app = Flask(__name__)


# configure your race
race_name = "Berlin Marathon"
race_day = dt(year=2020, month=9, day=27)


# determine daily assignment
def get_distance_message_text():
    day_of_week = get_time().weekday()
    
    distance_mapping = {
        0: 'rest!',
        1: 'run three miles.',
        2: 'run four miles.',
        3: 'run three miles.',
        4: 'rest!',
        5: 'run six miles.',
        6: 'do some cross training'
    }

    print('getting distance text')
    
    return "Today's assignment is to {}".format(distance_mapping[day_of_week])


def get_countdown_message_text():
    days_remaining = race_day - get_time()
    days_remaining = days_remaining.days

    print('getting countdown text')
    
    return "{} days until the {}!".format(days_remaining, race_name)


def assemble_message():

    message_text = 'the current time is: ' + str(get_time()) + '\n \n' + 'and the current day is: ' + str(get_time().weekday()) + '\n \n' + get_countdown_message_text() + '\n \n' + get_distance_message_text()

    return message_text


# Make magic
@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():

    # log incoming message for debugging
    print('message from:', request.values['From'])
    message_body = request.form['Body']
    print('message:', message_body)


    responseText = assemble_message()

    resp = MessagingResponse()
    resp.message(responseText)


    return str(resp)

@app.route("/", methods=['GET', 'POST'])
def sms_prompt():

    # log incoming message for debugging
    # print('message from:', request.values['From'])
    # message_body = request.form['Body']
    # print('message:', message_body)


    responseText = "replying to cron job" #assemble_message()

    resp = MessagingResponse()
    resp.message(responseText)


    return str(resp)




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
