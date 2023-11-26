import openai
import time
import os
import pickle
import uuid

query_prompt = """Write an accurate and concise answer for the given user question, using _only_ the provided summarized web search results. The answer should be correct, high-quality, and written by an expert using an unbiased and journalistic tone. The user's language of choice such as English, Français, Español, Deutsch, or 日本語 should be used. The answer should be informative, interesting, and engaging. The answer's logic and reasoning should be rigorous and defensible. Every sentence in the answer should be _immediately followed_ by an in-line citation to the search result(s). The cited search result(s) should fully support _all_ the information in the sentence. Search results need to be cited using [index]. When citing several search results, use [1][2][3] format rather than [1, 2, 3]. You can use multiple search results to respond comprehensively while avoiding irrelevant search results.

Question: {query}

Search Results:
{source_text}
"""

openai.api_key = os.environ["OPENAI_API_KEY"]

def generate_answer(query, sources, num_completions, temperature = 0.5, verbose = False, model = 'gpt-3.5-turbo-16k'):

    openai.api_base = 'https://api.openai.com/v1'

    source_text = '\n\n'.join(['### Source '+str(idx+1)+':\n'+source + '\n\n\n' for idx, source in enumerate(sources)])
    prompt = query_prompt.format(query = query, source_text = source_text)

    while True:
        try:
            print('Running OpenAI Model')
            response = openai.ChatCompletion.create(
                model = model,
                temperature=temperature,
                max_tokens=1024,
                messages = [
                    # { 'role': "system", 'content': system_prompt },
                    { 'role': "user", 'content': prompt }
                ],
                top_p=1,
                n=num_completions,
            )
            print('Response Done')
            break
        except Exception as e:
            print('Error in calling OpenAI API', e)
            time.sleep(15)
            continue
    pickle.dump(response.usage, open(f"response_usages_16k/{uuid.uuid4()}.pkl", "wb"))

    return [x.message.content + '\n' for x in response.choices]