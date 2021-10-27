import json
import re


def basic_analysis(dict_names, report_file):
    dummies = ['unavailable', 'missing', 'test', 'error', 'none', 'null', 'rand',
               'name', 'filler', 'private']
    dummies_dict = dict()
    string_dict_names = ['business_id', 'name', 'address', 'city', 'state', 'categories', 'hours']
    num_complete_records = 160585
    dummy_values = 0
    states = []
    cities = []
    business_per_state = dict()
    business_per_city = dict()
    stars_per_city = dict()
    closed_per_city = dict()
    dummies_found = []

    with open('yelp_academic_dataset_business.json', encoding='utf-8') as f:

        for item in f:
            data_dict = json.loads(item)
            record_checked = False

            for name in dict_names:
                if name == 'is_open':  # if business is closed, do not do analysis
                    if data_dict[name] == 0:
                        try:
                            closed_per_city.update({data_dict['city']: closed_per_city.get(data_dict['city']) + 1})
                        except:
                            closed_per_city.update({data_dict['city']: 1})
                        continue

                if data_dict[name] is None:  # counts number of complete records
                    if not record_checked:
                        record_checked = True
                        num_complete_records -= 1
                elif not isinstance(data_dict[name], float) and not isinstance(data_dict[name], int):
                    if len(data_dict[name]) == 0:
                        if not record_checked:
                            record_checked = True
                            num_complete_records -= 1

                if data_dict[name] in dummies:  # searches for dummy values, excluding cases where the dummy is a part of a bigger word
                    dummy_values += 1
                    dummies_found.append(data_dict[name])
                if name in string_dict_names:
                    d = data_dict[name]
                    if re.search(r"(?i)(^missing$|^null$|^unavailable$|^test$|^rand$|^name$|^error$|^filler$|^none$"
                                 r"|^private$)", str(d)):
                        dummy_values += 1
                        dummies_found.append(d)
                        try:
                            dummies_dict.update(({d: dummies_dict.get(d) + 1}))
                        except:
                            dummies_dict.update({d: 1})
                        break

                if name == 'state':  # calculates num businesses per state
                    if data_dict[name] not in states:
                        states.append(data_dict[name])
                        business_per_state.update({data_dict[name]: 0})
                    business_per_state.update(({data_dict[name]: business_per_state.get(data_dict[name]) + 1}))
                if name == 'city': # calculates num businesses per city, and average star rating per city
                    if data_dict[name] not in cities:
                        cities.append(data_dict[name])
                        stars_per_city.update({data_dict[name]: (0, 0)})
                        business_per_city.update({data_dict[name]: 0})
                    business_per_city.update(({data_dict[name]: business_per_city.get(data_dict[name]) + 1}))
                    stars_per_city.update({data_dict[name]: (stars_per_city.get(data_dict[name])[0] +
                                                             data_dict['stars'],
                                                             stars_per_city.get(data_dict[name])[1] + 1)})

        closed_per_city_new = dict()  # num closed businesses per city and total num of businesses per city
        closed_per_city_new.update((key, [{'closed: ', closed_per_city.get(key)}, {'total: ', business_per_city.get(key)}]) for key in closed_per_city)

        do_not_buy = dict()  # consider not buying records from cities where 75% or more businesses have shut down
        for key in closed_per_city:
            ratio = float(closed_per_city.get(key))/float(business_per_city.get(key))
            if ratio >= 0.75:
                do_not_buy.update({key: (ratio, closed_per_city.get(key))})

        stars_per_city_new = dict()  # avg star rating per city with num of ratings
        stars_per_city_new.update(
            (key, (round(stars_per_city.get(key)[0] / stars_per_city.get(key)[1], 2), stars_per_city.get(key)[1]))
            for key in stars_per_city)

        report_file.write('complete records: ' + str(num_complete_records) + '\n' + '\n')
        report_file.write('dummy values: ' + str(dummy_values) + '\n' + '\n')
        report_file.write('dummy values dictionary: ' + str(dummies_dict) + '\n' + '\n')
        report_file.write('businesses per state: ' + str(business_per_state) + '\n' + '\n')
        report_file.write('businesses per city: ' + str(business_per_city) + '\n' + '\n')
        report_file.write('closed businesses per city: ' + str(closed_per_city_new) + '\n' + '\n')
        report_file.write('city where 75% or more businesses closed down: ' + str(do_not_buy) + '\n' + '\n')
        report_file.write('stars per city: ' + str(stars_per_city_new) + '\n' + '\n')


