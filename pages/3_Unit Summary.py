import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

st.set_page_config(page_title="DEI Arthur", page_icon=":bar_chart:",layout="wide")

from streamlit_gsheets import GSheetsConnection

# # Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read()

# Calculate the unit distribution
unit_counts = df['unit'].value_counts().reset_index()
unit_counts.columns = ['unit', 'Count']

# Calculate percentage from total
total = unit_counts['Count'].sum()
unit_counts['Percentage'] = (unit_counts['Count'] / total * 100).round(2)

# Define a consistent color scheme for units
color_map = {
    'CFL': '#1f77b4',       # Blue
    'CHR': '#ff7f0e',       # Orange
    'CITIS': '#2ca02c',     # Green
    'CORCOMM': '#d62728',   # Red
    'CORCOMP': '#9467bd',   # Purple
    'CORSEC': '#8c564b',    # Brown
    'DYANDRA': '#e377c2',   # Pink
    'GOHR': '#7f7f7f',      # Gray
    'GOMAN': '#bcbd22',     # Olive
    'GOMED': '#17becf',     # Teal
    'GORP': '#aec7e8',      # Light Blue
    'KG': '#ffbb78',        # Light Orange
    'KG PRO': '#98df8a',    # Light Green
    'REKATA': '#ff9896',    # Light Red
    'UMN': '#c5b0d5'       # Light Purple
}

# Separate the units into two rows: first row with 8 units, second row with 7 units
first_row_units = unit_counts.iloc[:8]  # First 8 units
second_row_units = unit_counts.iloc[8:]  # Remaining 7 units

# Title
st.title("Unit Summary")
st.subheader("Percentage of Unit in KG")

st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

# First Row: Create 8 columns for the first row of units
cols_first_row = st.columns(8)

# Display the first row of unit percentage summary
for i, row in first_row_units.iterrows():
    with cols_first_row[i]:
        st.markdown(f"""
        <div style='text-align: center'>
            <h5>{row['unit']}</h5>
            <h2><strong>{row['Percentage']}%</strong></h2>
        </div>
        """, unsafe_allow_html=True)

# Second Row: Create 7 columns for the second row of units
cols_second_row = st.columns(7)

# Display the second row of unit percentage summary
for i, row in enumerate(second_row_units.iterrows()):
    with cols_second_row[i]:
        st.markdown(f"""
        <div style='text-align: center'>
            <h5>{row[1]['unit']}</h5>
            <h2><strong>{row[1]['Percentage']}%</strong></h2>
        </div>
        """, unsafe_allow_html=True)

# Add a horizontal rule to divide the charts
st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

# Create a bar chart for Unit vs Frequency using Altair, sorted by frequency in descending order
bar_chart = alt.Chart(unit_counts).mark_bar().encode(
    x=alt.X('unit:N', title='Unit', sort='-y'),  # Sort by frequency (Count) in descending order
    y=alt.Y('Count:Q', title='Frequency'),
    color=alt.Color('unit:N', scale=alt.Scale(domain=list(color_map.keys()), range=list(color_map.values())), legend=None)
).properties(
    title='Unit Distribution (Bar Chart)',
    width=800,
    height=400
)

# Display the bar chart in Streamlit
st.altair_chart(bar_chart, use_container_width=True)

# Create a pie chart for Unit vs Frequency using Plotly with the same color scheme
pie_chart = px.pie(
    unit_counts, 
    names='unit', 
    values='Count', 
    title='Unit Distribution (Pie Chart)',
    color='unit',  # Apply consistent colors
    color_discrete_map=color_map,  # Use the same color map for the pie chart
    hole=0.4  # This makes it a donut chart; remove if you want a full pie chart
)

# Display the pie chart in Streamlit
st.plotly_chart(pie_chart, use_container_width=True)