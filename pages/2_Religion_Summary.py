import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

st.set_page_config(page_title="DEI Arthur", page_icon=":bar_chart:",layout="wide")

from streamlit_gsheets import GSheetsConnection

# # Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read()

# Calculate the religion distribution
religion_counts = df['Religious Denomination Key'].value_counts().reset_index()
religion_counts.columns = ['Religious Denomination Key', 'Count']

# Calculate percentage from total
total = religion_counts['Count'].sum()
religion_counts['Percentage'] = (religion_counts['Count'] / total * 100).round(2)

# Define a consistent color scheme for religions
color_map = {
    'Buddha': '#1f77b4',       # Blue
    'Hindu': '#ff7f0e',        # Orange
    'Islam': '#2ca02c',        # Green
    'Katholik': '#d62728',     # Red
    'Kepercayaan': '#9467bd',  # Purple
    'Kong Hu Cu': '#8c564b',   # Brown
    'Kristen': '#e377c2'       # Pink
}

# Title
st.title("Religion Summary")
st.subheader("Percentage of Religion in KG")

st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)


# Create columns for the summary (side-by-side layout)
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

# Display religion percentage summary
for i, row in religion_counts.iterrows():
    # Choose a column based on the index
    if i == 0:
        col = col1
    elif i == 1:
        col = col2
    elif i == 2:
        col = col3
    elif i == 3:
        col = col4
    elif i == 4:
        col = col5
    elif i == 5:
        col = col6
    else:
        col = col7

    with col:
        st.markdown(f"""
        <div style='text-align: center'>
            <h5>{row['Religious Denomination Key']}</h5>
            <h1><strong>{row['Percentage']}%</strong></h1>
        </div>
        """, unsafe_allow_html=True)

# Add a horizontal rule to divide the charts
st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

# Create a bar chart for Religion vs Frequency using Altair, sorted by frequency in descending order
bar_chart = alt.Chart(religion_counts).mark_bar().encode(
    x=alt.X('Religious Denomination Key:N', title='Religion', sort='-y'),  # Sort by frequency (Count) in descending order
    y=alt.Y('Count:Q', title='Frequency'),
    color=alt.Color('Religious Denomination Key:N', scale=alt.Scale(domain=list(color_map.keys()), range=list(color_map.values())), legend=None)
).properties(
    title='Religion Distribution (Bar Chart)',
    width=600,
    height=400
)

# Display the bar chart in Streamlit
st.altair_chart(bar_chart, use_container_width=True)

# Create a pie chart for Religion vs Frequency using Plotly with the same color scheme
pie_chart = px.pie(
    religion_counts, 
    names='Religious Denomination Key', 
    values='Count', 
    title='Religion Distribution (Pie Chart)',
    color='Religious Denomination Key',  # Apply consistent colors
    color_discrete_map=color_map,  # Use the same color map for the pie chart
    hole=0.4  # This makes it a donut chart; remove if you want a full pie chart
)

# Display the pie chart in Streamlit
st.plotly_chart(pie_chart, use_container_width=True)