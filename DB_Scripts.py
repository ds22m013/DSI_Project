import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import config

# SELECT QUERIES

def get_country_data():
    engine = create_engine(config.postgres_connection_string)
    return pd.read_sql(" SELECT * FROM capital", con=engine)

def get_monument_data():
    engine = create_engine(config.postgres_connection_string)
    return pd.read_sql(" SELECT * FROM monument", con=engine)

def get_hotel_data():
    engine = create_engine(config.postgres_connection_string)
    return pd.read_sql(" SELECT * FROM hotelday", con=engine)

def get_flight_data():
    engine = create_engine(config.postgres_connection_string)
    return pd.read_sql(" SELECT * FROM flight", con=engine)


# INSERT QUERIES

def insert_MonumentsDF(monumentsDF):
    engine = create_engine(config.postgres_connection_string)
    monumentsDF.to_sql('monument', engine, if_exists='replace', index=False)
        
def insert_capitalsDF(capitalsDF):
    engine = create_engine(config.postgres_connection_string)
    capitalsDF.to_sql('capital', engine, if_exists='replace',index=False)

def send_booking_to_DB(dataPD):
    data = dataPD
    selector = {'checkin_date_y': 'checkin_date', 'city_trans': 'city','hotel_name': 'name', 'price_per_day': 'price', 'longitude': 'longitude', 'latitude': 'latitude', 'review_score': 'rating', 'import_date' : 'import_date' }
    engine = create_engine(config.postgres_connection_string)
    dataPD = dataPD.rename(columns=selector)[[*selector.values()]]
    dataPD.to_sql('hotelday', engine, if_exists='replace',index=False)

def send_skyscanner_to_DB(data):
    engine = create_engine(config.postgres_connection_string)
    data.to_sql('flight', engine, if_exists='replace',index=False)    

    
# CREATE QUERIES
        
def create_tables():
    engine = create_engine(config.postgres_connection_string)
    with engine.connect() as conn:
        a = conn.execute("CREATE TABLE IF NOT EXISTS capital ( \
                            c_id SERIAL, \
                            capital VARCHAR(30) UNIQUE, \
                            country VARCHAR(30), \
                            dest_id_booking NUMERIC, \
                            airport_code VARCHAR(5) \
                       );")

        a = conn.execute("CREATE TABLE IF NOT EXISTS monument ( \
                            m_id SERIAL, \
                            name VARCHAR(80), \
                            country VARCHAR(30), \
                            longitude NUMERIC, \
                            latitude NUMERIC, \
                            PRIMARY KEY (name, country) \
                      );");

        conn.execute("CREATE TABLE IF NOT EXISTS hotelday ( \
                            h_id SERIAL, \
                            checkin_date DATE, \
                            city VARCHAR(30), \
                            name VARCHAR(50), \
                            price NUMERIC, \
                            longitude NUMERIC, \
                            latitude NUMERIC, \
                            rating NUMERIC, \
                            import_date VARCHAR(10) \
                        );");

        conn.execute("CREATE TABLE IF NOT EXISTS flight ( \
                            f_id SERIAL, \
                            date DATE, \
                            time TIME, \
                            arrival_time TIME, \
                            duration NUMERIC, \
                            origin VARCHAR(30), \
                            destination VARCHAR(30), \
                            company VARCHAR(50), \
                            price NUMERIC, \
                            n_connections NUMERIC, \
                            import_date TIMESTAMP \
                        );");
        conn.close()

        
# CLEAR DB
    
def clear_Database():
    engine = create_engine(config.postgres_connection_string)
    with engine.connect() as conn:
        conn.execute("DROP TABLE capital; \
                      DROP TABLE monument; \
                      DROP TABLE hotelday; \
                      DROP TABLE flight");
        conn.close()

        

    
