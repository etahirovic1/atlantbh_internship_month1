import json
import re

import pandas as pd


def categorization(formatting_scores):

    dict_names = ['is_open', 'business_id', 'name', 'address', 'city', 'state', 'latitude', 'longitude',
                  'stars', 'categories', 'hours', 'postal_code']
    attributes = ['address', 'postal_code', 'attributes', 'categories', 'hours']

    units_completeness = [25, 25, 10, 20, 20]
    completeness_scores = []
    total_scores = []
    high_quality_num = 0
    medium_quality_num = 0
    low_quality_num = 0
    counter = 0

    high_quality = open('high_quality.json', 'w', encoding='utf8')
    medium_quality = open('medium_quality.json', 'w', encoding='utf8')
    low_quality = open('low_quality.json', 'w', encoding='utf8')
    open_businesses = open('open_businesses.json', 'w', encoding='utf8')

    with open('yelp_academic_dataset_business.json', encoding='utf-8') as f:
        for item in f:
            data_dict = json.loads(item)
            if data_dict['is_open'] == 0:
                continue
            else:
                open_businesses.write(item)
    open_businesses.close()

    with open('open_businesses.json', encoding='utf-8') as f:
        for item in f:
            data_dict = json.loads(item)
            current_completeness_score = 100
            for name in attributes:
                if data_dict[name] is None:
                    if name == 'address':
                        if data_dict['latitude'] is None or data_dict['longitude'] is None:
                            current_completeness_score -= units_completeness[attributes.index(name)]
                        else:
                            current_completeness_score -= units_completeness[attributes.index(name)]/2
                    else:
                        current_completeness_score -= units_completeness[attributes.index(name)]
                elif name == 'categories' or name == 'hours':
                    if re.search(r"(?i)(^none$)", str(data_dict[name])):
                        current_completeness_score -= units_completeness[attributes.index(name)]
                elif not isinstance(data_dict[name], float) and not isinstance(data_dict[name], int):
                    if len(data_dict[name]) == 0:
                        current_completeness_score -= units_completeness[attributes.index(name)]

            score = current_completeness_score*0.6
            completeness_scores.append(score)
            total_score = score + formatting_scores[counter]
            total_scores.append(total_score)

            if total_score >= 95:
                high_quality.write(item)
                high_quality_num += 1
            elif 95 > total_score >= 90:
                medium_quality.write(item)
                medium_quality_num += 1
            else:
                low_quality.write(item)
                low_quality_num += 1
            counter += 1

        high_quality.close()
        medium_quality.close()
        low_quality.close()

        print('num high q', high_quality_num)
        print('num medium q', medium_quality_num)
        print('num low q', low_quality_num)

        # print('total scores', total_scores)
