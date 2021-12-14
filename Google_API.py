import urllib.request, urllib.parse, urllib.error
import requests
import json
import ssl
import csv
import math
import os
import re
import pandas as pd
import numpy as np
from haversine import haversine, Unit
from fastDamerauLevenshtein import damerauLevenshtein

def grade(row, name, coordinates, state, street_number_short, street_number_long, street_name_short, street_name_long, postal):

    score = 100

    # name

    if damerauLevenshtein(name, row['name'])*100 < 60:
        score -= 20

    # address

    if len(str(row['address'])) == 0 or len(str(street_number_short)) == 0 or len(str(street_number_long)) == 0 or \
        len(str(street_name_short)) == 0 or len(str(street_name_short)) == 0:
        score -= 20
    else:
        if damerauLevenshtein(str(street_number_short) + ' ' + str(street_name_short).lower(), str(row['address']).lower())*100 < 70 and \
            damerauLevenshtein(str(street_number_short) + ' ' + str(street_name_long).lower(), str(row['address']).lower())*100 < 70 and \
            damerauLevenshtein(str(street_number_long) + ' ' + str(street_name_short).lower(), str(row['address']).lower())*100 < 70 and \
            damerauLevenshtein(str(street_number_long) + ' ' + str(street_name_long).lower(), str(row['address']).lower())*100 < 70:
            score -= 20

    # postal code

    pc = str(row['postal_code'])
    if len(pc) == 4: 
        pc = '0'+re.sub(',', '', pc)

    if damerauLevenshtein(postal, pc)*100 < 90:
        score -= 20

    # state

    if len(row['state']) == 0:
        score -= 20
    else:
        if str(state) != str(row['state']):
            score -= 20

    # coordinates

    if haversine(coordinates, (float(row['latitude']), float(row['longitude'])), unit='m') > 100:
        score -= 20

    return score

def haver_score(value):
    if value >= 100:
        return 0
    else:
        return 100 - value

def score_for_details(row, bunch):
    return sorted(bunch, key=lambda e: damerauLevenshtein(e[0], row['name'])*70 + haver_score(haversine(e[2], (float(row['latitude']), float(row['longitude'])), unit='m'))*0.3, reverse=True)

def places_details(name, place_id, coordinates, api_key, serviceurl_details, payload, headers, row, sample, row_index):
    
    google_data = pd.DataFrame(columns=['yelp_id', 'place_id', 'name', 'street_name', 'city', 'county', 'state', 'postal_code', 'coordinates', 'rating', 'review_count', 'business_status', 'category', 'hours'])
    parms_details = dict()
    parms_details['place_id'] = place_id
    parms_details['key'] = api_key

    response_details, js_details, success = pull_data(serviceurl_details, parms_details, payload, headers)

    if not success:
        return success

    state = np.NaN; postal = np.NaN; city_short = np.NaN; city_long = np.NaN
    street_number_short = np.NaN; street_number_long = np.NaN; street_name_short = np.NaN; street_name_long = np.NaN; county = np.NaN
    formatted_address = np.NaN; open_closed = np.NaN; hours = np.NaN; category = np.NaN; num_ratings = np.NaN; rating = np.NaN

    for component in js_details['result']['address_components']:
        if component['types'][0] == 'administrative_area_level_1':
            state = component['short_name']
        elif component['types'][0] == 'postal_code':
            postal = component['short_name']
        elif component['types'][0] == 'street_number':
            street_number_short = component['short_name']
            street_number_long = component['long_name']
        elif component['types'][0] == 'route':
            street_name_short = component['short_name']
            street_name_long = component['long_name']
        elif component['types'][0] == 'administrative_area_level_2':
            county = component['short_name']
        elif component['types'][0] == 'locality':
            city_short = component['short_name']
            city_long = component['long_name']

    try:
        formatted_address = js_details['result']['formatted_address']
    except:
        formatted_address = np.NaN
    try:
        open_closed = js_details['result']['business_status'] 
    except:
        open_closed = np.NaN
    try:
        hours = js_details['result']['opening_hours']['weekday_text']
    except:
        hours = np.NaN
    try:
        category = js_details['result']['types']
    except:
        category = np.NaN
    try: 
        num_ratings = js_details['result']['user_ratings_total']
    except:
        num_ratings = np.NaN
    try:
        rating = js_details['result']['rating']
    except:
        rating = np.NaN

    google_data.at[row_index, 'yelp_id'] = row['business_id']
    google_data.at[row_index, 'name'] = name
    google_data.at[row_index, 'place_id'] = place_id
    google_data.at[row_index, 'coordinates'] = coordinates
    google_data.at[row_index, 'street_name'] = str(street_number_short) + ' ' + str(street_name_short)
    google_data.at[row_index, 'postal_code'] = postal
    google_data.at[row_index, 'city'] = city_short
    google_data.at[row_index, 'county'] = county
    google_data.at[row_index, 'state'] = state
    google_data.at[row_index, 'category'] = category
    google_data.at[row_index, 'hours'] = hours
    google_data.at[row_index, 'business_status'] = open_closed
    google_data.at[row_index, 'review_count'] = num_ratings
    google_data.at[row_index, 'rating'] = rating

    google_data.to_csv('google_data.csv', index=False, header=False, mode='a') 

    # write match details into copy of yelp dataset

    sample['matched'][row_index] = ['name: '+str(name), 'full address: '+str(formatted_address), 'coordinates: '+str(coordinates), 'postal code: '+str(postal), 'state: '+str(state)]
    sample['confidence'][row_index] = grade(row, name, coordinates, state, street_number_short, street_number_long, street_name_short, street_name_long, postal)

    return True, sample, js_details


