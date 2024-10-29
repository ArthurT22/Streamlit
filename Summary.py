import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

st.set_page_config(page_title="KG DEI", page_icon=":bar_chart:", layout="wide")

from streamlit_gsheets import GSheetsConnection

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read()

# Replace NaN values in the 'layer' column with "N-A" for display and filtering purposes
df['layer'] = df['layer'].fillna("N-A")

st.sidebar.header('KG DEI Dashboard')
st.sidebar.header('Metrics')

# Page selection
pages = ['Gender', 'Generation', 'Religion', 'Tenure']
selected_page = st.sidebar.selectbox("Choose the Metrics you want to display:", pages)

# Sidebar Widgets
st.sidebar.header('Filters')

# Unit, Subunit, and Layer Filters using multiselect without "All" option
unit_options = df['unit'].unique().tolist()
subunit_options = df['subunit'].unique().tolist() if 'subunit' in df.columns else []
layer_options = df['layer'].unique().tolist() if 'layer' in df.columns else []

# Multiselect filters for Unit, Subunit, and Layer
selected_units = st.sidebar.multiselect("Select Unit(s)", unit_options)
selected_subunits = st.sidebar.multiselect("Select Subunit(s)", subunit_options)
selected_layers = st.sidebar.multiselect("Select Layer(s)", layer_options)

# Additional Filters for Gender, Generation, Religion, and Tenure
gender_options = df['gender'].unique().tolist() if 'gender' in df.columns else []
generation_options = df['generation'].unique().tolist() if 'generation' in df.columns else []
religion_options = df['Religious Denomination Key'].unique().tolist() if 'Religious Denomination Key' in df.columns else []
tenure_options = ['<1 Year', '1-3 Year', '4-6 Year', '6-10 Year', '11-15 Year', '16-20 Year', '20-25 Year', '>25 Year']

# Multiselect filters for Gender, Generation, Religion, and Tenure
selected_genders = st.sidebar.multiselect("Select Gender(s)", gender_options)
selected_generations = st.sidebar.multiselect("Select Generation(s)", generation_options)
selected_religions = st.sidebar.multiselect("Select Religion(s)", religion_options)
selected_tenures = st.sidebar.multiselect("Select Tenure(s)", tenure_options)

st.sidebar.header('Breakdown Variable')

# Add Breakdown Variable Selection
breakdown_options = ['unit', 'subunit', 'layer']
selected_breakdown = st.sidebar.selectbox("Breakdown Variable", breakdown_options)

# Filter the data based on selected units, subunits, layers, and additional criteria
filtered_df = df.copy()

# Apply filters only if specific options are selected; otherwise, keep the full dataset
if selected_units:
    filtered_df = filtered_df[filtered_df['unit'].isin(selected_units)]

if selected_subunits and 'subunit' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['subunit'].isin(selected_subunits)]

# Adjust filter logic for 'layer' to include "N-A" option for missing data
if selected_layers and 'layer' in filtered_df.columns:
    if "N-A" in selected_layers:
        filtered_df = filtered_df[filtered_df['layer'].isin(selected_layers) | (filtered_df['layer'] == "N-A")]
    else:
        filtered_df = filtered_df[filtered_df['layer'].isin(selected_layers)]

# Filter for Gender, Generation, Religion, and Tenure
if selected_genders and 'gender' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['gender'].isin(selected_genders)]

if selected_generations and 'generation' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['generation'].isin(selected_generations)]

if selected_religions and 'Religious Denomination Key' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['Religious Denomination Key'].isin(selected_religions)]

# For tenure, categorize 'Years' column and filter based on selected tenure groups
bins = [-1, 1, 3, 6, 10, 15, 20, 25, float('inf')]
labels = ['<1 Year', '1-3 Year', '4-6 Year', '6-10 Year', '11-15 Year', '16-20 Year', '20-25 Year', '>25 Year']
filtered_df['Service_Group'] = pd.cut(filtered_df['Years'], bins=bins, labels=labels, right=False)

if selected_tenures:
    filtered_df = filtered_df[filtered_df['Service_Group'].isin(selected_tenures)]

