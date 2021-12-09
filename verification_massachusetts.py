import pandas as pd
import re
import numpy as np
from haversine import haversine, Unit
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from fastDamerauLevenshtein import damerauLevenshtein


def clean(yelp, osm): # function for cleaning the names of keywords
	yelp = yelp.lower()
	osm = osm.lower()
	matches_yelp = re.findall(r"the | the |restaurant|caffe|cafe|theatre|food|house|park|club", str(yelp))
	matches_yelp = [match.strip() for match in matches_yelp]
	matches_osm = re.findall(r"the | the |restaurant|caffe|cafe|theatre|food|house|park|club", str(osm))
	matches_osm = [match.strip() for match in matches_osm]
	matches = list(set(matches_yelp) & set(matches_osm))
	for match in matches: # replace only common matches
		yelp = yelp.replace(match, '')
		osm = osm.replace(match, '')
	return yelp, osm


class US:

	def __init__(self, osm_us):
		self.osm_us = osm_us
		
	def score_it(self, dist, yelp_name, osm_name):
	
		haver_score = int(100-dist) # we only match up to 100m distance, so scale to 100 points

		if haver_score < 0: # if the distance is more than 100m, revert to 0 points
			haver_score = 0
	
		st1 = str(osm_name); st1 = st1.lower()
		st2 = str(yelp_name); st2 = st2.lower()
		
		dam_lev_score = 0
		calc = False

		if fuzz.token_set_ratio(st1, st2) > 10:  # if token set ratio fails, do not even check damerauLevenshtein
			yelp, osm = clean(yelp_name, osm_name) # clear keywords like restaurant, cafe, the, food, etc. in order to eliminate high scores based on those words
			if not re.search('[a-zA-Z]', yelp) and not re.search('[a-zA-Z]', osm): # if the stripped names are not left with no letters (e.g. only spaces left), then do damerauLevenshtein on the stripped names
				dam_lev_score = damerauLevenshtein(yelp, osm)*100
			else: # else do damerauLevenshtein on original names
				dam_lev_score = damerauLevenshtein(yelp_name, osm_name)*100
				calc = True
			if dam_lev_score > 40 and not calc: # if the damLev score for the stripped names is above 40, then calculate the damLev score on full names
				dam_lev_score = damerauLevenshtein(yelp_name, osm_name)*100

		if haver_score < 1 or dam_lev_score < 40: # if the scores are bad, below these thresholds, score them with 0 so that they don't have a chance at having a score larger than 40 in total
			score = 0
		else:
			score = round(haver_score*0.3 + dam_lev_score*0.7, 2) # scale everything back to 100 points

		return score

	def skor(self, yelp_row):
	
		true_score = -1
		rec = np.NaN
		yelp_coord = (yelp_row['latitude'], yelp_row['longitude'])
		
		for osm_row_index, osm_row in self.osm_us.iterrows():
	
			osm_coord = (osm_row['latitude'], osm_row['longitude'])

			haver = haversine(osm_coord, yelp_coord, unit='m')
	
			if  haver < 100: # only check in 100m radius
	
				score = self.score_it(haver, yelp_row['name'], osm_row['name'])

				if score > true_score: # find record which yields highest match score
					true_score = score
					rec = [osm_row['name'], osm_row['latitude'], osm_row['longitude']]
	
		if rec == 'nan' or true_score < 40:
			return 'not matched' + ": " + str(round(true_score, 2))+', '+str(rec)
		elif true_score < 80:
			return 'partially matched' + ": " + str(round(true_score, 2))+', '+str(rec)
		else:
			return 'matched' + ": " + str(round(true_score, 2))+', '+str(rec)
	

	def verif_us(self):

		yelp_us = pd.read_json('/Users/admin/PycharmProjects/atlantbh_internship/Massachusetts.json', lines=True)  # this is data that already only includes open businesses
		yelp_us = yelp_us.drop(['business_id', 'hours', 'stars', 'review_count', 'is_open', 'attributes', 'address', 'city', 'state', 'categories', 'postal_code'], axis=1)	
		yelp_500 = yelp_us.head(5)
		yelp_500['verification_score'] = yelp_500.apply(lambda x : self.skor(x), axis=1)
		#yelp_500 = yelp_500[yelp_500['verification_score'].str.contains(' nan')==False]

		yelp_500.to_csv("yelp_massachussets_verified_all_test.csv", index=None, encoding='utf-8')

if __name__ == '__main__':
	file = pd.read_csv('massachusetts-filtered.csv', sep=',')
	runner = US(file)
	runner.verif_us()
