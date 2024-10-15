import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

st.set_page_config(page_title="DEI Arthur", page_icon=":bar_chart:",layout="wide")

from streamlit_gsheets import GSheetsConnection

# # Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read()

# Calculate the generation distribution
generation_counts = df['generation'].value_counts().reset_index()
generation_counts.columns = ['generation', 'Count']

# Calculate percentage from total
total = generation_counts['Count'].sum()
generation_counts['Percentage'] = (generation_counts['Count'] / total * 100).round(2)

# Define a consistent color scheme for generations
color_map = {
    'Boomers': '#1f77b4',    # Blue
    'Gen X': '#ff7f0e',      # Orange
    'Gen Y': '#2ca02c',      # Green
    'Gen Z': '#d62728',      # Red
    'Post War': '#9467bd'    # Purple
}

# Title
st.title("Generation Summary")
st.subheader("Percentage of Generation in KG")

st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

# Create columns for the summary (side-by-side layout)
col1, col2, col3, col4, col5 = st.columns(5)

# Display generation percentage summary
for i, row in generation_counts.iterrows():
    # Choose a column based on the index
    if i == 0:
        col = col1
    elif i == 1:
        col = col2
    elif i == 2:
        col = col3
    elif i == 3:
        col = col4
    else:
        col = col5

    with col:
        st.markdown(f"""
        <div style='text-align: center'>
            <h5>{row['generation']}</h5>
            <h1><strong>{row['Percentage']}%</strong></h1>
        </div>
        """, unsafe_allow_html=True)

# Add a horizontal rule to divide the charts
st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

# Create a bar chart for Generation vs Frequency using Altair, sorted by frequency in descending order
bar_chart = alt.Chart(generation_counts).mark_bar().encode(
    x=alt.X('generation:N', title='Generation', sort='-y'),  # Sort by frequency (Count) in descending order
    y=alt.Y('Count:Q', title='Frequency'),
    color=alt.Color('generation:N', scale=alt.Scale(domain=list(color_map.keys()), range=list(color_map.values())), legend=None)
).properties(
    title='Generation Distribution (Bar Chart)',
    width=600,
    height=400
)

# Display the bar chart in Streamlit
st.altair_chart(bar_chart, use_container_width=True)

# Create a pie chart for Generation vs Frequency using Plotly with the same color scheme
pie_chart = px.pie(
    generation_counts, 
    names='generation', 
    values='Count', 
    title='Generation Distribution (Pie Chart)',
    color='generation',  # Apply consistent colors
    color_discrete_map=color_map,  # Use the same color map for the pie chart
    hole=0.4  # This makes it a donut chart; remove if you want a full pie chart
)

# Display the pie chart in Streamlit
st.plotly_chart(pie_chart, use_container_width=True)
