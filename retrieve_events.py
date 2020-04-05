import datetime as dt
import os
import random
import uuid
from random import randrange

import psycopg2
import pytz
from faker import Faker
from logzero import logger
from tqdm import trange


SYMPTOM_SELECT = """
SELECT ST_X(location::geometry) AS LNG, ST_Y(location::geometry) AS LAT
FROM geotable
WHERE ("timestamp" BETWEEN NOW() - INTERVAL %s AND NOW())
AND {symptom} = True
ORDER BY "timestamp"  DESC;
"""


def get_temperature_events_in_past_48_hrs():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cursor = conn.cursor()
    cursor.execute(SYMPTOM_SELECT.format(symptom='temperature'), ('48 HOURS',))

    return [
        { "lng":  item[0], "lat": item[1]}
        for item in cursor.fetchall()
    ]


def get_cough_events_in_past_48_hrs():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cursor = conn.cursor()
    cursor.execute(SYMPTOM_SELECT.format(symptom='cough'), ('48 HOURS',))

    return [
        { "lng":  item[0], "lat": item[1]}
        for item in cursor.fetchall()
    ]


if __name__ == "__main__":
    print(get_temperature_events_in_past_48_hrs())
    print(get_cough_events_in_past_48_hrs())
