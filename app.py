# -*- coding: utf-8 -*-
import os
import random
import requests
import json
# import pandas
import psycopg2
import time

from datetime import datetime, timedelta
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

# set env variables
twilio_account_sid = os.environ['TWILIO_ACCOUNT_SID']
twilio_auth_token = os.environ['TWILIO_AUTH_TOKEN']
twilio_number = os.environ['TWILIO_NUMBER']
my_number = os.environ['MY_NUMBER']
DATABASE_URL = os.environ['DATABASE_URL']

# create twilio client object
client = Client(twilio_account_sid, twilio_auth_token)

dt = datetime

# TODO: this is bad! find out the proper way to convert time zones
# convert from GMT to PST
def get_time():
    current_time = dt.now() - timedelta(hours=8)
    return current_time

app = Flask(__name__)


# configure your race
race_name = "Berlin Marathon"
race_day = dt(year=2020, month=9, day=27)


# get daily assignment
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

def get_random_inspirational_quote():

    quote_bank = (
        '"Today, do what others won’t so tomorrow you can accomplish what others can’t." - Jerry Rice ',
        '"The reward is not so great without the struggle." - Wilma Rudolph',
        '"I only start counting once it starts hurting." - Muhammad Ali',
        '"There may be people that have more talent than you, but there’s no excuse for anyone to work harder than you do." - Derek Jeter',
        '"It’s not the will to win that matters — everyone has that. It’s the will to prepare to win that matters." - Paul Bryant',
    )

    quote = random.choice(quote_bank)

    return quote

def get_countdown_message_text():
    days_remaining = race_day - get_time()
    days_remaining = days_remaining.days

    print('getting countdown text')
    
    return "{} days until the {}!".format(days_remaining, race_name)


def assemble_poke_message():

    # message_text = 'the current time is: ' + str(get_time()) + '\n \n' + 'and the current day is: ' + str(get_time().weekday()) + '\n \n' + get_countdown_message_text() + '\n \n' + get_distance_message_text()

    message_text = get_random_inspirational_quote() + '\n \n' +  get_countdown_message_text() + '\n \n' + get_distance_message_text() + "\n \n here's a song you might like: https://open.spotify.com/track/5Ihd9HrPvOADyVoonH9ZjB?si=__ClQa_GSCCYlL9LLyYSKw"

    return message_text


def send_a_message(body):

    message = client.messages.create(
            body=body,
            from_=twilio_number,
            to=my_number
        )
    
    return None





def get_current_token_if_valid():
    """Checks DB for oauth stuff. If existing creds are still valid it returns them as a dict which can be 
    passed to store_new_token_info() and get_dat_data()."""
    
    print('checking if current access_token is valid')
    
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    
    cur.execute("SELECT refresh_expiration, refresh_token, access_token FROM oauth WHERE id = 1;")
    oauth_data = cur.fetchone()

    cur.close()
    conn.close()
    
    current_time = int(time.time())
    
    current_timestamp = dt.utcfromtimestamp(current_time)
    expiry_timestamp = dt.utcfromtimestamp(oauth_data[0])
    
    print('current time UTC: ' + str(current_timestamp))
    print('access_token will expire at (UTC): ' + str(expiry_timestamp))
    
    if current_time < oauth_data[0]:
        
        creds = {
            'new_refresh_token': oauth_data[1],
            'new_access_token': oauth_data[2],
            'refresh_expiration': oauth_data[0]
        }
        
        return creds
    
    return False


# - get new token data from strava
def get_new_token():
    """hits up Strava for a new access token and refresh token and returns dict which can be passed to
    store_new_token_info() (which should be called to persist new info) and get_dat_data()."""
    
#     first, get supplies for making token refresh API call
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    cur.execute("SELECT grant_type, refresh_token, client_id, client_secret FROM oauth;")
    result = cur.fetchall()[0]

    if result:
        print("query for refresh token deets completed successfully")

    if(conn):
        cur.close()
        conn.close()
        print("postgres connection for refresh token deets has been closed")

    grant_type, refresh_token, client_id, client_secret = result[0], result[1], result[2], result[3]
    
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": grant_type
    }

    response = requests.post("https://www.strava.com/oauth/token", params=params)
    
    return {
            'new_refresh_token': response.json()['refresh_token'],
            'new_access_token': response.json()['access_token'],
            'refresh_expiration': response.json()['expires_at']
           }

    
# - read/write from db token data (access, refresh, expiration date)
def store_new_token_info(token_dict):
    """stores passed token_dict to oauth table in DB"""
    
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    cur.execute("UPDATE oauth SET access_token = '{}', refresh_token = '{}', refresh_expiration = {} WHERE id = 1;".format(token_dict['new_access_token'], token_dict['new_refresh_token'], token_dict['refresh_expiration']))
    conn.commit()

    if(conn):
        cur.close()
        conn.close()
        print("PostgreSQL connection is closed")


