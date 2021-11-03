import json
import re


def detect_unstandardized_data(dict_names, report_file, formatting_scores, write=True):
    num_open_businesses = 160585
    counter = 0
    invalid_values = 0
    wrong_format_city = []
    wrong_format_state = []
    wrong_format_postal_code = []
    wrong_format_hours = []

    us_states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
                 "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                 "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                 "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                 "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
    canada_states = ['AB', 'BC', 'MB', 'NB', 'NL', 'NT', 'NS', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT']
    units_formatting = [30, 30, 15, 15]  # scale back to 100
    attributes_formatting = ['state', 'city', 'postal_code', 'latitude']

    with open('yelp_academic_dataset_business.json', encoding='utf-8') as f:
        for item in f:
            data_dict = json.loads(item)
            current_formatting_score = 0
            for name in dict_names:
                if name == 'is_open':  # if business is closed, do not do analysis
                    if data_dict[name] == 0:
                        num_open_businesses -= 1
                        continue
                if name == 'latitude':
                    if not (90 >= data_dict[name] >= -90):
                        invalid_values += 1
                        current_formatting_score += units_formatting[attributes_formatting.index(name)]
                elif name == 'longitude':
                    if not (180 >= data_dict[name] >= -180):
                        invalid_values += 1
                        if 90 >= data_dict['latitude'] >= -90:
                            current_formatting_score += units_formatting[attributes_formatting.index('latitude')]
                elif name == 'stars':
                    if not (5 >= data_dict[name] >= 1):
                        invalid_values += 1
                        current_formatting_score += units_formatting[attributes_formatting.index(name)]
                elif name == 'state':  # checks name of state against lists of us and canada state abbreviations
                    if data_dict[name] not in us_states and data_dict[name] not in canada_states:
                        if data_dict[name] not in wrong_format_state:
                            wrong_format_state.append(data_dict[name])
                            current_formatting_score += units_formatting[attributes_formatting.index(name)]
                elif name == 'postal_code' and len(data_dict[name]) != 0:
                    if data_dict['state'] in us_states:
                        if not re.search(r"[0-9]{5}", data_dict[name]):
                            wrong_format_postal_code.append((data_dict['state'], data_dict['city'], data_dict[name],
                                                             data_dict['latitude'], data_dict['longitude']))
                            current_formatting_score += units_formatting[attributes_formatting.index(name)]
                    elif data_dict['state'] in canada_states:
                        if not re.search("\A((A|B|C|E|G|H|J|K|L|M|N|P|R|S|T|V|X|Y)[0-9]"
                                         "(A|B|C|E|G|H|J|K|L|M|N|P|R|S|T|V|W|X|Y|Z)( )"
                                         "[0-9](A|B|C|E|G|H|J|K|L|M|N|P|R|S|T|V|W|X|Y|Z)[0-9])|"
                                         "(A|B|C|E|G|H|J|K|L|M|N|P|R|S|T|V|X|Y)[0-9]"
                                         "(A|B|C|E|G|H|J|K|L|M|N|P|R|S|T|V|W|X|Y|Z)\Z", data_dict[name]):
                            wrong_format_postal_code.append((data_dict['state'], data_dict['city'], data_dict[name],
                                                             data_dict['latitude'], data_dict['longitude']))
                            current_formatting_score += units_formatting[attributes_formatting.index(name)]
                elif name == 'city':
                    statement = data_dict[name]
                    res = bool(re.match('[a-zA-Z\s]+$', statement))
                    if res:
                        continue
                    else:  # filtering out cases where St. or Dr. is contained, or even a dash between two names
                        if re.search(r"St\.|ST\.", statement) or re.search(r"Dr\.|DR\.", statement) or \
                                re.search(r"[a-zA-Z ]{2,100}-[a-zA-Z ]{2,100}", statement):
                            if str(data_dict['state']) in str(data_dict['city']):
                                wrong_format_city.append(statement)
                                current_formatting_score += units_formatting[attributes_formatting.index(name)]
                            else:
                                continue
                        else:  # if all checks fail then append into wrongly formatted list
                            wrong_format_city.append(statement)
                            current_formatting_score += units_formatting[attributes_formatting.index(name)]
                elif name == 'hours':
                    if data_dict['hours'] is not None:
                        wrong = False
                        hrs = data_dict['hours'].values()
                        for h in hrs:
                            interval = h.split('-')
                            for time in interval:
                                component = time.split(':')
                                if not 23 >= int(component[0]) >= 0 or not 59 >= int(component[1]) >= 0:
                                    wrong_format_hours.append(interval)
                                    current_formatting_score += units_formatting[attributes_formatting.index(name)]
                                    break
                            if wrong:
                                break

                formatting_scores[counter] = (formatting_scores[counter] - current_formatting_score)*0.4
                counter += 1

    if write:

        report_file.write('Wrongly formatted postal codes: ' + str(wrong_format_postal_code) + '\n' + '\n')
        report_file.write(
            'Number of wrongly formatted postal codes: ' + str(len(wrong_format_postal_code)) + '\n\n')
        report_file.write('Percentage of wrongly formatted postal codes: ' + str(round(100*len(
                                        wrong_format_postal_code) / num_open_businesses, 2)) + '%' + '\n\n')
        report_file.write('Number of invalid values of lat, long or stars: ' + str(invalid_values) + '\n' + '\n')
        report_file.write('Wronly formatted cities: ' + str(wrong_format_city) + '\n' + '\n')
        report_file.write('Wronly formatted states: ' + str(wrong_format_state) + '\n' + '\n')
        report_file.write('Percent of wrongly formatted cities: ' + str(
            round((len(wrong_format_city) / num_open_businesses) * 100, 5)) + '%' + '\n' + '\n')
        report_file.write('Number of wrongly formatted cities: ' + str(len(wrong_format_city)) + '\n' + '\n')
        report_file.write('Percent of wrongly formatted states: ' + str(
            round((len(wrong_format_state) / num_open_businesses) * 100, 5)) + '%' + '\n' + '\n')
        report_file.write('Number of wrongly formatted states: ' + str(len(wrong_format_state)) + '\n' + '\n')
        report_file.write('Number of wrongly formatted hours: ' + str(len(wrong_format_hours)) + '\n\n')

    return formatting_scores
