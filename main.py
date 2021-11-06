import csv

import detect_unstandardized_data
import json_to_csv
import os.path
import pandas as pd
import basic_analysis
import detect_suspicious_patterns
import categorization


def set_options():
    pd.options.display.width = None
    pd.options.display.max_columns = None
    pd.set_option('display.max_rows', 3000)
    pd.set_option('display.max_columns', 3000)


class Main:
    def __init__(self):
        self.formatting_scores = []

    def run(self):
        set_options()
        dict_names = ['is_open', 'business_id', 'name', 'address', 'city', 'state', 'latitude', 'longitude',
                      'stars', 'categories', 'hours', 'postal_code']
        if not os.path.isfile('./business_data.csv'):
            print('Making CSV file...')
            json_to_csv.json_to_csv()
        else:
            if not os.path.isfile('report.txt'):
                print('Creating report...')
                report_file = open('report.txt', 'w')
                basic_analysis.basic_analysis(dict_names, report_file)
                self.formatting_scores = detect_suspicious_patterns.detect_suspicious_patterns(report_file)
                self.formatting_scores = detect_unstandardized_data.detect_unstandardized_data(report_file,
                                                                                               self.formatting_scores)

                df = pd.read_csv('business_data.csv')

                report_file.write('Basic info table: ' + '\n')
                df.info(buf=report_file)
                report_file.write('\n\n')

                report_file.write('Description table: ' + '\n')
                report_file.write(str(df.describe().transpose()) + '\n' + '\n')

                report_file.write('Correlation table for numerical values: ' + '\n')
                report_file.write(str(df.loc[:, ['stars', 'review_count', 'is_open']].corr()) + '\n' + '\n')

                report_file.write('Number of null values per attribute: ' + '\n')
                report_file.write(str(df.isnull().sum()) + '\n' + '\n')

                report_file.write('Number of businesses per ciy per state: ' + '\n')
                # report_file.write(str(df.groupby(['state', 'city']).count().address) + '\n' + '\n')
                report_file.write(str(df.groupby(['state', 'city']).count().address.to_frame('address')
                                      .sort_values('address', ascending=False)) + '\n' + '\n')

                report_file.close()

            else:
                print('Categorizing data...')
                report_file = open('report.txt', 'a')
                self.formatting_scores = detect_suspicious_patterns.detect_suspicious_patterns(report_file, False)
                self.formatting_scores = detect_unstandardized_data.detect_unstandardized_data(report_file,
                                                                                               self.formatting_scores,
                                                                                               False)
                categorization.categorization(self.formatting_scores)
                report_file.close()


if __name__ == '__main__':
    runner = Main()
    runner.run()
