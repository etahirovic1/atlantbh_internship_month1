import json
import re


def detect_unstandardized_data(dict_names, report_file):
    invalid_values = 0
    wrong_format_city = []
    wrong_format_state = []
    us_states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
                 "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                 "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                 "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                 "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
    canada_states = ['BC', 'ON', 'ABE']
    with open('yelp_academic_dataset_business.json', encoding='utf-8') as f:
        for item in f:
            data_dict = json.loads(item)
            for name in dict_names:
                if name == 'latitude':
                    if not (90 >= data_dict[name] >= -90):
                        invalid_values += 1
                elif name == 'longitude':
                    if not (180 >= data_dict[name] >= -180):
                        invalid_values += 1
                elif name == 'stars':
                    if not (5 >= data_dict[name] >= 1):
                        invalid_values += 1
                elif name == 'city':
                    statement = data_dict[name]
                    res = bool(re.match('[a-zA-Z\s]+$', statement))
                    if res:
                        continue
                    else:  # filtering out cases where St. or Dr. is contained, or even a dash between two names
                        if re.search(r"St\.|ST\.", statement) or re.search(r"Dr\.|DR\.", statement) or \
                                re.search(r"[a-zA-Z ]{2,100}-[a-zA-Z ]{2,100}", statement):
                            continue
                        else:  # if all checks fail then append into wrongly formatted list
                            wrong_format_city.append(statement)
                elif name == 'state':  # checks name of state against lists of us and canada state abbreviations
                    if data_dict[name] not in us_states and data_dict[name] not in canada_states:
                        if data_dict[name] not in wrong_format_state:
                            wrong_format_state.append(data_dict[name])

        report_file.write('invalid values of lat, long or stars: ' + str(invalid_values) + '\n' + '\n')
        report_file.write('wrongly formatted cities: ' + str(wrong_format_city) + '\n' + '\n')
        report_file.write('wrongly formatted states: ' + str(wrong_format_city) + '\n' + '\n')
