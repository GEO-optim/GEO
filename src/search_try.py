import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from readabilipy import simple_json_from_html_string
import trafilatura
import nltk
import openai
import os
import pickle
import uuid

openai.api_key = os.environ["OPENAI_API_KEY"]


def clean_source_gpt35(source : str) -> str:
    for idx in range(8):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                    "role": "user",
                    "content": f"Clean and refine the extracted text from a website. Remove any unwanted content such as headers, sidebars, and navigation menus. Retain only the main content of the page and ensure that the text is well-formatted and free of HTML tags, special characters, and any other irrelevant information. Refined text should contain the main intended readable text. Apply markdown formatting when outputting the answer.\n\nHere is the website:\n```html_text\n{source.strip()}```"
                    },
                ],
                temperature=0,
                max_tokens=1800,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            break
        except Exception as e:
            print(f'Error while cleaning text with openai {e}')
            source = source[:-int(800*(1 + idx/2))]
            time.sleep(3 + idx**2)
    # Store the usage in the folder response_usages, with a random file name
    pickle.dump(response.usage, open(f"response_usages/{uuid.uuid4()}.pkl", "wb"))

    tex = response.choices[0].message.content.strip()
    new_lines = [""]
    for line in tex.split('\n\n'):
        new_lines[-1] +=line+'\n'
        if len(nltk.sent_tokenize(line))!=1:
            new_lines.append("")
    new_lines = [x.strip() for x in new_lines]
    return "\n\n".join(new_lines)

def clean_source_text(text: str) -> str:
    return (
        text.strip()
        .replace("\n\n\n", "\n\n")
        .replace("\n\n", " ")
        .replace("  ", " ")
        .replace("\t", "")
        .replace("\n", "")
    )

import time
from pdb import set_trace as bp
import openai
import os


def summarize_text_identity(source, query) -> str:
    return source[:8000]


def search_handler(req, source_count = 8):
    query = req

    # GET LINKS
    for _ in range(5):
        try:
            response = requests.get(f"https://www.google.com/search?q={query}")
            break
        except Exception as e:
            print(f'Error while fetching from Google {e}')
            time.sleep(5)
            continue

    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    link_tags = soup.find_all('a')
    links = []

    for link in link_tags:
        href = link.get('href')

        if href and href.startswith('/url?q='):
            cleaned_href = href.replace('/url?q=', '').split('&')[0]

            if cleaned_href not in links:
                links.append(cleaned_href)
                print(cleaned_href)

    exclude_list = ["google", "facebook", "twitter", "instagram", "youtube", "tiktok","quora"]
    filtered_links = []
    links = set(list(links))
    for link in links:
        try:
            if urlparse(link).hostname.split('.')[1] not in exclude_list:
                filtered_links.append(link)
        except: ...
    filtered_links = [link for idx, link in enumerate(links) if urlparse(link).hostname.split('.')[1] not in exclude_list and links.index(link) == idx]

    final_links = filtered_links#[:source_count]

    # SCRAPE TEXT FROM LINKS
    sources = []

    for link in final_links:
        print(f'Will be loading link {link}')
        try:
            for _ in range(5):
                downloaded = trafilatura.fetch_url(link)
                source_text = trafilatura.extract(downloaded)
                if source_text is not None:
                    break
                
                print(f'Error fetching link {link}')
                time.sleep(4)
            if source_text is None:
                continue
            response = requests.get(link, timeout=15)
        except Exception as e:
            continue
        print('Link Loaded')
        html = response.text
        try:
            html = simple_json_from_html_string(html)
            html_text = html['content']
        except:
            try:
                from readabilipy.extractors import extract_title
                {
                    "title": extract_title(html),
                    "content": str(html)
                }
            except:
                continue
        if len(html_text) < 400:
            continue
        print(len(html_text))

        soup = BeautifulSoup(html_text, 'html.parser')

        if source_text:
            source_text = clean_source_text(source_text)
            print('Going to call openai')
            raw_source = source_text
            source_text = clean_source_gpt35(source_text[:8000])
            summary_text = summarize_text_identity(source_text, query)
            sources.append({'url': link, 'text': f'Title: {html["title"]}\nSummary:' + summary_text, 'raw_source' : raw_source, 'source' : source_text, 'summary' : summary_text})
            print('Openai Called')
        if len(sources) == source_count:
            break
    return {'sources': sources}
    
if __name__ == '__main__':
    import sys
    search_handler('What is Generative Engine Optimization?')
    import json
    print(json.dumps(search_handler(sys.argv[1]), indent = 2))