# Function to display gender summary
def display_gender_summary():
    # Replace missing values in 'layer' column with "N-A"
    df['layer'] = df['layer'].fillna("N-A")
    filtered_df['layer'] = filtered_df['layer'].fillna("N-A")

    # Choose the correct DataFrame based on filters
    display_df = df if 'All' in selected_units and 'All' in selected_subunits and 'All' in selected_layers else filtered_df
    
    # Group by the selected breakdown variable and calculate gender distribution
    gender_counts = display_df.groupby([selected_breakdown, 'gender']).size().unstack().fillna(0)

    # Ensure that 'Male' and 'Female' exist in the groupby result
    if 'Male' not in gender_counts.columns:
        gender_counts['Male'] = 0
    if 'Female' not in gender_counts.columns:
        gender_counts['Female'] = 0

    # Calculate percentages for each gender
    gender_percentage = gender_counts.div(gender_counts.sum(axis=1), axis=0) * 100
    gender_percentage = gender_percentage.reset_index()

    # Define color scheme for gender
    color_map = {'Male': '#90d5ff', 'Female': '#ffb5c0'}
    
    # Combine count and percentage data for tooltips
    gender_combined = gender_percentage.melt(id_vars=[selected_breakdown], value_vars=['Male', 'Female'],
                                             var_name='Gender', value_name='Percentage')

    gender_combined = gender_combined.merge(
        gender_counts.reset_index().melt(id_vars=[selected_breakdown], value_vars=['Male', 'Female'],
                                         var_name='Gender', value_name='Count'),
        on=[selected_breakdown, 'Gender']
    )

    # Display title with filter details
    title_text = "Gender Metrics (All Units)" if 'All' in selected_units and 'All' in selected_subunits and 'All' in selected_layers else f"Gender Metrics (Filtered by {', '.join(selected_units)}, {', '.join(selected_subunits)}, {', '.join(selected_layers)})"
    st.title(title_text)
    st.subheader(f"Percentage of Gender by {selected_breakdown}")

    st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

    # Display male and female percentages and counts
    total_male = gender_counts['Male'].sum()
    total_female = gender_counts['Female'].sum()
    total_people = total_male + total_female
    male_percentage = (total_male / total_people * 100).round(2) if total_people > 0 else 0
    female_percentage = (total_female / total_people * 100).round(2) if total_people > 0 else 0

    col1, col2 = st.columns(2)
    col1.markdown(f"<div style='text-align: center'><h5>Male</h5><h1><strong>{male_percentage}%</strong></h1><p>{int(total_male)}</p></div>", unsafe_allow_html=True)
    col2.markdown(f"<div style='text-align: center'><h5>Female</h5><h1><strong>{female_percentage}%</strong></h1><p>{int(total_female)}</p></div>", unsafe_allow_html=True)
    
    st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

    # Custom order for layer breakdown, including "N-A"
    if selected_breakdown == 'layer':
        custom_layer_order = [
            "Group 5 STR Layer 1", "Group 4 STR Layer 2", "Group 3 STR Layer 3A",
            "Group 3 STR Layer 3B", "Group 2 STR Layer 4", "Group 1 STR Layer 5",
            "Group 5", "Group 4", "Group 3", "Group 2", "Group 1", "N-A"
        ]
        y_encoding = alt.Y(f'{selected_breakdown}:N', title=selected_breakdown, sort=custom_layer_order)
    else:
        y_encoding = alt.Y(f'{selected_breakdown}:N', title=selected_breakdown)

    # Horizontal stacked percentage bar chart for Gender Distribution by Breakdown Variable
    bar_chart = alt.Chart(gender_combined).mark_bar().encode(
        x=alt.X('Percentage:Q', title='Percentage', scale=alt.Scale(domain=[0, 100])),
        y=y_encoding,
        color=alt.Color('Gender:N', scale=alt.Scale(domain=list(color_map.keys()), range=list(color_map.values()))),
        tooltip=[alt.Tooltip(f'{selected_breakdown}:N'), alt.Tooltip('Percentage:Q', format='.2f'),
                 alt.Tooltip('Count:Q', title='Count'), 'Gender:N']
    ).properties(
        title=f'Gender Distribution by {selected_breakdown} (Stacked Bar Chart)',
        width=700,
        height=400
    )

    # Display the bar chart in Streamlit
    st.altair_chart(bar_chart, use_container_width=True)

