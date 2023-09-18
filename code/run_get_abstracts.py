import arxiv
import numpy as np
import os
# from refs_ads_functions import call_ads_api, extract_ads_refs
# from utils import convert_refdict_to_text
import pandas as pd

def main():
    # load arxiv ids
    arxiv_ids = np.load('../data/FRB_arxivIDs.npy')

    # # ads api token; need to query ads for authors and actual publish year
    # token = os.environ.get('ADS_API_TOKEN')

    # will save data to a pandas df
    df = pd.DataFrame(columns=['arxiv_id', 'authors', 'title', 'abstract', 'category'])

    # these papers should not be ignored... this was a manual inspection
    ids_do_not_ignore = ['1309.4451', '1308.4797', '1401.6674', '1408.0411', '1410.4323',
                        '1411.5373', '1412.7825', '1512.06245', '1609.01694', '1705.01278', '1712.04226',
                        '1801.03841', '1808.10636', '2012.09495', '2107.09687', '2301.12103']

    # call arxiv API to get titles and abstracts
    n = 100
    for i in range(0,len(arxiv_ids),n):
        search = arxiv.Search(id_list=arxiv_ids[i:i+n], max_results=n)
        for article in search.results():
            # ignore flag
            flag = False

            # arxiv id
            arxiv_id = article.get_short_id()
            if 'v' in arxiv_id:
                arxiv_id = arxiv_id[:arxiv_id.index('v')]
            
            # double check non-astro papers
            primary_category = article.primary_category
            if 'astro-ph' not in primary_category:
                flag = True

            # make sure fast radio burst or frb is indeed in title or abstract
            tmp = article.title.lower() + ' ' + article.summary.lower()
            tmp = tmp.replace('\n', ' ')
            if 'fast radio burst' not in tmp and 'frb' not in tmp:
                flag = True

            # ignore papers
            if flag and arxiv_id not in ids_do_not_ignore:
                print('ignored:', arxiv_id, article.title)
                continue

            # # query ads
            # ads_data = extract_ads_refs(call_ads_api(arxiv_id, token, get_refs=False))[0]
            # # the txt name of the paper, e.g. sloth et al. 2020
            # ref_name = convert_refdict_to_text(ads_data)

            # author names
            authors = ''
            if len(article.authors) <= 3:
                for author in article.authors:
                    authors += author.name + ', '
            else:
                authors = article.authors[0].name + ' et al.'

            # add to df
            df.loc[len(df)] = {'arxiv_id': 'arXiv:' + arxiv_id, # just to make sure pd dumps it as a string...
                'authors': authors, 'title': article.title, 'abstract': article.summary.replace('\n', ' '),
                'category': article.primary_category}

    print('total number of papers:', len(df))

    # dump to disk
    df.to_csv('../data/FRB_abstracts.csv', index=False)

if __name__ == '__main__':
    main()
