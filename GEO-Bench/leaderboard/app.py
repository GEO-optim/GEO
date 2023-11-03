import gradio as gr
import pandas as pd
import os
import itertools
from constants import metric_dict, tags, columns

# Download from github and load the data

# TODO: Download every x hours
def download_data(url = "https://github.com/Pranjal2041/GEO/GEO-Bench/leaderboard/leaderboard.jsonl", path = "leaderboard.jsonl"):
    ret_code = os.system(f'wget {url} -O {path}_tmp')
    if ret_code != 0:
        return ret_code
    os.system(f'mv {path}_tmp {path}')
    return 0

def search_leaderboard(df, queries):
    # Assuming DATA_OVERALL is the DataFrame containing the leaderboard data
    # filtered_data = df[df["Method"].str.contains(query, case=False, na=False)]
    temp_pds = []
    for query in queries:
        temp_pds.append(df[df["Method"].str.contains(query, case=False, na=False)])
    return pd.concat(temp_pds).drop_duplicates()
 
def search_tags_leaderboard(df, tag_blocks, queries):
    return search_leaderboard(filter_tags(df, tag_blocks), queries)

def filter_tags(df, tag_blocks):
    def fuzzy_in(x, y_set):
        return any(x in z for z in y_set)
    all_tags_sets = [set(tag.lower() for tag in tag_block) for tag_block in tag_blocks]

    filtered_rows = [i for i, tags in enumerate(complete_dt['tags']) if all('any' in tag_set or any(fuzzy_in(tag.lower(), tag_set) for tag in tags) for tag_set in all_tags_sets)]

    return prepare_complete_dt(df.iloc[filtered_rows])

def prepare_complete_dt(complete_dt):
    data = []
    DATA_OVERALL = complete_dt.copy()
    for Method in set(complete_dt['Method']):
        data.append([])
        data[-1].append(Method)
        for metric in metric_dict:
            metric_val = metric_dict[metric]
            data[-1].append(complete_dt[complete_dt['Method'] == Method][metric_val].mean())
        data[-1].append(complete_dt[complete_dt['Method'] == Method]['source'].iloc[0])
        DATA_OVERALL = pd.DataFrame(data, columns=columns)
    try:
        DATA_OVERALL.sort_values(by=['WordPos Overall'], inplace=True, ascending=False)
    except: ...
    return DATA_OVERALL

def format_df_for_leaderboard(df):
    # The source column needs to be embedded directly into the Method column using appropriate markdown.
    df['Method'] = df[['source', 'Method']].apply(lambda x: f'<a target="_blank" style="text-decoration: underline; color: #3571d7;" href="{x[0]}">{x[1]}</a>', axis=1)
    # Convert all float metrics to 1 decimal
    df_copy = df.copy()
    for metric in metric_dict:
        df_copy[metric] = df_copy[metric].apply(lambda x: float(f'{(100*x):.1f}'))
    # drop the source column
    return df_copy.drop(columns=['source'])


ret_code = 0
# ret_code = download_data()
if ret_code != 0:
    print("Leaderboard Download failed")

complete_dt = pd.read_json('leaderboard.jsonl', lines=True, orient='records')
DATA_OVERALL = prepare_complete_dt(complete_dt)


