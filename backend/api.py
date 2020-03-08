import os
import string
import pickle
import spacy
import numpy as np
from collections import defaultdict
import xml.etree.cElementTree as ET

from django.http import JsonResponse
from django.conf import settings

nlp = spacy.load('en_core_web_sm')

def tokenize(query):
    """
    Given a text query, returns a list of Nouns and NPs (all stemmed)
    """
    doc = nlp(query)

    noun_phrases = [chunk.lemma_.lower() for chunk in doc.noun_chunks]
    nouns = [token.lemma_.lower() for token in doc if token.pos_ == 'NOUN']

    all_queries = list( set( noun_phrases + nouns ))
    
    return all_queries


def load_xml_to_dict():
    """
    Parses the rare genetic diseases and associated phenotypes XML file
    creates two dictionaries:
        phenotype_tok_dict - maps token -> list of phenotypes
        phenotype_data - maps phenotype -> list of diagnoses
    """

    # if there is a pickle file use that (pre loaded)
    try:
        with open('data.pickle', 'rb') as f:
            phenotype_tok_dict, phenotype_data = pickle.load(f)
        return phenotype_tok_dict, phenotype_data

    # if not, build dictionaries
    except FileNotFoundError:

        visited_phenotypes = []
        phenotype_tok_dict = defaultdict(list)
        phenotype_data = defaultdict(list)

        # dict to convert frequencies to (average between range) values
        frequency_dict = {
            'Obligate (100%)': 1.0,
            'Very frequent (99-80%)': 0.90,
            'Frequent (79-30%)': 0.55,
            'Occasional (29-5%)': 0.18,
            'Very rare (<4-1%)': 0.03,
            'Excluded (0%)': 0.0,
        }

        # load XML
        data_file_path = os.path.join(settings.BASE_DIR, 'data.xml')
        tree = ET.parse(data_file_path)
        root = tree.getroot()

        disorder_query = 'DisorderList/Disorder'
        phenotype_query = 'HPODisorderAssociationList/HPODisorderAssociation'

        for disorder in root.findall(disorder_query):

            disorder_name = disorder.find('Name').text.lower()
            orpha_number = disorder.find('OrphaNumber').text

            # look through all phenotypes for a given disorder
            for phenotype in disorder.findall(phenotype_query):

                phenotype_name = phenotype.find('HPO/HPOTerm').text.lower()
                frequency_text = phenotype.find('HPOFrequency/Name').text

                if phenotype_name not in visited_phenotypes:
                    visited_phenotypes.append(phenotype_name)

                    # add tokens to dict and store phenotypes in list
                    phenotype_toks = tokenize(phenotype_name)
                    for tok in phenotype_toks:
                        phenotype_tok_dict[tok].append(phenotype_name)

                # add phenotypes to list and store diagnoses in a list
                phenotype_data[phenotype_name].append({
                    'disorder_id': orpha_number,
                    'disorder': disorder_name,
                    'frequency': frequency_dict[frequency_text] # get average frequency from dict above
                    })

        return phenotype_tok_dict, phenotype_data


def search_phenotypes(request):
    """
    Given a search query return list of possible genetic diseases and probabilites
    """

    query = request.GET.get('q', '')
    search_terms = tokenize(query)

    phenotype_tok_dict, diagnosis_dict = load_xml_to_dict()

    disorder_probs = {}
    phenotype_matches = {}
    match_count = 0
    for search_term in search_terms:

        # if no match keep looking
        if search_term not in phenotype_tok_dict:
            continue
        match_count += 1 # keep track of how many search terms have associated phenotypes

        # look through all possible phenotypes and count how many tokens match the phenotype
        for p in phenotype_tok_dict[ search_term ]:
            if p not in phenotype_matches:
                phenotype_matches[p] = 0
            phenotype_matches[p] += 1 # keep track of how many matches there are for a given phenotype


    # store all possible diagnoses for possible phenotypes
    max_shared = 0
    for phenotype in phenotype_matches.keys():
        for d in diagnosis_dict[phenotype]:
            disorder_name = d['disorder']

            # initiate with orpha id and empty list to be filled with probabilities
            if disorder_name not in disorder_probs:
                disorder_probs[disorder_name] = [d['disorder_id'], []]

            # store frequencies
            # frequency equals prob of having the phenotype with the disorder * prob of searching the phenotype
            # (ie how many search terms match the phenotype / all the search terms) (this is not the best way to do this)
            disorder_probs[disorder_name][1].append( np.exp( np.log(d['frequency']) + np.log( phenotype_matches[phenotype]/match_count ) ) )
            
            # keep track of which disorders have the the most phenotype matches
            max_shared = max(max_shared, len(disorder_probs[disorder_name][1]))

    # format results and create link
    results = [{
        'disorder': d,
        'prob': sum(disorder_probs[d][1])/max_shared,
        'link': 'https://www.orpha.net/consor/cgi-bin/OC_Exp.php?lng=en&Expert=%s' % disorder_probs[d][0]} for d in disorder_probs.keys()]

    # filter results which are improbable and sort
    results = list(filter(lambda r: r['prob'] > 0.05, results))
    results = sorted(results, key=lambda d: d['prob'], reverse=True) 

    return JsonResponse({'results': results})

