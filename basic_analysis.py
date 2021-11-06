import json
import re
from collections import Counter

import matplotlib.pyplot as plt

def basic_analysis(dict_names, report_file):
    dummies = ['unavailable', 'missing', 'test', 'error', 'none', 'null', 'rand',
               'name', 'filler', 'private']
    string_dict_names = ['business_id', 'name', 'address', 'city', 'state', 'categories', 'hours']
    all_names = {'business_id': 0, 'name': 0, 'address': 0, 'city': 0, 'state': 0, 'postal_code': 0, 'latitude': 0,
                 'longitude': 0, 'stars': 0, 'review_count': 0, 'is_open': 0, 'attributes': 0, 'categories': 0,
                 'hours': 0}
    num_records = 160585
    num_complete_records = 160585
    dummy_values = 0
    open_businesses = 0
    states = []
    cities = []
    dummies_found = []
    business_per_state = dict()
    business_per_city = dict()
    stars_per_city = dict()
    closed_per_city = dict()
    dummies_dict = dict()

    open_businesses_file = open('open_businesses.json', 'w', encoding='utf8')

    with open('yelp_academic_dataset_business.json', encoding='utf-8') as f:
        for item in f:
            data_dict = json.loads(item)
            if data_dict['is_open'] == 0:
                if data_dict['city'] is not None:
                    if data_dict['city'] in closed_per_city:
                        closed_per_city.update({data_dict['city']: closed_per_city.get(data_dict['city']) + 1})
                    else:
                        closed_per_city.update({data_dict['city']: 1})
            else:
                open_businesses_file.write(item)  # make a .json of open businesses
                for name in all_names.keys():
                    if not isinstance(data_dict[str(name)], float) and not isinstance(data_dict[str(name)], int):
                        if data_dict[str(name)] is not None:
                            if len(data_dict[str(name)]) == 0:
                                all_names.update({name: all_names.get(name)+1})
    open_businesses_file.close()

    with open('yelp_academic_dataset_business.json', encoding='utf-8') as f:

        for item in f:
            data_dict = json.loads(item)
            record_checked = False

            for name in dict_names:
                if name == 'is_open':  # if business is closed, do not do analysis
                    if data_dict[name] == 0:
                        continue
                    else:
                        open_businesses += 1

                if data_dict[name] is None:  # counts number of complete records
                    if not record_checked:
                        record_checked = True
                        num_complete_records -= 1
                elif not isinstance(data_dict[name], float) and not isinstance(data_dict[name], int):
                    if len(data_dict[name]) == 0:
                        if not record_checked:
                            record_checked = True
                            num_complete_records -= 1
                if data_dict[name] in dummies:  # searches for dummy values,
                    # excluding cases where the dummy is a part of a bigger word
                    dummy_values += 1
                    dummies_found.append(str(data_dict[name]))
                if name in string_dict_names:
                    d = data_dict[name]
                    if data_dict[name] is not None:
                        if re.search(r"(?i)(^missing$|^null$|^unavailable$|^test$|^rand$|^name$|^error$|^filler$|^none$"
                                     r"|^private$)", str(d)):
                            dummy_values += 1
                            dummies_found.append(str(d))
                            try:
                                dummies_dict.update(({(name, str(d)): dummies_dict.get((name, str(d))) + 1}))
                            except:
                                dummies_dict.update({(name, str(d)): 1})
                            break
                if name == 'state':  # calculates num businesses per state
                    if data_dict[name] not in states:
                        states.append(data_dict[name])
                        business_per_state.update({data_dict[name]: 0})
                    business_per_state.update(({data_dict[name]: business_per_state.get(data_dict[name]) + 1}))
                if name == 'city':  # calculates num businesses per city, and average star rating per city
                    if data_dict[name] not in cities:
                        cities.append(data_dict[name])
                        stars_per_city.update({data_dict[name]: (0, 0)})
                        business_per_city.update({data_dict[name]: 0})
                    business_per_city.update(({data_dict[name]: business_per_city.get(data_dict[name]) + 1}))
                    stars_per_city.update({data_dict[name]: (stars_per_city.get(data_dict[name])[0] +
                                                             data_dict['stars'],
                                                             stars_per_city.get(data_dict[name])[1] + 1)})

        do_not_buy = dict()  # consider not buying records from cities where 75% or more businesses have shut down
        for key in closed_per_city:
            ratio = float(closed_per_city.get(key)) / float(business_per_city.get(key))
            if ratio >= 0.75:
                do_not_buy.update({key: (str(ratio * 100) + '%', 'number: ' + str(closed_per_city.get(key)))})

        closed_per_city_new = dict()  # num closed businesses per city and total num of businesses per city
        closed_per_city_new.update(
            {key: round((closed_per_city.get(key) / business_per_city.get(key)) * 100, 2)
             for key in closed_per_city})
        closed_per_city_new = dict(sorted(closed_per_city_new.items(), key=lambda item1: item1[1], reverse=True))

        stars_per_city_new = dict()  # avg star rating per city with num of ratings
        stars_per_city_new.update(
            (key, (round(stars_per_city.get(key)[0] / stars_per_city.get(key)[1], 2), stars_per_city.get(key)[1]))
            for key in stars_per_city)

        report_file.write('Number of empty values per attribute: ' + str(all_names) + '\n\n')
        report_file.write('Number of complete records: ' + str(int(num_complete_records / 1000)) + ',' +
                          str(num_complete_records % 1000) + '\n' + '\n')
        report_file.write('Total number of dummy values found: ' + str(int(dummy_values / 1000)) + ',' +
                          str(dummy_values % 1000) + '\n' + '\n')
        report_file.write('Number of dummy values found per attribute: ' + str(dummies_dict) + '\n' + '\n')
        report_file.write('Number of businesses per state: ' + str(business_per_state) + '\n' + '\n')
        report_file.write('Number of businesses per city: ' + str(business_per_city) + '\n' + '\n')
        report_file.write('Percentage of closed businesses per city: ' + str(closed_per_city_new) + '\n' + '\n')
        report_file.write('Cities where 75% or more businesses closed down: ' + str(do_not_buy) + '\n' + '\n')
        report_file.write(
            'Average star rating per city with number of ratings: ' + str(stars_per_city_new) + '\n' + '\n')
        report_file.write(
            'Percentage of open businesses: ' + str(round((open_businesses / num_records) * 100, 2)) + '%' + ' (' +
            str(int(open_businesses / 1000)) + ',' + str(open_businesses % 1000) + ')' + '\n\n')

        # plt.bar(business_per_state.keys(), business_per_state.values(), width=1, color='g')
        # plt.show()
