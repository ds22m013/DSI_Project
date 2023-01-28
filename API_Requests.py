import requests
import json
from pandas import json_normalize
import config
from datetime import date, timedelta, datetime
import pandas as pd

#REQUEST FOR BOOKING

def get_BookingAPI_response(id_booking, from_date):
    
    to_date = date.fromisoformat(from_date) + timedelta(days=config.days_hotel)
    
    # URL
    url_booking = "https://booking-com.p.rapidapi.com/v1/hotels/search"
    
    # Headers
    headersBooking = {
        "X-RapidAPI-Key": config.rapidAPI_Key,
        "X-RapidAPI-Host": "booking-com.p.rapidapi.com"
    }
    
    # Parameters
    querystring_booking = {"room_number":"1", 
                   "units":"metric",
                   "order_by":"review_score", # andere Möglichkeiten: popularity,class_ascending,class_descending,distance,upsort_bh,review_score,price
                   "adults_number":"2",
                   "filter_by_currency":"EUR",
                   "locale":"en-gb", 
                   "dest_type":"city",
                   "categories_filter_ids":"class::3,class::4,class::5,free_cancellation::1", # 3 bis 5 Sterne, gratis Stornierung. Alle filter siehe filters_booking.json
                   "page_number":"0",
                   "include_adjacency":"true",
                   "checkin_date": from_date, 
                   "checkout_date": to_date, 
                   "dest_id":id_booking} # Include nearby places. 
    
    # Send request and parse
    response = requests.request("GET", url_booking, headers= headersBooking, params=querystring_booking)
    
    # Parse request and get only relevant data
    dat = pd.DataFrame(response.json()['result'])
    dat['checkin_date'] = from_date
    dat['import_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dat = dat.loc[:, ['city_trans', 'hotel_name', 'min_total_price', 'currencycode', 'longitude', 'latitude', 'review_score', 'checkin_date', 'import_date']]
    return dat


# SKYSCANNER API REQUEST

def get_SkyScannerAPI_response(to_cityCode, to_city, in_date):
    
    # URL
    url = "https://skyscanner44.p.rapidapi.com/search"

    # Parameters
    querystring = {"adults":"1",
                   "origin": "VIE",
                   "destination": to_cityCode,
                   "departureDate": in_date,
                   "currency":"EUR"}

    # Headers
    headers = {
        "X-RapidAPI-Key": config.skyScanner_key,
        "X-RapidAPI-Host": "skyscanner44.p.rapidapi.com"
    }
    
    #Send request
    response = requests.request("GET", url, headers=headers, params=querystring)
    
    # Parse request and get only relevant data
    final = pd.DataFrame(columns = ["time", "duration", "company", "price", "n_connections"])
    for item in response.json()["itineraries"]["buckets"]:
        if (item["id"] == "Best"):
            time = item["items"][0]["legs"][0]["departure"][-8:]
            duration = item["items"][0]["legs"][0]["durationInMinutes"]
            company = item["items"][0]["legs"][0]["carriers"]["marketing"][0]["name"]
            price = item["items"][0]["price"]["raw"]
            n_connections = item["items"][0]["legs"][0]["stopCount"]
            df = pd.DataFrame([[time, duration, company, price, n_connections]], 
                              columns = ["time", "duration", "company", "price", "n_connections"])
            final = pd.concat([final, df], axis = 0)  
    
    final.drop_duplicates(inplace = True)
    final["date"] = in_date
    final["import_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    final["origin"] = "Vienna"
    final["destination"] = to_city
    
    return final