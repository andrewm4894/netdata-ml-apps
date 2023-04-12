import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
import plotly.express as px
from netdata_pandas.data import get_data
from scipy.spatial.distance import cdist


st.set_page_config(page_title="Metric Similarity", page_icon="📈")

st.markdown("# Metric Similarity")

run = st.sidebar.button('Run')
st.sidebar.header("Inputs")


host = st.sidebar.text_input('host', value='london.my-netdata.io')
after = st.sidebar.number_input('after', value=-60*15)
before = st.sidebar.number_input('before', value=0)
target = st.sidebar.text_input('target', value='system.cpu|user')
charts_regex = st.sidebar.text_input('charts_regex', value='system|apps|users|services\..*')
freq = st.sidebar.text_input('freq', value='15s')
top_n = st.sidebar.number_input('top_n', value=10)

if run: 
    df = get_data(
        hosts=[host], 
        after=after, 
        before=before, 
        charts_regex=charts_regex,
        freq=freq
        )
    print(df.shape)
    df_raw = df.copy()
    df = (df - df.min()) / (df.max() - df.min())
    df = df.fillna(0)
    df_dist = pd.DataFrame(
        data=zip(df.columns, cdist(df[[target]].fillna(0).transpose(), df.fillna(0).transpose(), 'cosine')[0]),
        columns=['metric', 'distance']
    )
    df_dist['rank'] = (1 - df_dist['distance']).rank(ascending=False)
    df_dist = df_dist.sort_values('rank')
    plot_cols = df_dist.head(top_n)['metric'].values.tolist()
    
    st.dataframe(df_dist.head(top_n))
    
    for col in plot_cols:
        st.line_chart(df_raw[col])

else:
    st.write('Click "Run" to find similar metrics')