# Function to display generation summary
def display_generation_summary():
    # Replace missing values in 'layer' column with "N-A"
    df['layer'] = df['layer'].fillna("N-A")
    filtered_df['layer'] = filtered_df['layer'].fillna("N-A")

    # Choose the correct DataFrame based on filters
    display_df = df if 'All' in selected_units and 'All' in selected_subunits and 'All' in selected_layers else filtered_df
    
    # Group by the selected breakdown and calculate generation distribution
    generation_counts = display_df.groupby([selected_breakdown, 'generation']).size().unstack().fillna(0)

    # Define color map for generations
    color_map = {
        'Boomers': '#1f77b4',  # Blue
        'Gen X': '#ff7f0e',    # Orange
        'Gen Y': '#2ca02c',    # Green
        'Gen Z': '#d62728',    # Red
        'Post War': '#9467bd'  # Purple
    }

    # Ensure all generations are represented in data
    for generation in color_map.keys():
        if generation not in generation_counts.columns:
            generation_counts[generation] = 0

    # Calculate percentages for each generation
    generation_percentage = generation_counts.div(generation_counts.sum(axis=1), axis=0) * 100
    generation_percentage = generation_percentage.reset_index()

    # Combine count and percentage data for tooltips
    generation_combined = generation_percentage.melt(id_vars=[selected_breakdown], value_vars=list(color_map.keys()),
                                                     var_name='Generation', value_name='Percentage')
    generation_combined = generation_combined.merge(
        generation_counts.reset_index().melt(id_vars=[selected_breakdown], value_vars=list(color_map.keys()),
                                             var_name='Generation', value_name='Count'),
        on=[selected_breakdown, 'Generation']
    )

    # Display title with filter details
    title_text = "Generation Metrics (All Units)" if 'All' in selected_units and 'All' in selected_subunits and 'All' in selected_layers else f"Generation Metrics (Filtered by {', '.join(selected_units)}, {', '.join(selected_subunits)}, {', '.join(selected_layers)})"
    st.title(title_text)
    st.subheader(f"Percentage of Generation by {selected_breakdown}")

    st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

    # Display total counts and percentages with birth year ranges
    total_counts = generation_counts.sum().sum()
    total_percentage = {gen: (generation_counts[gen].sum() / total_counts * 100).round(2) if total_counts > 0 else 0 for gen in color_map.keys()}

    # Define birth year ranges for each generation
    birth_year_ranges = {
        'Post War': '(1928-1945)',
        'Boomers': '(1946-1964)',
        'Gen X': '(1965-1980)',
        'Gen Y': '(1981-1996)',
        'Gen Z': '(1997-2012)'
    }

    # Display generation information with birth years
    cols = st.columns(len(color_map.keys()))
    for i, (gen, color) in enumerate(color_map.items()):
        birth_year_range = birth_year_ranges.get(gen, "")
        cols[i].markdown(f"""
            <div style='text-align: center'>
                <h5 style="margin-bottom: 0;">{gen}</h5>
                <h5 style='margin-top: 0; margin-bottom: 0;'>{birth_year_range}</h5>
                <h1><strong>{total_percentage[gen]}%</strong></h1>
                <p>{int(generation_counts[gen].sum())}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

    # Custom order for layer breakdown, including "N-A"
    if selected_breakdown == 'layer':
        custom_layer_order = [
            "Group 5 STR Layer 1", "Group 4 STR Layer 2", "Group 3 STR Layer 3A",
            "Group 3 STR Layer 3B", "Group 2 STR Layer 4", "Group 1 STR Layer 5",
            "Group 5", "Group 4", "Group 3", "Group 2", "Group 1", "N-A"
        ]
        y_encoding = alt.Y(f'{selected_breakdown}:N', title=selected_breakdown, sort=custom_layer_order)
    else:
        y_encoding = alt.Y(f'{selected_breakdown}:N', title=selected_breakdown)

    # Horizontal stacked percentage bar chart for Generation Distribution by Breakdown Variable
    bar_chart = alt.Chart(generation_combined).mark_bar().encode(
        x=alt.X('Percentage:Q', title='Percentage', scale=alt.Scale(domain=[0, 100])),
        y=y_encoding,
        color=alt.Color('Generation:N', scale=alt.Scale(domain=list(color_map.keys()), range=list(color_map.values()))),
        tooltip=[alt.Tooltip(f'{selected_breakdown}:N'), alt.Tooltip('Percentage:Q', format='.2f'),
                 alt.Tooltip('Count:Q', title='Count'), 'Generation:N']
    ).properties(
        title=f'Generation Distribution by {selected_breakdown} (Stacked Bar Chart)',
        width=700,
        height=400
    )

    # Display the bar chart in Streamlit (Bottom Part)
    st.altair_chart(bar_chart, use_container_width=True)

# Function to display religion summary
def display_religion_summary():
    # Replace missing values in 'layer' column with "N-A"
    df['layer'] = df['layer'].fillna("N-A")
    filtered_df['layer'] = filtered_df['layer'].fillna("N-A")

    # Choose the correct DataFrame based on filters
    display_df = df if 'All' in selected_units and 'All' in selected_subunits and 'All' in selected_layers else filtered_df

    # Calculate religion distribution by selected breakdown
    religion_counts = display_df.groupby([selected_breakdown, 'Religious Denomination Key']).size().unstack().fillna(0)

    # Define color map for religions
    color_map = {
        'Islam': '#1f77b4', 'Kristen': '#ff7f0e', 'Katholik': '#2ca02c', 'Hindu': '#d62728', 
        'Buddha': '#9467bd', 'Kepercayaan': '#8c564b', 'Kong Hu Cu': '#e377c2'
    }

    # Ensure all religions are present in the data
    for religion in color_map.keys():
        if religion not in religion_counts.columns:
            religion_counts[religion] = 0

    # Calculate religion percentages
    religion_percentage = religion_counts.div(religion_counts.sum(axis=1), axis=0) * 100
    religion_percentage = religion_percentage.reset_index()

    # Combine count and percentage data for tooltips
    religion_combined = religion_percentage.melt(id_vars=[selected_breakdown], value_vars=list(color_map.keys()),
                                                 var_name='Religion', value_name='Percentage')
    religion_combined = religion_combined.merge(
        religion_counts.reset_index().melt(id_vars=[selected_breakdown], value_vars=list(color_map.keys()),
                                           var_name='Religion', value_name='Count'),
        on=[selected_breakdown, 'Religion']
    )

    # Display title with filter details
    title_text = "Religion Metrics (All Units)" if 'All' in selected_units and 'All' in selected_subunits and 'All' in selected_layers else f"Religion Metrics (Filtered by {', '.join(selected_units)}, {', '.join(selected_subunits)}, {', '.join(selected_layers)})"
    st.title(title_text)
    st.subheader(f"Percentage of Religion by {selected_breakdown}")

    st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

    # Display total counts and percentages
    total_counts = religion_counts.sum().sum()
    total_percentage = {rel: (religion_counts[rel].sum() / total_counts * 100).round(2) if total_counts > 0 else 0 for rel in color_map.keys()}

    # Display religion summary with percentages and counts
    cols = st.columns(len(color_map.keys()))
    for i, (rel, color) in enumerate(color_map.items()):
        cols[i].markdown(f"<div style='text-align: center'><h5>{rel}</h5><h2><strong>{total_percentage[rel]}%</strong></h2><p>{int(religion_counts[rel].sum())}</p></div>", unsafe_allow_html=True)

    st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

    # Custom order for layer breakdown, including "N-A"
    if selected_breakdown == 'layer':
        custom_layer_order = [
            "Group 5 STR Layer 1", "Group 4 STR Layer 2", "Group 3 STR Layer 3A",
            "Group 3 STR Layer 3B", "Group 2 STR Layer 4", "Group 1 STR Layer 5",
            "Group 5", "Group 4", "Group 3", "Group 2", "Group 1", "N-A"
        ]
        y_encoding = alt.Y(f'{selected_breakdown}:N', title=selected_breakdown, sort=custom_layer_order)
    else:
        y_encoding = alt.Y(f'{selected_breakdown}:N', title=selected_breakdown)

    # Horizontal stacked percentage bar chart for Religion Distribution by Breakdown Variable
    bar_chart = alt.Chart(religion_combined).mark_bar().encode(
        x=alt.X('Percentage:Q', title='Percentage', scale=alt.Scale(domain=[0, 100])),
        y=y_encoding,
        color=alt.Color('Religion:N', scale=alt.Scale(domain=list(color_map.keys()), range=list(color_map.values()))),
        tooltip=[alt.Tooltip(f'{selected_breakdown}:N'), alt.Tooltip('Percentage:Q', format='.2f'),
                 alt.Tooltip('Count:Q', title='Count'), 'Religion:N']
    ).properties(
        title=f'Religion Distribution by {selected_breakdown} (Stacked Bar Chart)',
        width=700,
        height=400
    )

    # Display the bar chart in Streamlit
    st.altair_chart(bar_chart, use_container_width=True)

# Function to display tenure summary
def display_tenure_summary():
    # Replace missing values in 'layer' column with "N-A"
    df['layer'] = df['layer'].fillna("N-A")
    filtered_df['layer'] = filtered_df['layer'].fillna("N-A")

    # Select the correct DataFrame based on filters
    display_df = df if 'All' in selected_units and 'All' in selected_subunits and 'All' in selected_layers else filtered_df

    # Define tenure groups and categorize them
    bins = [-1, 1, 3, 6, 10, 15, 20, 25, float('inf')]
    labels = ['<1 Year', '1-3 Year', '4-6 Year', '6-10 Year', '11-15 Year', '16-20 Year', '20-25 Year', '>25 Year']
    display_df['Service_Group'] = pd.cut(display_df['Years'], bins=bins, labels=labels, right=False)

    # Calculate tenure distribution by selected breakdown
    tenure_counts = display_df.groupby([selected_breakdown, 'Service_Group']).size().unstack().fillna(0)

    # Define color map for tenure groups
    color_map = {
        '<1 Year': '#1f77b4', '1-3 Year': '#ff7f0e', '4-6 Year': '#2ca02c', '6-10 Year': '#d62728',
        '11-15 Year': '#9467bd', '16-20 Year': '#8c564b', '20-25 Year': '#e377c2', '>25 Year': '#7f7f7f'
    }

    # Ensure all tenure groups are present in the data
    for tenure_group in color_map.keys():
        if tenure_group not in tenure_counts.columns:
            tenure_counts[tenure_group] = 0

    # Calculate tenure percentages
    tenure_percentage = tenure_counts.div(tenure_counts.sum(axis=1), axis=0) * 100
    tenure_percentage = tenure_percentage.reset_index()

    # Combine count and percentage data for tooltips
    tenure_combined = tenure_percentage.melt(id_vars=[selected_breakdown], value_vars=list(color_map.keys()),
                                             var_name='Tenure Group', value_name='Percentage')
    tenure_combined = tenure_combined.merge(
        tenure_counts.reset_index().melt(id_vars=[selected_breakdown], value_vars=list(color_map.keys()),
                                         var_name='Tenure Group', value_name='Count'),
        on=[selected_breakdown, 'Tenure Group']
    )

    # Display title with filter details
    title_text = "Tenure Metrics (All Units)" if 'All' in selected_units and 'All' in selected_subunits and 'All' in selected_layers else f"Tenure Metrics (Filtered by {', '.join(selected_units)}, {', '.join(selected_subunits)}, {', '.join(selected_layers)})"
    st.title(title_text)
    st.subheader(f"Percentage of Tenure by {selected_breakdown}")

    st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

    # Display total counts and percentages
    total_counts = tenure_counts.sum().sum()
    total_percentage = {tenure: (tenure_counts[tenure].sum() / total_counts * 100).round(2) if total_counts > 0 else 0 for tenure in color_map.keys()}

    cols = st.columns(len(color_map.keys()))
    for i, (tenure, color) in enumerate(color_map.items()):
        cols[i].markdown(f"<div style='text-align: center'><h5>{tenure}</h5><h2><strong>{total_percentage[tenure]}%</strong></h2><p>{int(tenure_counts[tenure].sum())}</p></div>", unsafe_allow_html=True)

    st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

    # Custom order for layer breakdown, including "N-A"
    if selected_breakdown == 'layer':
        custom_layer_order = [
            "Group 5 STR Layer 1", "Group 4 STR Layer 2", "Group 3 STR Layer 3A",
            "Group 3 STR Layer 3B", "Group 2 STR Layer 4", "Group 1 STR Layer 5",
            "Group 5", "Group 4", "Group 3", "Group 2", "Group 1", "N-A"
        ]
        y_encoding = alt.Y(f'{selected_breakdown}:N', title=selected_breakdown, sort=custom_layer_order)
    else:
        y_encoding = alt.Y(f'{selected_breakdown}:N', title=selected_breakdown)

    # Horizontal stacked percentage bar chart for Tenure Distribution by Breakdown Variable
    bar_chart = alt.Chart(tenure_combined).mark_bar().encode(
        x=alt.X('Percentage:Q', title='Percentage', scale=alt.Scale(domain=[0, 100])),
        y=y_encoding,
        color=alt.Color('Tenure Group:N', scale=alt.Scale(domain=list(color_map.keys()), range=list(color_map.values()))),
        tooltip=[alt.Tooltip(f'{selected_breakdown}:N'), alt.Tooltip('Percentage:Q', format='.2f'),
                 alt.Tooltip('Count:Q', title='Count'), 'Tenure Group:N']
    ).properties(
        title=f'Tenure Distribution by {selected_breakdown} (Stacked Bar Chart)',
        width=700,
        height=400
    )

    # Display the bar chart in Streamlit
    st.altair_chart(bar_chart, use_container_width=True)



# Display the selected page's summary
if selected_page == 'Gender':
    display_gender_summary()
elif selected_page == 'Generation':
    display_generation_summary()
elif selected_page == 'Religion':
    display_religion_summary()
elif selected_page == 'Tenure':
    display_tenure_summary()