with gr.Blocks() as demo:
    
    demo_content = """
<style>
  .badge-container {
    text-align: center;
    display: flex;
    justify-content: center;
  }
  .badge {
    margin: 1px;
  }
</style>
<h1 style="text-align: center;">GEO-Bench Leaderboard</h1>
<div class="badge-container">
    <a href="https://pranjal2041.github.io/geo/" class="badge">
        <img src="https://img.shields.io/website?down_message=down&style=for-the-badge&up_message=up&url=https%3A%2F%2Fpranjal2041.github.io/geo/" alt="Website">
    </a>
    <a href="https://arxiv.org/abs/2310.18xxx" class="badge">
        <img src="https://img.shields.io/badge/arXiv-2310.18xxx-red.svg?style=for-the-badge" alt="Arxiv Paper">
    </a>
    <a href="https://huggingface.co/datasets/Pranjal2041/geo-bench" class="badge">
        <img src="https://img.shields.io/badge/Dataset-GEO-%2DBENCH-orange?style=for-the-badge" alt="Dataset">
    </a>
    <a href="https://github.com/Pranjal2041/GEO" class="badge">
        <img src="https://img.shields.io/badge/Github-Code-green?style=for-the-badge" alt="Code">
    </a>
</div>
<p>
    - For benchmarking content optimization Methods for Generative Engines.<br>
    - GEO-Bench evaluates Methods for optimizing website content to improve visibility in generative engine responses. Benchmark contains 10K queries across 9 datasets covering diverse domains and intents.<br>
    - Refer to GEO paper for more <a href="https://arxiv.org/abs/2310.18xxx">details</a>
</p>
"""


    gr.HTML(demo_content)




    with gr.Tabs():

        with gr.TabItem('Overall 📊'):

            with gr.Row():
                gr.Markdown('## Overall Leaderboard')
            
            with gr.Row():
                data_overall = gr.components.Dataframe(
                    format_df_for_leaderboard(DATA_OVERALL),
                    datatype=["markdown"] + ["number"] * (len(DATA_OVERALL.columns) - 2) + ['markdown'],
                    type="pandas",
                    wrap=True,
                    interactive=False,
                )
                # data_overall.
        
            with gr.Row():
                # search_bar = gr.Textbox(type="text", label="Search for a Method:")
                search_bar = gr.Textbox(
                    placeholder=" 🔍 Search for your Method (separate multiple queries with `,`) and press ENTER...",
                    show_label=False,
                    elem_id="search-bar",
                )

                def search_button_click(query):
                    filtered_data = search_leaderboard(DATA_OVERALL, [x.strip() for x in query.split(',')])
                    return format_df_for_leaderboard(filtered_data)
                
        with gr.TabItem('Tag-Wise Results 📊'):
            with gr.Row():
                gr.Markdown(f"""
                ## Tag-Wise Results
                - The following table shows the results for each tag.
                - The tags are sorted in the order of their performance.
                - The table is sorted in the order of the overall score.
                """)
            with gr.Row():

                search_bar_tag = gr.Textbox(
                    placeholder=" 🔍 Search for your Method (separate multiple queries with `,`) and press ENTER...",
                    show_label=False,
                    elem_id="search-bar",
                )

                def search_button_click(query):
                    filtered_data = search_leaderboard(DATA_OVERALL, [x.strip() for x in query.split(',')])
                    return format_df_for_leaderboard(filtered_data)

            with gr.Row():
                boxes = dict()
                with gr.Column(min_width=320):
                    for tag in list(tags.keys())[:3]:
                        with gr.Box(elem_id="box-filter"):
                            boxes[tag] = gr.CheckboxGroup(
                                label=tag,
                                choices=tags[tag],
                                value=tags[tag],
                                interactive=True,
                                elem_id=f"filter-{tag}",
                            )
                with gr.Column(min_width=320):
                    for tag in list(tags.keys())[4:]:
                        with gr.Box(elem_id="box-filter"):
                            boxes[tag] = gr.CheckboxGroup(
                                label=tag,
                                choices=tags[tag],
                                value=tags[tag],
                                interactive=True,
                                elem_id=f"filter-{tag}",
                            )
            with gr.Row():
                tag = list(tags.keys())[3]
                with gr.Box(elem_id="box-filter"):
                    boxes[tag] = gr.CheckboxGroup(
                        label=tag,
                        choices=tags[tag],
                        value=tags[tag],
                        interactive=True,
                        elem_id=f"filter-{tag}",
                    )
            with gr.Row():
                data_tag_wise = gr.components.Dataframe(
                    format_df_for_leaderboard(DATA_OVERALL),
                    datatype=["markdown"] + ["number"] * (len(DATA_OVERALL.columns) - 2) + ['markdown'],
                    type="pandas",
                    wrap=True,
                    interactive=False,
                )
            def filter_tag_click(*boxes):
                return format_df_for_leaderboard(filter_tags(complete_dt, list(boxes)))
            def search_tag_click(query, *boxes):
                return format_df_for_leaderboard(search_tags_leaderboard(complete_dt, list(boxes), [x.strip() for x in query.split(',')]))
            for box in boxes:
                boxes[box].change(fn=filter_tag_click, inputs=list(boxes.values()), outputs=data_tag_wise)
                search_bar_tag.submit(fn=search_tag_click, inputs=[search_bar_tag] + list(boxes.values()), outputs=data_tag_wise)

        with gr.TabItem('About GEO-bench 📖'):
            with gr.Row():
                gr.Markdown(f"""
                ## About GEO-bench
                - GEO-bench is a benchmarking platform for content optimization Methods for generative engines.
                - It is a part of the work released under [GEO](https://arxiv.org/abs/2310.18xxx)
                - The benchmark comprises of 9 datasets, 7 of which were publicly available, while 2 have been released by us.
                - Dataset can be downloaded from [here](huggingface.co/datasets/pranjal2041/geo-bench)""")

            with gr.Row():

                # Goal of benchmarking content optimization for generative engines
                # Contains 10K carefully curated queries
                # Queries are diverse and cover many domains/intents
                # Annotated with tags/dimensions like domain, difficulty, etc.
                # Above list in HTML format
                gr.HTML(f"""
                <h3>Key-Highlights of GEO-bench</h3>
                <ul>
                    <li>Goal of benchmarking content optimization for generative engines</li>
                    <li>Contains 10K carefully curated queries</li>
                    <li>Queries are diverse and cover many domains/intents</li>
                    <li>Annotated with tags/dimensions like domain, difficulty, etc.</li>
                </ul>
                """)

                # Benchmark Link:
                # gr.Markdown(f"""### Benchmark Link: [GEO-bench](huggingface.co/datasets/pranjal2041/geo-bench)""")

                # Info about tags and other statistics
                            

        with gr.TabItem('Submit 📝'):
            with gr.Row():
                gr.Markdown(f"""
                ## Submit
                - To submit your Method, please check [here](github.com/Pranjal2041/GEO/GEO-Bench/leaderboard/Readme.md)""")


                # Create a form to submit, the response should be sent to a google form
                            
        search_bar.submit(fn=search_button_click, inputs=search_bar, outputs=data_overall)

if __name__ == "__main__":
    demo.launch()