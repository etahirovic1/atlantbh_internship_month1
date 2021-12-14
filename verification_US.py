import pandas as pd
import re
import numpy as np
from haversine import haversine, Unit
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from fastDamerauLevenshtein import damerauLevenshtein

def transf(row):
	return (row['latitude'], row['longitude'])

def clean(yelp, osm): # function for cleaning the names of keywords
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
		self.osm_us = self.osm_us[self.osm_us.name.notnull()==True]
		self.osm_us = self.osm_us[self.osm_us.highway.notnull()==False]
		self.osm_us = self.osm_us[self.osm_us.other_tags.notnull()==True]
		self.osm_us = self.osm_us[self.osm_us.other_tags.str.contains("amenity")]
		self.osm_us = self.osm_us.drop(['barrier','highway','ref','address','is_in','place','man_made', 'osm_id'], axis=1)
		self.osm_us = self.osm_us.rename(columns = { 'Y': 'latitude', 'X': 'longitude'}, inplace = False)
		self.osm_us = self.osm_us[self.osm_us['other_tags'].str.contains('addr|name:en|cuisine')]
		self.osm_us = self.osm_us.drop('other_tags', axis=1)
		self.osm_us = self.osm_us.reset_index()
		self.osm_us = self.osm_us.drop('index',axis=1)
		self.osm_us['coordinates'] = self.osm_us.apply(lambda x : transf(x), axis=1) 
		self.osm_us = self.osm_us.drop(columns=['latitude', 'longitude'])

	def score_it(self, row, yelp_name):

		osm_name = row['name']
		dist = row['haversine']
		haver_score = int(100-dist) # we only match up to 100m distance, so scale to 100 points
	
		st1 = str(osm_name); st1 = st1.lower()
		st2 = str(yelp_name); st2 = st2.lower()

		dam_lev_score = 0
		fuzz_score = 0
		calc = False

		if fuzz.token_set_ratio(st1, st2) > 10:  # if token set ratio fails, do not even check damerauLevenshtein
			yelp, osm = clean(st1, st2) # clear keywords like restaurant, cafe, the, food, etc. in order to eliminate high scores based on those words
			if not re.search('[a-zA-Z]', yelp) and not re.search('[a-zA-Z]', osm): # if the stripped names are not left with no letters (e.g. only spaces left), then do damerauLevenshtein on the stripped names
				dam_lev_score = damerauLevenshtein(yelp, osm)*100
				fuzz_score = fuzz.token_set_ratio(yelp, osm)
			else: # else do damerauLevenshtein on original names
				dam_lev_score = damerauLevenshtein(st1, st2)*100
				fuzz_score = fuzz.token_set_ratio(st1, st2)
				calc = True
			if dam_lev_score > 40 and not calc: # if the damLev score for the stripped names is above 40, then calculate the damLev score on full names
				dam_lev_score = damerauLevenshtein(st1, st2)*100
				fuzz_score = fuzz.token_set_ratio(st1, st2)

		#if haver_score < 1 or dam_lev_score < 40: # if the scores are bad, below these thresholds, score them with 0 so that they don't have a chance at having a score larger than 40 in total
		#	score = 0
		#else:
		name_score = dam_lev_score*0.7 + fuzz_score*0.3
		score = round(haver_score*0.3 + name_score*0.7, 2) # scale everything back to 100 points

		return score


	def skor(self, yelp_row):
	
		true_score = -1
		rec = np.NaN
		yelp_coord = (yelp_row['latitude'], yelp_row['longitude'])
		cluster = self.osm_us

		cluster['haversine'] = cluster['coordinates'].apply(lambda x : haversine(x, yelp_coord, unit='m'))
		cluster = cluster[cluster['haversine'] < 100]
		
		if len(cluster) > 0:
			cluster['verification_score'] = cluster.apply(lambda x : self.score_it(x, yelp_row['name']), axis=1)
			max_score = max(cluster['verification_score'])
			#print('max score', max_score)
			index_of_max = cluster[cluster['verification_score']==max_score].index[0]
			#print('index of max score', index_of_max)
			rec = [cluster.at[index_of_max,'name'], cluster.at[index_of_max,'coordinates']]
	
			if max_score < 50:
				return 'not matched' + ": " + str(round(max_score, 2))+', '+str(rec)
			elif max_score < 80:
				return 'partially matched' + ": " + str(round(max_score, 2))+', '+str(rec)
			else:
				return 'matched' + ": " + str(round(max_score, 2))+', '+str(rec)
		else:
			return 'not matched'

	def verif_us(self):

		yelp_us = pd.read_json('/Users/admin/PycharmProjects/atlantbh_internship/high_quality.json', lines=True)
		yelp_us = yelp_us.drop(['business_id', 'hours', 'stars', 'review_count', 'is_open', 'attributes', 'address', 'city', 'state', 'categories', 'postal_code'], axis=1)
		#yelp_us = yelp_us.tail(200)	
		yelp_us['verification_score'] = yelp_us.apply(lambda x : self.skor(x), axis=1)
		yelp_us.to_csv("yelp_hq_verified.csv", index=None, encoding='utf-8')


if __name__ == '__main__':
	file = pd.read_csv('us-points-csv.csv', sep='\t')
	#file.to_csv("test.csv", index=None, encoding='utf-8')
	runner = US(file)
	runner.verif_us()
