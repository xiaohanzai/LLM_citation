import re

def get_year_from_arxivid(arxiv_id):
    '''
    Get year of submission from arxiv id.
    '''
    arxiv_year = re.search(r'\d{2}', arxiv_id).group(0)
    if int(arxiv_year[0]) < 5:
        arxiv_year = '20' + arxiv_year
    else:
        arxiv_year = '19' + arxiv_year
    return arxiv_year

def convert_refdict_to_text(ref):
    '''
    Convert a reference dict to text format.
    Ref dict is like {'authors': ['sloth', 'flash'], 'year': '2002', 'pubdate': 'a'}.
    Return a string like 'sloth & flash (2002a)'.
    '''
    string = ref['authors'][0]
    if ref['authors'][-1] == '...':
        string += ' et al.'
    elif len(ref['authors']) == 2:
        string += ' & ' + ref['authors'][1]
    elif len(ref['authors']) == 3: # should be rare
        string += ',' + ref['authors'][1] + ', & ' + ref['authors'][2]

    string += ' ' + ref['year']
    if len(ref['pubdate']) == 1: # because if ads ref dict, pub date is the actual publication date
        string += ref['pubdate']

    return string
