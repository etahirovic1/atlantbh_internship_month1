import csv

import detect_unstandardized_data
import json_to_csv
import os.path
import pandas as pd
import json
import basic_analysis
import detect_suspicious_patterns

pd.options.display.width = None
pd.options.display.max_columns = None
pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 3000)

if __name__ == '__main__':
    if not os.path.isfile('./business_data.csv'):
        print('Making CSV file...')
        json_to_csv.json_to_csv()
    else:
        if not os.path.isfile('report.txt'):
            report_file = open('report.txt', 'a')
            dict_names = ['is_open', 'business_id', 'name', 'address', 'city', 'state', 'latitude', 'longitude',
                          'stars', 'categories', 'hours']
            basic_analysis.basic_analysis(dict_names, report_file)
            detect_suspicious_patterns.detect_suspicious_patterns(dict_names, report_file)
            detect_unstandardized_data.detect_unstandardized_data(dict_names, report_file)

            df = pd.read_csv('business_data.csv')
            df.info()
            group_city = df[['city', 'state']].groupby('state')

            report_file.write(str(df.describe().transpose()) + '\n' + '\n')
            report_file.write(str(df.corr()) + '\n' + '\n')
            report_file.write(str(df.isnull().sum()) + '\n' + '\n')
            report_file.write(str(group_city.head()) + '\n' + '\n')
            report_file.write(str(df.groupby(['state', 'city']).count().address) + '\n' + '\n')
            report_file.write(str(df.groupby('city').mean().stars) + '\n' + '\n')
            report_file.close()

            # group_address = df[['address', 'city', 'state']].groupby('address')
            # print(group_address.count())
            # print(df.groupby('hours').count().state)
            # print(df.groupby(by='is_open').agg('count'))
            # att = df.groupby('attributes').count()
            # print(att)
