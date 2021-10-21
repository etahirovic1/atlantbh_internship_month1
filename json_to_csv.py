import json
import csv


def json_to_csv():

    count = 0
    num_lines = 0
    num_written_lines = 0

    x = open('yelp_academic_dataset_business.json', encoding='utf-8')
    x.close()

    csv_writer = csv.writer(open('business_data.csv', 'w+', encoding='utf-8', newline=''))
    with open('yelp_academic_dataset_business.json', 'r', encoding='utf8') as f:
        for item in f:
            num_lines += 1
            data_dict = json.loads(item)

            if count == 0:
                header = data_dict.keys()
                csv_writer.writerow(header)
                count += 1

            csv_writer.writerow(data_dict.values())
            num_written_lines += 1

    print('Number of lines: ', num_lines)
    print('Number of written lines: ', num_written_lines)