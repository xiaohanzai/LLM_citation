import numpy as np
from utils import convert_refdict_to_text

def cross_match_txt_and_ads(refs_txt, refs_ads, current_year):
    '''
    Cross match text ref dicts and ads ref dicts.
    Returns a pandas dataframe with columns 'txt_ref', 'arxiv_id', where
      'txt_ref' is the text reference string e.g. 'sloth & flash 2002a', 'sloth et al. 2020';
      'arxiv_id' is the arxiv id of the matched ads ref (in the case of no arxiv id available, it is a list of identifiers returned by ads).
    Later on I will combine a lot of pandas dataframes and match arxiv ids, so there might be different txt ref names.
    Details of the matching algorithm:
      Authors in ref_txt can be one, two, three (very rare), one + '...', collaboration + '...'
      Authors in ref_ads can be one, two, three, one + one + '...', collaboration + one + '...'
      I'm going to assume that any publication older by >=1 years are published
      TODO: the text ref dicts have no info of publisher; should in principle make use of that but scipdf is not good at the moment.
    '''

    rst = []

    for ref_txt in refs_txt:
        matched_refs_ads = []

        for ref_ads in refs_ads:
            flag = False # matched flag

            year = ref_ads['year']
            arxiv_year = ref_ads['arxiv_year']
            if int(current_year) - int(year) > 0: # assumed published if more than 1 year old
                arxiv_year = year # if published, shouldn't use arxiv year

            if ref_txt['authors'][-1] != '...': # <= 3 authors
                if ref_ads['authors'] == ref_txt['authors'] and\
                    (year == ref_txt['year'] or arxiv_year == ref_txt['year']):
                    flag = True
            else: # the et al. case
                if ref_ads['authors'][0] == ref_txt['authors'][0] and len(ref_ads['authors']) > 2 and\
                    (year == ref_txt['year'] or arxiv_year == ref_txt['year']):
                    flag = True
                elif 'collaboration' in ref_ads['authors'][0] and 'collaboration' not in ref_txt['authors'][0] and\
                    ref_ads['authors'][1] == ref_txt['authors'][0] and\
                    (year == ref_txt['year'] or arxiv_year == ref_txt['year']):
                    flag = True

            if flag:
                matched_refs_ads.append(ref_ads)

        # add to rst, one arxiv id per entry
        # need a flag for multiple matched ones
        # if both single entry, definitely matched (hopefully yes?)
        if len(matched_refs_ads) == 1 and ref_txt['pubdate'] == '':
            rst.append({'txt_ref': convert_refdict_to_text(ref_txt), 'arxiv_id': matched_refs_ads[0]['arxiv_id'], 'duplicate': False})
        # if both multiple entries, or if the author added papers that were not actually cited
        # TODO: currently there's no good way of telling which paper is which; people may also not label abcd according to pubdate
        elif len(matched_refs_ads) > 1:
            # inds = np.argsort([ref_ads['pubdate'] for ref_ads in matched_refs_ads])
            # ind = inds[ord(ref_txt['pubdate'])-ord('a')]
            # matched_arxiv_id = matched_refs_ads[ind]['arxiv_id']
            for r in matched_refs_ads:
                rst.append({'txt_ref': convert_refdict_to_text(ref_txt), 'arxiv_id': r['arxiv_id'], 'duplicate': True})
        # nothing matched
        # TODO: authors may also miss label... e.g. 2021 labeled as 2020b, then this is currently not considered as matched
        # else:
        #     rst.append({'txt_ref': convert_refdict_to_text(ref_txt), 'arxiv_id': '', 'duplicate': False})

    return rst
