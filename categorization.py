import json
import re
import matplotlib.pyplot as plt


def categorization(formatting_scores):
    attributes = ['address', 'postal_code', 'categories', 'hours']

    units_completeness = [20, 25, 35, 20]
    completeness_scores = []
    total_scores = []
    high_medium_bordering = []
    medium_low_bordering = []
    high_quality_num = 0
    medium_quality_num = 0
    low_quality_num = 0
    counter = 0

    all_scores = dict()

    lower_bound = 88
    upper_bound = 95

    high_quality = open('high_quality.json', 'w', encoding='utf8')
    medium_quality = open('medium_quality.json', 'w', encoding='utf8')
    low_quality = open('low_quality.json', 'w', encoding='utf8')

    with open('open_businesses.json', encoding='utf-8') as f:
        for item in f:
            data_dict = json.loads(item)
            current_completeness_score = 100
            current_null = []
            for name in attributes:
                if data_dict[name] is None:
                    if name == 'address':
                        if data_dict['latitude'] is None or data_dict['longitude'] is None:
                            current_completeness_score -= units_completeness[attributes.index(name)]
                            current_null.append('latitude or longitude')
                        else:
                            current_completeness_score -= units_completeness[attributes.index(name)] / 2
                            current_null.append(name)
                    else:
                        current_completeness_score -= units_completeness[attributes.index(name)]
                        current_null.append(name)
                elif name == 'categories' or name == 'hours':
                    if re.search(r"(?i)(^none$)", str(data_dict[name])):
                        current_completeness_score -= units_completeness[attributes.index(name)]
                        current_null.append(name)
                elif len(data_dict[name]) == 0:
                    current_completeness_score -= units_completeness[attributes.index(name)]
                    current_null.append(name)

            score = current_completeness_score * 0.4
            completeness_scores.append(score)
            total_score = score + formatting_scores[counter]
            total_scores.append(total_score)

            all_scores.update({data_dict['business_id']: total_score})

            # separating into quality categories
            if total_score >= upper_bound:
                high_quality.write(item)
                high_quality_num += 1
                if total_score == upper_bound + 1:
                    high_medium_bordering.append(current_null)

            elif total_score >= lower_bound:
                medium_quality.write(item)
                medium_quality_num += 1
                if total_score == upper_bound - 1:
                    high_medium_bordering.append(current_null)
                elif total_score == lower_bound + 1:
                    medium_low_bordering.append(current_null)

            else:
                low_quality.write(item)
                low_quality_num += 1
                if total_score == lower_bound - 1:
                    medium_low_bordering.append(current_null)
            counter += 1

        high_quality.close()
        medium_quality.close()
        low_quality.close()
        num_records = high_quality_num + medium_quality_num + low_quality_num

        print('High quality records\nNumber:', str(int(high_quality_num / 1000)) + ',' +
              str(high_quality_num % 1000), 'Percentage:',
              round(float(high_quality_num / num_records) * 100, 2), '%\n')
        print('Medium quality records\nNumber:', str(int(medium_quality_num / 1000)) + ',' +
              str(medium_quality_num % 1000), 'Percentage:',
              round(float(medium_quality_num / num_records) * 100, 2), '%\n')
        print('Low quality records\nNumber:', str(int(low_quality_num / 1000)) + ',' +
              str(low_quality_num % 1000), 'Percentage:',
              round(float(low_quality_num / num_records) * 100, 2), '%\n')

        # print('High to medium: ', high_medium_bordering)
        # print('Medium to low: ', medium_low_bordering)
        # print('total scores', total_scores)

        plt.hist(total_scores, bins=20)
        plt.show()

        # print(all_scores)
