import pandas as pd
import numpy as np
import json
import sys
'''

The program finds competitor software from two datasets.

Input:
    software: the name of a software or a sub-category
    
Output:
    A JSON file in JSON array format (called competitor.txt).

Usage:
    python industry_name.py software

'''

class CompetitorAnalyst:

    # Reading in data
    def __init__(self, result_path, review_path):
        self.result_base = pd.read_csv(result_path, low_memory=False)
        self.result_base['total.reviews'].fillna(0, inplace=True)

        # Replacing NA values in the 'logo' column
        self.result_base['logo'].fillna("", inplace=True)

        self.review_base = pd.read_csv(review_path, low_memory=False)
        return

    def analyse_competitor(self, val, kind='business'):
        '''
        The analyse_competitor function takes user input software and finds all sub-categories associated with the software.
        '''
        if kind not in ['business', 'job_title']:
            raise ValueError('unsupported:' + kind)
        if val in self.result_base['software.name'].values.tolist():
            category = self.result_base[self.result_base['software.name']
                                        == val]['Sub.cat1'].values[0]
            self._analyse_cat(category, kind)
            return
        elif val in self.result_base['Sub.cat1'].values.tolist():
            self._analyse_cat(val, kind)
            return
        else:
            raise ValueError('wrong input:' + val)

    def _analyse_cat(self, category, kind='business'):
        '''
        The _analyse_cat function iterates through the list of categories found in the analyse_competitor function and creates a list of all competing software in the data with the same sub-category.
        '''
        cat_competitions = {}
        competitors = self.result_base.loc[self.result_base['Sub.cat1']
                                          == category]['software.name'].unique()
                                            
        competitor_count = 0
        competitor_list = []

        for software in competitors:
            competitor_count = competitor_count + 1
            competitor_list.append(software)

        value_competitions_list = []
        
        for software in competitors:
            value = self._analyse_software_in_review(
                software, kind)

            # Getting the logo for each software in competitors
            logo = self.result_base.loc[self.result_base['software.name']==software]['logo'].unique()

            value['Competitor'] = software

            # Adding the logo to the dataframe value
            value['Logo'] = logo[0]

            value = value.items()
            value_list = list(value)

            value_list = value_list[-2:] + value_list[:-2]

            value_dict = dict(value_list)
            value_competitions_list.append(value_dict)

        # Creating JSON file     
        with open(analyse_result_path, 'w') as f:
            json.dump(value_competitions_list, f, indent=4, separators=(',', ': '))
        return

    def _analyse_software_in_review(self, software, kind='business'):
        '''
        The _analyse_software_in_review function iterates through each software in the competitors list and retrieves total review information for each associated sub-category.
        '''
        tester = self.review_base.dropna(axis=0, subset=['business'])
        software_review = tester.loc[tester['software.name'] == software].copy()

        if kind == 'business':
            y = []
            for x in software_review['business']:
                y.append(x)
            software_review['business'] = y
        
        kind_of_software_review = software_review[[
            'software.name', kind]].dropna().groupby(kind).count()
        counters = kind_of_software_review['software.name'].sum()
        array_kind_of_software = np.array(
            kind_of_software_review['software.name'])
        a = pd.Series(np.around(np.true_divide(array_kind_of_software, counters), 2),
                      index=kind_of_software_review.index).to_dict()
        raw_total_review = self.result_base[self.result_base['software.name']
                                            == software]['total.reviews'].values[0]
        total_review = int(raw_total_review) if pd.notna(
            raw_total_review) else raw_total_review
        a['total.reviews'] = total_review

        my_list = list(a.items())
        for item in my_list:
            if item[0] == ' ':
                my_list.remove(item)
                a = dict(my_list)
                return a

        return a


result_base_path = r'data/result_base.csv'
review_base_path = r'data/review_base.csv'
analyse_cat = 'business'
analyse_result_path = r'data/industry_name.json'


def main():
    analyst_ins = CompetitorAnalyst(result_base_path, review_base_path)

    analyst_target = ''.join(sys.argv[1])

    try:
        analyst_ins.analyse_competitor(analyst_target, analyse_cat)
    except ValueError as e:
        print(e)
    else:
        print("complete")


if __name__ == '__main__':
    main()
