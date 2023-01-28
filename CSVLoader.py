# Libraries
import pandas as pd
import DB_Scripts

def create_start_DB():
    
    # Create Tables
    DB_Scripts.create_tables()
    
    # MONUMENTS 
    #Read CSV in a dataframe
    monumentsDF = pd.read_csv("Data//Monuments1000.csv", delimiter = ";", decimal = ",")
    monumentsDF = monumentsDF[["name", "country", "longitude", "latitude"]]
    # Insert DF in DB
    DB_Scripts.insert_MonumentsDF(monumentsDF)
    
    # CAPITALS
    # Read CSV in a dataframe and filter to only european
    capitalsDF = pd.read_csv("Data//Capitals_clean.csv", delimiter = ";", decimal = ",")
    # Insert entries in DB
    DB_Scripts.insert_capitalsDF(capitalsDF)