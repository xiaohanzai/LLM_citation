import scipdf
import pandas as pd
import pickle

def main():
    arxiv_ids = pd.read_csv('../data/FRB_abstracts.csv')['arxiv_id'].values

    # get intro sections using scipdf
    for i in range(len(arxiv_ids)):
        arxiv_id = arxiv_ids[i][6:]
        # # for debugging
        # if arxiv_id not in ['2305.11302', '2305.09428', '2211.06048']:
        #     continue

        # run scipdf
        try:
            article_dict = scipdf.parse_pdf_to_dict('https://arxiv.org/pdf/%s.pdf' % arxiv_id, as_list=False)
        except:
            print(arxiv_id, 'ignored')
            continue

        # find out which one is intro section; usually 0
        ind = -1
        for j in range(len(article_dict['sections'])):
            # a better way is to include "motivation" or "background" in the heading
            # and identify whether "introduction" is in the first many characters in article_dict['sections'][j].text
            # but it looks like most of the things are fine
            if 'introduction' in article_dict['sections'][j]['heading'].lower() and article_dict['sections'][j]['n_publication_ref'] > 0:
                ind = j
                print(i, arxiv_id, 'using section', ind, 'intro sec')
                break
        # nature/science papers or some other wierd format papers...
        if ind < 0:
            if article_dict['sections'][0]['n_publication_ref'] > 0:
                ind = 0
                print(i, arxiv_id, 'using section 0')
        # nothing found then ignore
        if ind < 0:
            print(arxiv_id, 'no intro section found; first section also ignored')
            continue # somehow those papers are in disk... I probably ran some old codes of saving the 0th section a long time ago

        # save to disk
        with open('../data/%s.pickle' % arxiv_id, 'wb') as f:
            pickle.dump({'text': article_dict['sections'][ind], 'references': article_dict['references']}, f)

if __name__ == '__main__':
    main()
