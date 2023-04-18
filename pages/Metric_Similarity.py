import streamlit as st
import pandas as pd
from netdata_pandas.data import get_data
from scipy.spatial.distance import cdist


st.set_page_config(page_title="Metric Similarity", page_icon="📈")

landing_text = """
Enter inputs and click "Run" in sidebar to find similar metrics.
"""

st.markdown("# Metric Similarity")

run = st.sidebar.button('Run')
st.sidebar.header("Inputs")


host = st.sidebar.text_input('host', value='london.my-netdata.io')
after = st.sidebar.number_input('after', value=-60*15)
before = st.sidebar.number_input('before', value=0)
target_metric = st.sidebar.text_input('target_metric', value='system.cpu|user', help='metric to compare other metrics to')
charts_regex = st.sidebar.text_input('charts_regex', value='system|apps|users|services\..*', help='regex to match charts')
opts = st.sidebar.text_area('opts', value='freq=15s\ntop_n=50', help='optional key=value params separated by new line')
opts_dict = {opt.split('=')[0].strip():opt.split('=')[1].strip() for opt in opts.split('\n')}
print(opts_dict)
freq = str(opts_dict.get('freq','15s'))
top_n = int(opts_dict.get('top_n','50'))

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
    print(df_dist_top_n[['similarity', 'rank']].to_dict(orient='index'))
    
    # plot top_n most similar metrics
    for col in plot_cols:
        st.write(f"## {col} (similarity={100*df_dist_top_n.loc[col]['similarity']:0.2f}%)")
        st.line_chart(df_raw[col])

else:
    st.write(landing_text)



