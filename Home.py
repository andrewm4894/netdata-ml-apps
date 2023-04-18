import streamlit as st

st.set_page_config(page_title="Home", page_icon="🏠")

st.sidebar.success("Select an app above.")

st.write("# Netdata ML Apps")
st.write("A collection of little ML apps.")
st.markdown("""
         - [Metric Clustering](/Metric_Clustering) : Cluster your metrics on to a heatmap to find groups of similar patterns.
         - [Metric Similarity](/Metric_Similarity) : Given a metric of interest find what other metrics are most similar looking.
         """
)


