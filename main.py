import json_to_csv
import os.path
import pandas as pd
import json

if __name__ == '__main__':
    if not os.path.isfile('./business_data.csv'):
        print('Making CSV file...')
        json_to_csv.json_to_csv()
    else:
        # json_file = open('yelp_academic_dataset_business.json', encoding='utf-8')
        # pd.read_json(json_file, lines=True)
        # df = pd.DataFrame()

        dict_names = ['business_id', 'name', 'address', 'city', 'state', 'latitude', 'longitude',
                      'stars', 'categories', 'hours', 'is_open']
        dummies = ['unavailable', 'missing', 'test', 'error', 'none', 'null', 'rand',
                   'name', 'filler', 'private']
        string_dict_names = ['business_id', 'name', 'address', 'city', 'state', 'categories', 'hours']

        restaurant_wildcards = ['restaurant', 'food', 'coffee', 'tea', 'hospice', 'mexican', 'chinese', 'italian',
                                'indian', ]
        beauty_wildcards = ['spa', 'hospital', 'beauty', 'salon', 'nails', ]
        mechanic_wildcards = ['auto', 'repair', 'tires', 'automotive', ]

        count = 0
        num_complete_records = 160585

        dummy_values = 0
        invalid_values = 0
        closed = 0
        states = []
        cities = []
        business_per_state = dict()
        business_per_city = dict()
        closed_per_city = dict()

        with open('yelp_academic_dataset_business.json', encoding='utf-8') as f:
            # df = pd.DataFrame(json.loads(line) for line in f)
            for item in f:
                data_dict = json.loads(item)
                record_checked = False

                # print(item)

                for name in dict_names:

                    if data_dict[name] is None:
                        if not record_checked:
                            record_checked = True
                            num_complete_records -= 1
                    elif not isinstance(data_dict[name], float) and not isinstance(data_dict[name], int):
                        if len(data_dict[name]) == 0:
                            if not record_checked:
                                record_checked = True
                                num_complete_records -= 1

                    if data_dict[name] in dummies:
                        dummy_values += 1

                    elif name == 'latitude':
                        if not (90 >= data_dict[name] >= -90):
                            invalid_values += 1
                    elif name == 'longitude':
                        if not (180 >= data_dict[name] >= -180):
                            invalid_values += 1
                    elif name == 'stars':
                        if not (5 >= data_dict[name] >= 1):
                            invalid_values += 1
                    elif name == 'is_open':
                        if data_dict[name] == 0:
                            closed += 1

                    if name in string_dict_names:
                        for dummy in dummies:
                            if data_dict[name] is None:
                                continue
                            if dummy in data_dict[name]:
                                dummy_values += 1
                                break
                    if name == 'state':
                        if data_dict[name] not in states:
                            states.append(data_dict[name])
                            business_per_state.update({data_dict[name]: 0})
                        business_per_state.update(({data_dict[name]: business_per_state.get(data_dict[name]) + 1}))
                    if name == 'city':
                        if data_dict[name] not in cities:
                            cities.append(data_dict[name])
                            business_per_city.update({data_dict[name]: 0})
                            closed_per_city.update({data_dict[name]: 0})
                        business_per_city.update(({data_dict[name]: business_per_city.get(data_dict[name]) + 1}))
                        if data_dict['is_open'] == 0:
                            closed_per_city.update(({data_dict[name]: closed_per_city.get(data_dict[name]) + 1}))

        print('invalid values of lat, long or stars', invalid_values)
        print('closed', closed)
        print('complete records', num_complete_records)
        print('dummy values', dummy_values)

        print(business_per_state)
        print(business_per_city)
        print(closed_per_city)
