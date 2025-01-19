from utils import get_answer, extract_citations_new, impression_subjective_impression, impression_wordpos_count_simple, impression_subjpos_detailed, impression_diversity_detailed, impression_uniqueness_detailed, impression_follow_detailed, impression_influence_detailed, impression_relevance_detailed, impression_subjcount_detailed, impression_pos_count_simple, impression_word_count_simple
from typing import List, Tuple
import numpy as np
import json
from geo_functions import *
import sys
import time
import os
from datasets import load_dataset

def identity(summary, source):
	return summary

IMPRESSION_FNS = {
	'simple_wordpos' : impression_wordpos_count_simple, 
	'simple_word' : impression_word_count_simple,
	'simple_pos' : impression_pos_count_simple,
	'subjective_score' : impression_subjective_impression,
	'subjpos_detailed' : impression_subjpos_detailed,
	'diversity_detailed' : impression_diversity_detailed,
	'uniqueness_detailed' : impression_uniqueness_detailed,
	'follow_detailed' : impression_follow_detailed,
	'influence_detailed' : impression_influence_detailed,
	'relevance_detailed' : impression_relevance_detailed,
	'subjcount_detailed' : impression_subjcount_detailed,
}


GEO_METHODS = {
	'identity' : identity,
	'fluent_gpt' : fluent_optimization_gpt,
	'unique_words_gpt' : unique_words_optimization_gpt,
	'authoritative_mine' : authoritative_optimization_mine,
	'more_quotes_mine' : more_quotes_mine,
	'citing_credible_mine': citing_credible_sources_mine,
	'simple_language_mine': simple_language_mine,
	'technical_terms_mine' : technical_terms_mine,
	'stats_optimization_gpt' : stats_optimization_mine,
	'seo_optimize_mine2' : seo_optimize_mine2,
}

EXTRACTIVE = False
loaded_cache = None
LAST_UPDATE_TIME = time.time()

def improve(query : str, idx : int, sources : List[str] = None, summaries : List[str] = None, impression_fn = impression_wordpos_count_simple, returnFullData = False, static_cache=os.environ.get('STATIC_CACHE', None)=='True') -> Tuple[np.array, List]: 
	global loaded_cache
	global LAST_UPDATE_TIME
	if static_cache:
		if loaded_cache is not None:
			modified_time = os.path.getmtime(os.environ.get('GLOBAL_CACHE_FILE', 'global_cache.json'))
			if modified_time - LAST_UPDATE_TIME > 0:
				loaded_cache = json.load(open(os.environ.get('GLOBAL_CACHE_FILE', 'global_cache.json')))
			LAST_UPDATE_TIME = 	modified_time

			pass
		else:
			loaded_cache = json.load(open(os.environ.get('GLOBAL_CACHE_FILE', 'global_cache.json')))
	else:
		loaded_cache = None
	# idx indicates the website to boost
	print('query is', query)
	answers = get_answer(query, summaries = summaries, num_completions = 5, n = 5, loaded_cache = loaded_cache)
	if sources is None:
		sources = [x['source'] for x in answers['sources']]
	if summaries is None:
		summaries = [x['summary'] for x in answers['sources']]

	answers = answers['responses'][-1]

	if impression_fn == impression_subjective_impression or  impression_fn == impression_subjpos_detailed or impression_fn == impression_diversity_detailed or impression_fn == impression_uniqueness_detailed or impression_fn == impression_follow_detailed or impression_fn == impression_influence_detailed or impression_fn == impression_relevance_detailed or impression_fn == impression_subjcount_detailed:
		orig_init_scores = np.array([impression_fn(x, query, 5, idx = idx) for x in answers])
		orig_init_scores = orig_init_scores[~np.all(orig_init_scores == 0, axis=1)]
	else:
		orig_init_scores = np.array([impression_fn(extract_citations_new(x), 5) for x in answers])
	
	init_scores = orig_init_scores.mean(axis=0)
	print('Init Scores: ', init_scores)
	improvements = []
	all_final_scores = []

	for meth_name in GEO_METHODS:

		summaries_copy = summaries[:idx] + [GEO_METHODS[meth_name](summaries[idx])] + summaries[idx+1:] 
		answers = get_answer(query, summaries = summaries_copy, num_completions = 5, n = 5, loaded_cache = loaded_cache)
		answers = answers['responses'][-1]
		if impression_fn == impression_subjective_impression or impression_fn == impression_subjpos_detailed or impression_fn == impression_diversity_detailed or impression_fn == impression_uniqueness_detailed or impression_fn == impression_follow_detailed or impression_fn == impression_influence_detailed or impression_fn == impression_relevance_detailed or impression_fn == impression_subjcount_detailed:
			final_scores = np.array([impression_fn(x, query, 5, idx = idx) for x in answers])
			final_scores = final_scores[~np.all(final_scores == 0, axis=1)]
		else:
			final_scores = [impression_fn(extract_citations_new(x), 5) for x in answers]
		all_final_scores.append(np.array(final_scores))
		final_scores = np.array(final_scores).mean(axis=0)
		print(final_scores)
		improvements.append((final_scores - init_scores))
	improvements = np.vstack(improvements)

	if returnFullData:
		return orig_init_scores, all_final_scores
	else:
		return improvements, improvements[:, idx] > 0


if __name__ == '__main__':
	dataset = load_dataset("GEO-Optim/geo-bench", 'test')
	for i, k in enumerate(dataset['test']):
		# Insert Metric here 
		print(improve(k['query'], idx = int(k['sugg_idx']), impression_fn=impression_wordpos_count_simple))
