import streamlit as st
import pandas as pd
import altair as alt

# Set page config
st.set_page_config(page_title="DEI Arthur", page_icon=":bar_chart:", layout="wide")

# Load data from Google Sheets (replace with actual connection and data loading)
from streamlit_gsheets import GSheetsConnection
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read()

# Title and Subheader
st.title(" :bar_chart: Workforce Directory :bar_chart:")
st.subheader("Representation of different demographics")
st.divider()

# Inform the user what to do
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
    grouped_data = df.groupby([category1, category2]).size().reset_index(name='Frequencies')

    # Normalize the frequencies by dividing each count by the total for that category1
    grouped_data['Normalized'] = grouped_data.groupby(category1)['Frequencies'].transform(lambda x: x / x.sum())

    # Create Altair chart
    chart = alt.Chart(grouped_data).mark_bar().encode(
        x=alt.X(f'{category1}:N', title=category1),
        y=alt.Y('Normalized:Q', title='Proportion', axis=alt.Axis(format='%')),
        color=alt.Color(f'{category2}:N', title=category2),
        tooltip=[alt.Tooltip(f'{category1}:N', title=category1),
                 alt.Tooltip(f'{category2}:N', title=category2),
                 alt.Tooltip('Frequencies:Q', title='Frequencies'),
                 alt.Tooltip('Normalized:Q', title='Proportion', format='.2%')]
    ).properties(
        title=f'Normalized Frequencies of {category1} vs {category2}',
        width=800,
        height=600
    ).configure_title(
        fontSize=16,
        anchor='middle'
    )

    # Display the chart using st.altair_chart
    st.altair_chart(chart, use_container_width=True)

else:
    st.warning("Please select both categories to compare.")