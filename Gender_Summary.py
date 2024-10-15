import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

st.set_page_config(page_title="DEI Arthur", page_icon=":bar_chart:",layout="wide")

from streamlit_gsheets import GSheetsConnection

# # Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read()

# Calculate the gender distribution
gender_counts = df['gender'].value_counts().reset_index()
gender_counts.columns = ['gender', 'Count']

# Calculate percentage from total
total = gender_counts['Count'].sum()
gender_counts['Percentage'] = (gender_counts['Count'] / total * 100).round(2)

# Define a consistent color scheme for genders
color_map = {
    'Male': '#90d5ff',       # Blue
    'Female': '#ffb5c0',     # Orange
}

# Title
st.title("Gender Summary")
st.subheader("Percentage of Gender in KG")

st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

# Create columns for the summary (side-by-side layout)
col1, col2 = st.columns(2)

# Display gender percentage summary
for i, row in gender_counts.iterrows():
    # Choose a column based on the index
    if i == 0:
        col = col1
    else:
        col = col2

    with col:
        st.markdown(f"""
        <div style='text-align: center'>
            <h5>{row['gender']}</h5>
            <h1><strong>{row['Percentage']}%</strong></h1>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

# Create a bar chart for Gender vs Frequency using Altair, sorted by frequency in descending order
bar_chart = alt.Chart(gender_counts).mark_bar().encode(
    x=alt.X('gender:N', title='Gender', sort='-y'),  # Sort by frequency (Count) in descending order
    y=alt.Y('Count:Q', title='Frequency'),
    color=alt.Color('gender:N', scale=alt.Scale(domain=list(color_map.keys()), range=list(color_map.values())), legend=None)
).properties(
    title='Gender Distribution (Bar Chart)',
    width=600,
    height=400
)

# Display the bar chart in Streamlit
st.altair_chart(bar_chart, use_container_width=True)

# Create a pie chart for Gender vs Frequency using Plotly with the same color scheme
pie_chart = px.pie(
    gender_counts, 
    names='gender', 
    values='Count', 
    title='Gender Distribution (Pie Chart)',
    color='gender',  # Apply consistent colors
    color_discrete_map=color_map,  # Use the same color map for the pie chart
    hole=0.4  # This makes it a donut chart; remove if you want a full pie chart
)

# Display the pie chart in Streamlit
st.plotly_chart(pie_chart, use_container_width=True)