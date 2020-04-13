import datetime as dt
import os
import random
import uuid
from random import randrange

import psycopg2
import pytz
from faker import Faker
from faker.providers.geo import Provider
from logzero import logger
from tqdm import trange

import sk_municipality_provider

Provider.land_coords = Provider.land_coords + sk_municipality_provider.LAND_COORDS



# global time
current_date = dt.datetime(2020, 1, 27, tzinfo=pytz.UTC)

# Time between events is currently uniformly distributed
# Consider Poisson distribution or other
MAX_NUM_SECS_BETWEEN_EVENTS = 2 * 60 * 60
MAX_MOBILITY = 0.5

Faker.seed(0)
fake = Faker('sk_SK')


#%%

class FakeUser:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.home_location = fake.local_latlng(country_code='SK')
        self.mobility =  MAX_MOBILITY * random.random()
        self.general_health = random.random()
        self.age = 18 + 80 * random.random()
        self.sex = random.choice(['M', 'F', 'Other'])

        self.exposure_abroad = random.random() > 0.9
        self.exposure_to_quarantined_or_sick = random.random() > 0.9

    def sample(self):
        """Create a sample event"""

        global current_date # consider an alternative
        random_second = MAX_NUM_SECS_BETWEEN_EVENTS * random.random()
        current_date = current_date + dt.timedelta(seconds=random_second)
        
        temperature = 36 + 4 * (1 - self.general_health) * random.random()
        symptoms = {
            'dry_cough': random.random() > self.general_health,
            'fever': temperature >= 38,
            'temperature_under_38': temperature < 38,
            'temperature_over_38': temperature >= 38,
            'temperature_idk': False,
            'difficulty_breathing': random.random() > self.general_health,
            'headache': random.random() > self.general_health,
            'taste_and_smell_loss': random.random() > self.general_health,
            'headache': random.random() > self.general_health,
            'sore_throat': random.random() > self.general_health,
            'weakness': random.random() > self.general_health,
            "chest_pain": random.random() > self.general_health,
            "chills": random.random() > self.general_health,
            "sweating": random.random() > self.general_health,
            "stuffy_nose": random.random() > self.general_health,
            "runny_nose": random.random() > self.general_health,
            "diarrhea": random.random() > self.general_health,
            "watery_itchy_eyes": random.random() > self.general_health,

        }
    
        
        asymptomatic = not any(symptoms.values())
        data = {
            'customer_id': self.id,
            'age': int(self.age),
            'sex': self.sex,
            'lat': float(fake.coordinate(
                 center=self.home_location[0],
                 radius=self.mobility
            )),
            'lon': float(fake.coordinate(
                 center=self.home_location[1],
                 radius=self.mobility
            )),
            # INFO: location must go away, for real data add lat - lon
            'location_iq': {"address": ""},
            'symptoms': symptoms,
             **symptoms,
            "nonsymptomatic": asymptomatic,

            # 3. Other important information
            'exposure_abroad': self.exposure_abroad,
            'exposure_to_quarantined_or_sick': self.exposure_to_quarantined_or_sick,
            'test_time': dt.datetime.now(tz=pytz.UTC),
            "test_result": random.random() > 0.99,
        }

        return data

# def persist_datapoint(conn, data):
#     INSERT_EVENT = """
# INSERT INTO geotable (customer_id, timestamp, location, age, sex, symptoms, cough, fever, dificulty_breathing, weakness, headache, taste_and_smell_loss, nonsymptomatic)
# VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
# """

#     cursor = conn.cursor()

# #   id serial PRIMARY KEY,
# #   customer_id VARCHAR(36),
# #   timestamp TIMESTAMP,
# #   location geography(POINT, 4326),
# #   age int,
# #   sex VARCHAR(100),
# #   symptoms json,
# #   cough boolean,
# #   fever boolean,
# #   dificulty_breathing boolean,
# #   weakness boolean,
# #   headache boolean,
# #   taste_and_smell_loss boolean,
# #   nonsymptomatic boolean

#     cursor.execute(
#         INSERT_EVENT, (
#             data['customer_id'],
#             data['timestamp'],
#             data['location']['lat'],
#             data['location']['lng'],
#             data['age'],
#             data['sex'],
#             data['dry_cough'],
#             data['fever'],
#             data['dificulty_breathing'],
#             data['weakness'],
#             data['headache'],
#             data['taste_and_smell_loss'],
#             data['nonsymptomatic'],
#        )
#     )
#     conn.commit()




