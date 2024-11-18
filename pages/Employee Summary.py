import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Summary", page_icon=":bar_chart:", layout="wide")

# Example data: Replace this with your actual data
from streamlit_gsheets import GSheetsConnection

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read()

# Replace NaN values in the 'layer' column with "N-A"
df['layer'] = df['layer'].fillna("N-A")

# Page Title
st.title("Employee Summary")

# Display total employee count
total_employees = len(df)
st.markdown(f"<h1 style='text-align: center;'>Total Employees: {total_employees}</h1>", unsafe_allow_html=True)

# Divider line
st.markdown("<hr style='border:1px solid black'>", unsafe_allow_html=True)

# Select Box for Summary Breakdown
st.header("Summary Breakdown")
breakdown_options = ['unit', 'subunit', 'layer']
selected_breakdown = st.selectbox("Choose a Breakdown Variable:", breakdown_options)

# Create Summary and Bar Chart based on Selection
if selected_breakdown in df.columns:
    # Group by the selected breakdown and count
    breakdown_summary = df[selected_breakdown].value_counts().reset_index()
    breakdown_summary.columns = [selected_breakdown.capitalize(), 'Count']

    # Display the summary as a table
    st.dataframe(breakdown_summary)

    # Create a bar chart
    bar_chart = alt.Chart(breakdown_summary).mark_bar().encode(
        x=alt.X('Count:Q', title='Count'),
        y=alt.Y(f'{selected_breakdown.capitalize()}:N', title=selected_breakdown.capitalize(), sort='-x'),
        tooltip=[alt.Tooltip(f'{selected_breakdown.capitalize()}:N', title=selected_breakdown.capitalize()),
                 alt.Tooltip('Count:Q', title='Count')]
    ).properties(
        title=f'Employee Distribution by {selected_breakdown.capitalize()}',
        width=700,
        height=400
    )

    # Display the bar chart
    st.altair_chart(bar_chart, use_container_width=True)
else:
    st.warning(f"'{selected_breakdown}' is not available in the dataset.")

# Divider line
st.markdown("<hr style='border:1px solid black'>", unsafe_allow_html=True)

# Add other summary sections or features below if needed