def pull_data(serviceurl, parms, payload, headers):

    success = True
    url = serviceurl + urllib.parse.urlencode(parms)
    print('url', url)
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)

    try:
        js = json.loads(response.text)
    except:
        js = None

    if not js or 'status' not in js or js['status'] != 'OK':
        print('==== Failure To Retrieve ====')
        success = False

    print(json.dumps(js, indent=4))

    return response, js, success

def seek(sample, google_data):

    payload = {}
    headers = {}

    api_key = 'x'
    serviceurl_search = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
    serviceurl_details = 'https://maps.googleapis.com/maps/api/place/details/json?'

    json_search = open('search.json', 'w') 
    json_details = open('details.json', 'w')
   
    for row_index, row in sample.iterrows():

        # url format:
        # url = "https://maps.googleapis.com/maps/api/place/textsearch/json?query=123%20main%20street&location=42.3675294%2C-71.186966&radius=10000&key=YOUR_API_KEY"

        print("PLACE SEARCH API")

        parms_search = dict()
        parms_search['location'] = str(row['latitude']) +','+ str(row['longitude'])
        parms_search['radius'] = str(500)
        parms_search['keyword'] = str(row['name'])
        parms_search['key'] = api_key

        response_search, js_search, success = pull_data(serviceurl_search, parms_search, payload, headers)

        if not success:
            continue

        # dump into json for PLACE SEARCH

        json.dump(js_search, json_search, indent=2)

        if len(js_search['results']) > 1:

            bunch = []

            for i in range(len(js_search['results'])):
                bunch.append([js_search['results'][i]['name'], 
                            js_search['results'][i]['place_id'], 
                            (js_search['results'][i]['geometry']['location']['lat'], js_search['results'][i]['geometry']['location']['lng'])])

            print('WE HAVE A WINNER: ', bunch)
            bunch = score_for_details(row, bunch)
            print('WE HAVE A WINNER: ', bunch)
            winner = bunch[0]

            name = winner[0]; place_id = winner[1]; coordinates = winner[2]

            print("PLACE DETAILS API")
            success, sample, js_details = places_details(name, place_id, coordinates, api_key, serviceurl_details, payload, headers, row, sample, row_index)
            if not success:
                continue

        else: 

            name = js_search['results'][0]['name'],
            place_id =  js_search['results'][0]['place_id']
            coordinates = (js_search['results'][0]['geometry']['location']['lat'], js_search['results'][0]['geometry']['location']['lng'])

            print("PLACE DETAILS API")
            success, sample, js_details = places_details(name, place_id, coordinates, api_key, serviceurl_details, payload, headers, row, sample, row_index)
            if not success:
                continue

        # dump into json for PLACE DETAILS

        json.dump(js_details, json_details, indent=2)


        print('Record number: ', row_index+1)

    json_search.close()
    json_details.close()

    return sample

def main():
    
    sample = pd.read_csv('yelp_sample_500_3.csv', sep=',')
    sample = sample.reset_index()
    sample['matched'] = np.NaN
    sample['confidence'] = np.NaN

    if os.path.isfile('google_data.csv'):
        google_data = pd.read_csv('google_data.csv', sep=',')
        sample = sample[len(google_data):500]        
        sample = seek(sample, google_data)
    else:
        google_data = pd.DataFrame(columns=['yelp_id', 'place_id', 'name', 'street_name', 'city', 'county', 'state', 'postal_code', 'coordinates', 'rating', 'review_count', 'business_status', 'category', 'hours'])
        google_data.to_csv("google_data.csv", index=False)
        sample = seek(sample, google_data)

    sample.to_csv("google_matches.csv", index=None, encoding='utf-8')
    

if __name__ == '__main__':
    main()
