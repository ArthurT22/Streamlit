import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

st.set_page_config(page_title="DEI Arthur", page_icon=":bar_chart:", layout="wide")

from streamlit_gsheets import GSheetsConnection

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read()

# Sidebar Widgets
st.sidebar.header('Filters')
st.sidebar.write("Use these options to filter the data")

# Multiselect widget for filtering pages
pages = ['Gender', 'Generation', 'Religion', 'Unit']
selected_pages = st.sidebar.multiselect("Choose the summary you want to display:", pages, default=pages)

# Title
if 'Gender' in selected_pages:
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

if 'Generation' in selected_pages:
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

if 'Religion' in selected_pages:
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

if 'Unit' in selected_pages:
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