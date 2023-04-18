import streamlit as st
from urllib.parse import urlparse
import pandas as pd
from netdata_pandas.data import get_data
from scipy.spatial.distance import cdist

DEFAULT_HOST = 'london.my-netdata.io'
DEFAULT_URL = ''
DEFAULT_AFTER = -60*15
DEFAULT_BEFORE = 0
DEFAULT_TARGET_METRIC = 'system.cpu|user'
DEFAULT_CHARTS_REGEX = 'system|apps|users|services|groups\..*'
DEFAULT_FREQ = '15s'
DEFAULT_TOP_N = 15

st.set_page_config(page_title="Metric Similarity", page_icon="📈")

landing_text = """
Enter inputs and click "Run" in sidebar to find similar metrics.
"""

st.markdown("# Metric Similarity")

run = st.sidebar.button('Run')
st.sidebar.header("Inputs")


url = st.sidebar.text_input('url', value=DEFAULT_URL, help='netdata agent dashboard url to pull host,after,before from')
host = st.sidebar.text_input('host', value=DEFAULT_HOST, help='netdata host to pull data from')
after = st.sidebar.number_input('after', value=DEFAULT_AFTER)
before = st.sidebar.number_input('before', value=DEFAULT_BEFORE)
target_metric = st.sidebar.text_input('target_metric', value=DEFAULT_TARGET_METRIC, help='metric to compare other metrics to')
charts_regex = st.sidebar.text_input('charts_regex', value=DEFAULT_CHARTS_REGEX, help='regex to match charts')
opts = st.sidebar.text_area('opts', value=f'freq={DEFAULT_FREQ}\ntop_n={DEFAULT_TOP_N}', help='optional key=value params separated by new line')
opts_dict = {opt.split('=')[0].strip():opt.split('=')[1].strip() for opt in opts.split('\n')}
freq = str(opts_dict.get('freq',DEFAULT_FREQ))
top_n = int(opts_dict.get('top_n',DEFAULT_TOP_N))

if url != '':
    url_parsed = urlparse(url)
    url_fragments = {x.split('=')[0]:x.split('=')[1] for x in url_parsed.fragment.split(';') if '=' in x}
    host = f'{url_parsed.hostname}:{url_parsed.port}' if url_parsed.port else f'{url_parsed.hostname}'
    highlight_after = url_fragments.get('highlight_after')
    highlight_before = url_fragments.get('highlight_before')
    after = int(int(url_fragments.get('after')) / 1000)
    before = int(int(url_fragments.get('before')) / 1000)

if run:
    
    # get data from agent 
    df = get_data(
        hosts=[host], 
        after=after, 
        before=before, 
        charts_regex=charts_regex,
        freq=freq
        )
    print(df.shape)
    
    # copy raw data for plotting later
    df_raw = df.copy()
    
    # normalize data for similarity calculation
    df = (df - df.min()) / (df.max() - df.min())
    df = df.fillna(0)
    
    # get metric distances
    df_dist = pd.DataFrame(
        data=zip(df.columns, cdist(df[[target_metric]].fillna(0).transpose(), df.fillna(0).transpose(), 'cosine')[0]),
        columns=['metric', 'distance']
    )
    
    # rank based on similarity
    df_dist['similarity'] = 1 - df_dist['distance']
    df_dist['rank'] = df_dist['similarity'].rank(ascending=False)
    
    # sort based on rank
    df_dist = df_dist.sort_values('rank')
    
    # get top_n most similar metrics
    df_dist_top_n = df_dist.head(top_n)
    df_dist_top_n = df_dist_top_n.set_index('metric')
    
    # get top_n cols to plot
    plot_cols = df_dist_top_n.index.values.tolist()
    
    # plot top_n cols similairty
    st.write('## Top {} most similar metrics'.format(top_n))
    st.dataframe(df_dist_top_n)
    
    # plot top_n most similar metrics
    for col in plot_cols:
        st.write(f"## {col} (similarity={100*df_dist_top_n.loc[col]['similarity']:0.2f}%)")
        st.line_chart(df_raw[col])

else:
    st.write(landing_text)