def persist_datapoint(conn, content):
    cursor = conn.cursor()
    # Variables to insert into postgres
    # FIX: this should not be customer id but some expirable customer/user token
    customer_id = content['customer_id']
    lat = content['lat']
    lon = content['lon']

    # 2a. Main symptoms
    dry_cough = content["dry_cough"]
    fever = content["fever"]
    temperature_under_38 = content["temperature_under_38"]
    temperature_idk = content["temperature_idk"]
    temperature_over_38 = content["temperature_over_38"]
    taste_and_smell_loss = content["taste_and_smell_loss"]
    difficulty_breathing = content["difficulty_breathing"]
    # 2b. Other symptoms
    headache = content["headache"]
    sore_throat = content["sore_throat"]
    weakness = content["weakness"]
    chest_pain = content["chest_pain"]
    chills = content["chills"]
    sweating = content["sweating"]
    stuffy_nose = content["stuffy_nose"]
    runny_nose = content["runny_nose"]
    diarrhea = content["diarrhea"]
    watery_itchy_eyes = content["watery_itchy_eyes"]
    # 3. Other important information
    exposure_abroad = content["exposure_abroad"]
    exposure_to_quarantined_or_sick = content["exposure_to_quarantined_or_sick"]
    test_time = content["test_time"]
    test_result = content["test_result"]
    # TODO REMOVE too detailed information BEFORE LIVE
    location_iq = {"address": ""} #reverse_geocode_locationiq(lat, lon)

    # Remember to close SQL resources declared while running this function.
    # Keep any declared in global scope (e.g. pg_pool) for later reuse.
    
    sql = f"""INSERT INTO symptom_report (
            -- STUFF
            customer_id, updated_at, 
            -- MAIN SYMPTOMS
            dry_cough, fever,
            temperature_under_38, temperature_idk, temperature_over_38, 
            taste_and_smell_loss, difficulty_breathing,
            -- SECONDARY SYMPTOMS
            headache,sore_throat,weakness,chest_pain,chills,sweating,stuffy_nose,runny_nose,
            diarrhea,watery_itchy_eyes,
            -- OTHER
            exposure_abroad,exposure_to_quarantined_or_sick,test_time,test_result,
            -- LOCATION
            latlon,
            address
        ) VALUES (
            -- STUFF
            %s, NOW(), 
            -- MAIN SYMPTOMS
            {dry_cough}, {fever},
            {temperature_under_38}, {temperature_idk}, {temperature_over_38},
            {taste_and_smell_loss}, {difficulty_breathing},
            -- SECONDARY SYMPTOMS
            {headache},{sore_throat},{weakness},{chest_pain},{chills},{sweating},{stuffy_nose},{runny_nose},
            {diarrhea},{watery_itchy_eyes},
            -- OTHER
            {exposure_abroad},{exposure_to_quarantined_or_sick},(%s),{test_result},
            -- LOCATION
            ST_SetSRID(ST_Point({lat}, {lon}), 4326)::geography, 
            %s
        ) RETURNING customer_id;"""

    # TODO: fix all the SQL injections - either use SQLAlchemy or similar, or at least a dict with the value names,
    # definitely not string interpolations 
    cursor.execute(sql, (customer_id, test_time,'{}'))
    conn.commit()



import requests

def post_datapoint(data):
    res = requests.post('https://europe-west3-hackthevirus.cloudfunctions.net/insert_location', json=data)
    breakpoint()
    print(res.json())
    return res.json()

if __name__ == "__main__":
    fake_users = [FakeUser()]

    NUM_EVENTS = 15000
    R0_star = 1.01
    new_user_proba = 0.01

    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

    for _ in range(NUM_EVENTS):
        if new_user_proba > random.random():
            # logger.debug('New user creation')
            fake_users.append(FakeUser())
            logger.debug(f'user {fake_users[-1].home_location}')

        new_user_proba *= R0_star

        user = random.choice(fake_users)
        # logger.debug(f'Selected user {user.home_location}')
        data = user.sample()
        # logger.info(data)
        print(data)
        
        # posted = post_datapoint(data)
        
        persist_datapoint(conn, data)

    # cursor = conn.cursor()
    # cursor.execute('SELECT COUNT(*) FROM geotable;')
    # print(cursor.fetchone()[0])
