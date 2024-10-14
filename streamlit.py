import streamlit as st
import plotly.express as px
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="DEI Arthur", page_icon=":bar_chart:",layout="wide")

from streamlit_gsheets import GSheetsConnection

# # Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read()

st.title(" :bar_chart: Workforce Directory :bar_chart:")
st.subheader("Representation of different demographics")

st.divider()

st.write("Compare Two Categories")

# Create two columns for side-by-side selection
col1, col2 = st.columns(2)

# Get available columns and add a placeholder for "empty" selection
available_columns = list(df.columns)
placeholder = "Select..."

# Dropdowns for user selection placed in columns with empty as initial selection
with col1:
    category1 = st.selectbox('Choose first category', [placeholder] + available_columns)

# For second category, exclude the selected first category
if category1 != placeholder:
    remaining_columns = [col for col in available_columns if col != category1]
else:
    remaining_columns = available_columns

with col2:
    category2 = st.selectbox('Choose second category', [placeholder] + remaining_columns)

# Ensure both categories are selected before proceeding
if category1 != placeholder and category2 != placeholder:
    # Group data by the selected categories and get frequencies
    grouped_data = df.groupby([category1, category2]).size().unstack().fillna(0)

    # Display the normalized stacked bar chart using st.bar_chart
    st.subheader(f'Normalized Frequencies of {category1} vs {category2}')
    st.bar_chart(grouped_data, stack="normalize", width=800, height=600)
else:
    st.warning("Please select both categories to compare.")