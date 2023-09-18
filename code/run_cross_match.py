import glob
import re
import pandas as pd
import os
from refs_txt_functions import extract_txt_refs
from refs_ads_functions import get_ads_refs
from cross_match_functions import cross_match_txt_and_ads
from utils import get_year_from_arxivid
# import json

def add_new_entries(rst_full, rst, reason):
    '''
    rst is a list returned by cross_match_txt_and_ads().
    reason is the string explaining the reason of citing the references in rst.
    rst_full is the pandas dataframe that we need to combine rst and reason into.
    '''
    for entry in rst:
        ind = -1 # indicate whether there's the same arxiv_id in rst_full already
        for i in range(len(rst_full)):
            if rst_full.iloc[i]['arxiv_id'] == entry['arxiv_id']:
                ind = i
        if ind >= 0:
            if entry['txt_ref'] not in rst_full.iloc[ind]['txt_ref']:
                rst_full.iloc[ind]['txt_ref'] += '; ' + entry['txt_ref']
            rst_full.iloc[ind]['reasons'] += '; '
            if entry['duplicate']:
                rst_full.iloc[ind]['reasons'] += '*'
            rst_full.iloc[ind]['reasons'] += reason
        else: # create new row
            r = reason
            if entry['duplicate']:
                r = '*' + reason
            rst_full.loc[len(rst_full)] = {
                'txt_ref': entry['txt_ref'], 'arxiv_id': entry['arxiv_id'], 'reasons': r}

def read_data_and_cross_match(fname, refs_ads, current_year, rst_full):
    json_file = False
    with open(fname) as f:
        lines = f.readlines()
        if lines[0][0] == '{':
            json_file = True

        i = 0
        while i < len(lines):
            line = lines[i]
            if ':' not in line or 'N/A' in line:
                i += 1
                continue

            refs_txt = extract_txt_refs(line) # list of ref dicts

            if len(refs_txt) > 0:
                # the reason for citation
                ind = line.index(':')+1
                reason = None
                if json_file:
                    tmp = line[ind:]
                    reason = tmp[tmp.index('"')+1:tmp.rindex('"')].lower()
                else:
                    if re.search(r'(cited|referenced|mentioned)', line.lower()[ind:]):
                        reason = line.lower()[ind:]
                    elif re.search(r'(cited|referenced|mentioned)', lines[i+1].lower()):
                        reason = lines[i+1].lower()
                        i += 1

                # cross match with ads
                rst = cross_match_txt_and_ads(refs_txt, refs_ads, current_year)
                # add to results
                if reason is not None:
                    add_new_entries(rst_full, rst, reason)

            i += 1

def main():
    fnames = glob.glob('../data/2[23]*txt')
    token = os.environ.get('ADS_API_TOKEN')

    rst_full = pd.DataFrame(columns=['txt_ref', 'arxiv_id', 'reasons'])

    for fname in fnames:
        current_arxiv_id = fname[fname.rindex('/')+1:-4]
        current_year = get_year_from_arxivid(current_arxiv_id)

        refs_ads = get_ads_refs(current_arxiv_id, token)

        read_data_and_cross_match(fname, refs_ads, current_year, rst_full)

    rst_full.to_csv('../data/data_23.csv', index=False)

if __name__ == '__main__':
    main()
