import pandas as pd
import numpy as np
from llama_index import Document
from llama_index import ServiceContext
from llama_index import VectorStoreIndex, SimpleKeywordTableIndex, RAKEKeywordTableIndex#, KeywordTableIndex
from llama_index.llms import OpenAI
from llama_index.embeddings import OpenAIEmbedding
import os

def set_service_context():
    key = os.environ.get('OPENAI_API_KEY')
    service_context = ServiceContext.from_defaults(llm=OpenAI(api_key=key), embed_model=OpenAIEmbedding(api_key=key))
    return service_context

def get_index(index_name):
    Index = None
    if index_name == 'VectorStoreIndex':
        Index = VectorStoreIndex
    elif index_name == 'SimpleKeywordTableIndex':
        Index = SimpleKeywordTableIndex
    elif index_name == 'RAKEKeywordTableIndex':
        Index = RAKEKeywordTableIndex
    else:
        print('index name not imported')
    return Index

def gen_citation_db(service_context, index_name):
    '''
    Generate the vector db using the reasons for citation and save to disk.
    '''
    data = pd.read_csv('../data/FRB_citations_23.csv')

    # each doc should contain one reason for citation
    documents = []
    for i, row in data.iterrows():
        metadata = {
            'doc_id': str(i),
        }
        reasons = row['reasons'].replace("\n", "").split(';')
        for reason in reasons:
            if '*' in reason[:2]:
                # don't include ambiguous ones for now
                continue
            document = Document(text=reason, metadata=metadata)
            document.excluded_embed_metadata_keys = ['doc_id']
            documents.append(document)

    # create index
    Index = get_index(index_name)
    if Index is None:
        return
    index = Index.from_documents(
        documents,
        service_context=service_context,
        show_progress=True,
    )
    index.storage_context.persist(f'../data/llamaindex{index_name}_openaiEmbed_citation_db')

def gen_abstract_db(service_context, index_name):
    data = pd.read_csv('../data/FRB_abstracts.csv')

    # each doc should contain title and abstract
    documents = []
    for i, row in data.iterrows():
        metadata = {
            'doc_id': str(i),
        }
        text = row['title'] + ': ' + row['abstract']
        text = text.replace("\n", " ").lower()
        document = Document(text=text, metadata=metadata)
        document.excluded_embed_metadata_keys = ['doc_id']
        documents.append(document)

    # create index
    Index = get_index(index_name)
    if Index is None:
        return
    index = Index.from_documents(
        documents,
        service_context=service_context,
        show_progress=True,
    )
    index.storage_context.persist(f'../data/llamaindex{index_name}_openaiEmbed_abstract_db')

def main():
    service_context = set_service_context()
    for index_name in ['VectorStoreIndex',
                       'SimpleKeywordTableIndex',
                       'RAKEKeywordTableIndex']:
        gen_citation_db(service_context, index_name)
        gen_abstract_db(service_context, index_name)

if __name__ == '__main__':
    main()
