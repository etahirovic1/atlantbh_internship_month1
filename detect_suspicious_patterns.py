import json


def detect_suspicious_patterns(dict_names, report_file, write=True):

    all_records_no_duplicates = set()
    all_records = list()
    invalid_locations = []
    formatting_scores = []
    business_per_address = dict()
    units_formatting = [30, 30, 15, 15]  # scale back to 100
    attributes_formatting = ['state', 'city', 'postal_code', 'latitude']

    with open('yelp_academic_dataset_business.json', encoding='utf-8') as f:
        for item in f:
            data_dict = json.loads(item)
            data = ((key, data_dict.get(key)) for key in data_dict.keys())
            all_records_no_duplicates.add(data)
            all_records.append(data)
            current_formatting_score = 100
            for name in dict_names:
                if name == 'is_open':  # if business is closed, do not do analysis
                    if data_dict[name] == 0:
                        continue
                if name == 'latitude':
                    if not (90 >= data_dict[name] >= 0):
                        invalid_locations.append((data_dict['city'], (data_dict['latitude'], data_dict['longitude'])))
                        current_formatting_score -= units_formatting[attributes_formatting.index(name)]
                elif name == 'longitude':
                    if not (0 >= data_dict[name] >= -180):
                        invalid_locations.append((data_dict['city'], (data_dict['latitude'], data_dict['longitude'])))
                        if 90 >= data_dict[name] >= 0:
                            current_formatting_score -= units_formatting[attributes_formatting.index('latitude')]
                elif name == 'address' and len(data_dict[name]) != 0:
                    if data_dict[name] not in business_per_address.keys():
                        business_per_address.update({data_dict[name]: 0})
                    business_per_address.update(({data_dict[name]: business_per_address.get(data_dict[name]) + 1}))
                formatting_scores.append(current_formatting_score)
    suspicious_numbers = []

    for key in business_per_address.keys():
        if business_per_address.get(key) > 1000:
            suspicious_numbers.append((key, business_per_address.get(key)))

    difference = set(all_records).difference(all_records_no_duplicates)  # check for duplicated data

    if write:

        report_file.write('Number of duplicated records: ' + str(difference) + '\n' + '\n')
        report_file.write(
            'Suspiciously large number (1000 or greater) of businesses per address: ' + str(
                suspicious_numbers) + '\n\n')
        report_file.write('Places with incorrect values of latitude and longitude, as per NW quadrant: '
                          + str(invalid_locations) + '\n' + '\n')

    return formatting_scores
