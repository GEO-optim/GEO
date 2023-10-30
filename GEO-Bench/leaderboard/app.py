import gradio as gr
import pandas as pd


data = [
    ['**Baseline**', 19.7, 19.6, 19.8, 19.8, 19.8, 19.8, 19.8, 19.8, 19.8, 19.8, 19.8, "[[1]](https://arxiv.org/abs/2310.18xxx)"],
    ['**Keyword Stuffing**', 19.6, 19.5, 19.8, 20.8, 19.8, 20.4, 20.6, 19.9, 21.1, 21.0, 20.6, "[[1]](https://arxiv.org/abs/2310.18xxx)"],
    ['**Unique Words**', 20.6, 20.5, 20.7, 20.8, 20.3, 20.5, 20.9, 20.4, 21.5, 21.2, 20.9, "[[1]](https://arxiv.org/abs/2310.18xxx)"],
    ['**Simple Language**', 21.5, 22.0, 21.5, 21.0, 21.1, 21.2, 20.9, 20.6, 21.9, 21.4, 21.3, "[[1]](https://arxiv.org/abs/2310.18xxx)"],
    ['**Authoritative Language**', 21.3, 21.2, 21.1, 22.3, 22.9, 22.1, 23.2, 21.9, 23.9, 23.0, 23.1, "[[1]](https://arxiv.org/abs/2310.18xxx)"],
    ['**Technical Language**', 22.5, 22.4, 22.5, 21.2, 21.8, 20.5, 21.1, 20.5, 22.1, 21.2, 21.4, "[[1]](https://arxiv.org/abs/2310.18xxx)"],
    ['**Fluent Language**', 24.4, 24.4, 24.4, 21.3, 23.2, 21.2, 21.4, 20.8, 23.2, 21.5, 22.1, "[[1]](https://arxiv.org/abs/2310.18xxx)"],
    ['**Citation Addition**', 25.5, 25.3, 25.3, 22.8, 24.2, 21.7, 22.3, 21.3, 23.5, 21.7, 22.9, "[[1]](https://arxiv.org/abs/2310.18xxx)"],
    ['**Quotes Addition**', 27.5, 27.6, 27.1, 24.4, 26.7, 24.6, 24.9, 23.2, 26.4, 24.1, 25.5, "[[1]](https://arxiv.org/abs/2310.18xxx)"],
    ['**Adding Statistics**', 25.8, 26.0, 25.5, 23.1, 26.1, 23.6, 24.5, 22.4, 26.1, 23.8, 24.8, "[[1]](https://arxiv.org/abs/2310.18xxx)"]
]

# Column names
columns = ['Method', 'Word', 'Position', 'WordPos Overall', 'Rel.', 'Infl.', 'Unique', 'Div.', 'FollowUp', 'Pos.', 'Count', 'Subjective Average', 'Source']

# Create a DataFrame
DATA_OVERALL = pd.DataFrame(data, columns=columns)
DATA_OVERALL.sort_values(by=['WordPos Overall'], inplace=True, ascending=False)

with gr.Blocks() as demo:
    gr.Markdown(f"""
    # GEO-Bench Leaderboard, for benchmarking conent optimziation methods for Generative Engines.
    - To submit check [here](https://github.com/Pranjal2041/GEO/GEO-Bench/leaderboard/Readme.md)
    - Refer to GEO paper for more [details](https://arxiv.org/abs/2310.18xxx)
    """)

    with gr.Tabs():

        with gr.TabItem('Overall'):

            with gr.Row():
                gr.Markdown('## Overall Leaderboard')
            with gr.Row():
                data_overall = gr.components.Dataframe(
                    DATA_OVERALL,
                    datatype=["markdown"] + ["number"] * len(DATA_OVERALL.columns) + ['markdown'],
                    type="pandas",
                    wrap=True,
                    interactive=False,
                )
            with gr.Row():
                data_run_overall = gr.Button("Refresh")
                    # data_run_overall.click(get_mteb_average, inputs=None, outputs=data_overall)
 
                            

if __name__ == "__main__":
    demo.launch()