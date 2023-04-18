import streamlit as st
from urllib.parse import urlparse
import pandas as pd
from sklearn.cluster import KMeans
import plotly.express as px
from netdata_pandas.data import get_data

DEFAULT_HOST = 'london.my-netdata.io'
DEFAULT_URL = ''
DEFAULT_AFTER = -60*15
DEFAULT_BEFORE = 0
DEFAULT_TARGET_METRIC = 'system.cpu|user'
DEFAULT_CHARTS_REGEX = 'system|apps|users|services|groups\..*'
DEFAULT_FREQ = '15s'
DEFAULT_N_CLUSTERS = 20
DEFAULT_FIG_W = 900
DEFAULT_FIG_H = 25

st.set_page_config(page_title="Metric Clustering", page_icon="📈")

landing_text = """
Enter inputs and click "Run" in sidebar to generate the heatmap.
"""

st.markdown("# Metric Clustering")

run = st.sidebar.button('Run')
st.sidebar.header("Inputs")


url = st.sidebar.text_input('url', value=DEFAULT_URL, help='netdata agent dashboard url to pull host/after/before params from')
host = st.sidebar.text_input('host', value=DEFAULT_HOST, help='netdata host to pull data from')
after = st.sidebar.number_input('after', value=DEFAULT_AFTER)
before = st.sidebar.number_input('before', value=DEFAULT_BEFORE)
charts_regex = st.sidebar.text_input('charts_regex', value=DEFAULT_CHARTS_REGEX, help='regex to match charts')
opts = st.sidebar.text_area('opts', value=f'n_clusters={DEFAULT_N_CLUSTERS}\nfreq={DEFAULT_FREQ}\nfig_w={DEFAULT_FIG_W}\nfig_h={DEFAULT_FIG_H}', help='optional key=value params separated by new line')
opts_dict = {opt.split('=')[0].strip():opt.split('=')[1].strip() for opt in opts.split('\n')}
n_clusters = int(opts_dict.get('n_clusters',DEFAULT_N_CLUSTERS))
freq = str(opts_dict.get('freq',DEFAULT_FREQ))
fig_w = int(opts_dict.get('fig_w',DEFAULT_FIG_W))
fig_h = int(opts_dict.get('fig_h',DEFAULT_FIG_H))

if url != '':
    url_parsed = urlparse(url)
    url_fragments = {x.split('=')[0]:x.split('=')[1] for x in url_parsed.fragment.split(';') if '=' in x}
    host = f'{url_parsed.hostname}:{url_parsed.port}' if url_parsed.port else f'{url_parsed.hostname}'
    highlight_after = url_fragments.get('highlight_after')
    highlight_before = url_fragments.get('highlight_before')
    after = int(int(url_fragments.get('after')) / 1000)
    before = int(int(url_fragments.get('before')) / 1000)

if run:
    
    # get data from netdata
    df = get_data(
        hosts=[host], 
        after=after, 
        before=before, 
        charts_regex=charts_regex,
        freq=freq
        )
    print(df.shape)
    
    # normalize each column to be 0 to 1
    # https://en.wikipedia.org/wiki/Feature_scaling#Rescaling_(min-max_normalization)
    df = ( df-df.min() ) / ( df.max() - df.min() )

    # ffill and bfill any missing data
    df = df.ffill().bfill()

    # drop any columns that are all NaN
    df = df.dropna(axis=1,how='all')

    # get X matrix to feed into clustering
    X = df.transpose().dropna().values

    # cluster the data
    cluster = KMeans(n_clusters=n_clusters, n_init=5).fit(X)

    # sort based on clustering
    df_cols_sorted = pd.DataFrame(
        zip(df.columns, cluster.labels_),
        columns=['metric', 'cluster']
        ).sort_values('cluster', ascending=False)
    cols_sorted = df_cols_sorted['metric'].values.tolist()
    cols_renamed = [f'{c} ({i})' for c,i in zip(df_cols_sorted['metric'].values, df_cols_sorted['cluster'].values)]
    df = df[cols_sorted]
    df.columns = cols_renamed

    # create heatmap fig
    fig = px.imshow(df.transpose(), color_continuous_scale='Greens')
    fig.update_layout(
                autosize=False,
                width=fig_w,
                height=len(df.columns)*fig_h)

    # plot the heatmap
    st.plotly_chart(fig)

else:
    st.write(landing_text)



