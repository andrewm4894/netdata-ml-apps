import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
import plotly.express as px
from netdata_pandas.data import get_data


st.set_page_config(page_title="Metric Clustering", page_icon="📈")

landing_text = """
Enter inputs and click "Run" in sidebar to generate the heatmap.
"""

st.markdown("# Metric Clustering")

run = st.sidebar.button('Run')
st.sidebar.header("Inputs")


host = st.sidebar.text_input('host', value='london.my-netdata.io')
after = st.sidebar.number_input('after', value=-60*15)
before = st.sidebar.number_input('before', value=0)
charts_regex = st.sidebar.text_input('charts_regex', value='system|apps|users|services\..*', help='regex to match charts')
opts = st.sidebar.text_area('opts', value='n_clusters=15\nfreq=15s\nfig_w=900\nfig_h=25', help='optional key=value params separated by new line')
opts_dict = {opt.split('=')[0].strip():opt.split('=')[1].strip() for opt in opts.split('\n')}
n_clusters = int(opts_dict.get('n_clusters','15'))
freq = str(opts_dict.get('freq','15s'))
fig_w = int(opts_dict.get('fig_w','900'))
fig_h = int(opts_dict.get('fig_h','25'))


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



