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


# global time
current_date = dt.datetime(2020, 1, 27, tzinfo=pytz.UTC)

# Time between events is currently uniformly distributed
# Consider Poisson distribution or other
MAX_NUM_SECS_BETWEEN_EVENTS = 2 * 60 * 60
MAX_MOBILITY = 10

Faker.seed(0)
fake = Faker('sk_SK')


class FakeUser:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.home_location = fake.local_latlng(country_code='SK')
        self.mobility =  MAX_MOBILITY * random.random()
        self.general_health = random.random()

    def sample(self):
        """Create a sample event"""

        global current_date # consider an alternative
        random_second = MAX_NUM_SECS_BETWEEN_EVENTS * random.random()
        current_date = current_date + dt.timedelta(seconds=random_second)
        data = {
           'user_id': self.id,
           'timestamp': current_date,
           'location': {
               'lat': fake.coordinate(
                   center=self.home_location[0],
                   radius=self.mobility
                ),
               'lng': fake.coordinate(
                   center=self.home_location[1],
                   radius=self.mobility
                )
           },
           'cough': random.random() > self.general_health,
           'temperature': random.random() > self.general_health,
        }

        return data


def persist_datapoint(conn, data):
    INSERT_EVENT = """
INSERT INTO geotable (user_id, timestamp, location, cough, temperature)
VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s)
"""

    cursor = conn.cursor()

    cursor.execute(
        INSERT_EVENT, (
            data['user_id'],
            data['timestamp'],
            data['location']['lat'],
            data['location']['lng'],
            data['cough'],
            data['temperature'],
       )
    )
    conn.commit()


if __name__ == "__main__":
    fake_users = [FakeUser()]

    NUM_EVENTS = 150
    R0_star = 1.01 
    new_user_proba = 0.01

    conn = psycopg2.connect(
        host=os.getenv('DBHOST'),
        dbname=os.getenv('DBNAME'),
        user=os.getenv('DBUSER'),
        password=os.getenv('DBPASSWORD')
    )

    for _ in range(NUM_EVENTS):
        if new_user_proba > random.random():
            logger.debug('New user creation')
            fake_users.append(FakeUser())

        new_user_proba *= R0_star

        user = random.choice(fake_users)
        logger.debug(f'Selected user {user.id}')
        data = user.sample()
        logger.info(data)
        persist_datapoint(conn, data)

    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM geotable;')
    print(cursor.fetchone()[0])