# - get actual data from strava
def get_dat_data(token_dict):
    
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    cur.execute("SELECT grant_type, access_token, client_id, client_secret FROM oauth WHERE id = 1;")
    result = cur.fetchall()[0]

    if result:
        print("query for refresh token deets completed successfully")

    if(conn):
        cur.close()
        conn.close()
        print("postgres connection for refresh token deets has been closed")

    grant_type, access_token, client_id, client_secret = result[0], result[1], result[2], result[3]

    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "access_token": access_token,
        "grant_type": "authorization_code"
    }

    response = requests.get("https://www.strava.com/api/v3/activities", params=params)
    
    return response.json()

def write_new_run_data_if_present(json):
    
    print('checking most recent run timestamp')
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute("SELECT MAX(start_date_local) FROM runs;")
    max_timestamp = cur.fetchone()[0]
    
    print('most recent run occurred at: ', max_timestamp)
    
    if not max_timestamp:
        print('runs table is empty. adding all runs returned from strava, but beware page limit!')
        max_timestamp = dt(2011, 11, 11) #'2000-11-11T11:11:11Z'
    
    for json_run in json:
        run_datetime = dt.strptime(json_run['start_date_local'], '%Y-%m-%dT%H:%M:%SZ')
        if run_datetime > max_timestamp and json_run['type'] == 'Run':
            
            print('found new run with timestamp: ',  run_datetime)
            run_id = json_run['id']
            start_timestamp = "'" + json_run['start_date_local'] + "'"
            average_speed = json_run['average_speed']
            max_speed = json_run['max_speed']
            distance = json_run['distance']
            elapsed_time = json_run['elapsed_time']
            moving_time = json_run['moving_time']
            total_elevation_gain = json_run['total_elevation_gain']
            
            
            sql = '''INSERT INTO runs (id, start_date_local, average_speed, max_speed, distance, elapsed_time, moving_time, total_elevation_gain)
            VALUES ({}, {}, {}, {}, {}, {}, {}, {})'''.format(run_id, start_timestamp, average_speed, max_speed, distance, elapsed_time, moving_time, total_elevation_gain)

            cur.execute(sql)
            conn.commit()
            
    if(conn):
        cur.close()
        conn.close()
        print('DB connection closed')
    
    
    return


def data_kitten_kaboodle():
    """ This function pieces together all the pieces to get updated DB credentials for oauth, make API call to get run data, and record """
#     get oauth credz from oauth table, check if they're still good, get new ones if not
    creds = get_current_token_if_valid()
    if not creds:
        creds = get_new_token()
        store_new_token_info(creds)
    
#     see if new data is present and write to DB
    write_new_run_data_if_present(get_dat_data(creds))
    
    return

def get_most_recent_run():
    
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    cur.execute("SELECT * FROM runs WHERE runs.start_date_local = (SELECT MAX(start_date_local) FROM runs) LIMIT 1")
    last_run_tuple = cur.fetchone()
    
    last_run = {
        'id': last_run_tuple[0],
        'start_date_local': last_run_tuple[1],
        'average_speed': last_run_tuple[2],
        'max_speed': last_run_tuple[3],
        'distance': last_run_tuple[4],
        'elapsed_time': last_run_tuple[5],
        'moving_time': last_run_tuple[6],
        'total_elevation_gain': last_run_tuple[7],
    }

    cur.close()
    conn.close()
    
    return last_run









# Make magic
@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():

    # log incoming message for debugging
    print('message from:', request.values['From'])
    message_body = request.form['Body']
    print('message:', message_body)


    # responseText = assemble_message()

    # resp = MessagingResponse()
    # resp.message(responseText)

    if message_body in ("How far have I run?", "how far have I run?", "how far have i run?"):
        text = "You have run a lot of miles! that's the equivalent of running from here to a far away place!"
    elif message_body in ("How many days?", "How long?", "How much time?"):
        text = get_countdown_message_text()
    elif message_body in ("Inspire me"):
        text = get_random_inspirational_quote()
    
    else:
        text = "Keep up the good work!"

    return send_a_message(text)

# Send poke message when poked by cron job
@app.route("/morning-poke", methods=['GET', 'POST'])
def sms_prompt():

    print('replying')

    return send_a_message(assemble_poke_message())


# Send poke message when poked by cron job
@app.route("/evening-poke", methods=['GET', 'POST'])
def evening_actions():

    data_kitten_kaboodle()

    most_recent_run = get_most_recent_run()['start_date_local']

    text = "Your most recent run was on {}".format(str(most_recent_run))

    return send_a_message(text)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
