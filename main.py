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

        # or:
        with open('yelp_academic_dataset_business.json', encoding='utf-8') as f:
            df = pd.DataFrame(json.loads(line) for line in f)