import json


def detect_suspicious_patterns(dict_names, report_file):
    """restaurant_wildcards = ['restaurant', 'food', 'coffee', 'tea', 'hospice', 'mexican', 'chinese', 'italian',
                            'indian', ]
    beauty_wildcards = ['spa', 'hospital', 'beauty', 'salon', 'nails', ]
    mechanic_wildcards = ['auto', 'repair', 'tires', 'automotive', ]"""

    all_records_no_duplicates = set()
    all_records = list()

    with open('yelp_academic_dataset_business.json', encoding='utf-8') as f:
        for item in f:
            data_dict = json.loads(item)
            data = ((key, data_dict.get(key)) for key in data_dict.keys())
            all_records_no_duplicates.add(data)
            all_records.append(data)

    difference = set(all_records).difference(all_records_no_duplicates)  # check for duplicated data
    report_file.write('duplicate records: ' + str(difference) + '\n' + '\n')
