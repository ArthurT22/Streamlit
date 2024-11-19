import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="KG DEI Dashboard", page_icon=":bar_chart:", layout="wide")

from streamlit_gsheets import GSheetsConnection

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read()

# Replace NaN values in the 'layer' column with "N-A" for display and filtering purposes
df['layer'] = df['layer'].fillna("N-A")

st.sidebar.header('KG DEI Dashboard')
st.sidebar.header('Metrics')

# Metrics Selection with a blank option
metrics_options = [''] + ['Gender', 'Generation', 'Religion', 'Tenure']
selected_metrics = st.sidebar.selectbox("Choose Metrics to Display:", metrics_options)

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

# Filter the data based on selected filters
filtered_df = df.copy()

if selected_units:
    filtered_df = filtered_df[filtered_df['unit'].isin(selected_units)]

if selected_subunits:
    filtered_df = filtered_df[filtered_df['subunit'].isin(selected_subunits)]

if selected_layers:
    if "N-A" in selected_layers:
        filtered_df = filtered_df[filtered_df['layer'].isin(selected_layers) | (filtered_df['layer'] == "N-A")]
    else:
        filtered_df = filtered_df[filtered_df['layer'].isin(selected_layers)]

if selected_genders:
    filtered_df = filtered_df[filtered_df['gender'].isin(selected_genders)]

if selected_generations:
    filtered_df = filtered_df[filtered_df['generation'].isin(selected_generations)]

if selected_religions:
    filtered_df = filtered_df[filtered_df['Religious Denomination Key'].isin(selected_religions)]

# For tenure, categorize 'Years' column and filter based on selected tenure groups
bins = [-1, 1, 3, 6, 10, 15, 20, 25, float('inf')]
labels = ['<1 Year', '1-3 Year', '4-6 Year', '6-10 Year', '11-15 Year', '16-20 Year', '20-25 Year', '>25 Year']
filtered_df['Service_Group'] = pd.cut(filtered_df['Years'], bins=bins, labels=labels, right=False)

if selected_tenures:
    filtered_df = filtered_df[filtered_df['Service_Group'].isin(selected_tenures)]

# Function to display total employees
def display_total_employees():
    total_employees = len(filtered_df)
    title_text = "Total Employees (All Data)" if not selected_units and not selected_subunits and not selected_layers else f"Total Employees (Filtered Data)"
    st.title(title_text)
    st.subheader(f"{total_employees} Employees")
    st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

# Function to display gender summary
def display_gender_summary():
    # Replace missing values in 'layer' column with "N-A"
    df['layer'] = df['layer'].fillna("N-A")
    filtered_df['layer'] = filtered_df['layer'].fillna("N-A")

    # Select the correct DataFrame based on filters
    display_df = filtered_df.copy()

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

    # Combine count and percentage data
    gender_combined = gender_percentage.melt(id_vars=[selected_breakdown], value_vars=['Male', 'Female'],
                                             var_name='Gender', value_name='Percentage')
    gender_combined = gender_combined.merge(
        gender_counts.reset_index().melt(id_vars=[selected_breakdown], value_vars=['Male', 'Female'],
                                         var_name='Gender', value_name='Count'),
        on=[selected_breakdown, 'Gender']
    )
    gender_combined['Label'] = gender_combined.apply(
        lambda row: f"{int(row['Count'])} ({row['Percentage']:.1f}%)", axis=1
    )

    # Display title with filter details
    title_text = "Gender Metrics (All Units)" if not selected_units and not selected_subunits and not selected_layers else f"Gender Metrics (Filtered by {', '.join(selected_units)}, {', '.join(selected_subunits)}, {', '.join(selected_layers)})"
    st.title(title_text)
    st.subheader(f"Percentage of Gender by {selected_breakdown}")

    st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

    # Display total counts and percentages
    total_male = gender_counts['Male'].sum()
    total_female = gender_counts['Female'].sum()
    total_people = total_male + total_female
    male_percentage = (total_male / total_people * 100).round(2) if total_people > 0 else 0
    female_percentage = (total_female / total_people * 100).round(2) if total_people > 0 else 0

    col1, col2 = st.columns(2)
    col1.markdown(f"<div style='text-align: center'><h5>Male</h5><h1><strong>{male_percentage}%</strong></h1><p>{int(total_male)}</p></div>", unsafe_allow_html=True)
    col2.markdown(f"<div style='text-align: center'><h5>Female</h5><h1><strong>{female_percentage}%</strong></h1><p>{int(total_female)}</p></div>", unsafe_allow_html=True)

    st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

    # Plotly stacked bar chart
    fig = px.bar(
        gender_combined,
        x="Percentage",
        y=selected_breakdown,
        color="Gender",
        orientation="h",
        text="Label",
        color_discrete_map={'Male': '#90d5ff', 'Female': '#ffb5c0'},
        labels={
            "Percentage": "Percentage (%)",
            selected_breakdown: selected_breakdown.capitalize(),
            "Gender": "Gender"
        },
    )

    # Update layout to improve readability
    fig.update_traces(textposition="inside", insidetextanchor="middle")
    fig.update_layout(
        title=f"Gender Distribution by {selected_breakdown}",
        xaxis_title="Percentage (%)",
        yaxis_title=selected_breakdown.capitalize(),
        bargap=0.2,
        height=600,
        width=800,
        legend_title="Gender"
    )

    # Display the Plotly chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Function to display generation summary
def display_generation_summary():
    # Generation Distribution Logic (kept same as before)
    generation_counts = filtered_df.groupby(['unit', 'generation']).size().unstack().fillna(0)

    # Ensure all generations exist
    for generation in ['Boomers', 'Gen X', 'Gen Y', 'Gen Z', 'Post War']:
        if generation not in generation_counts.columns:
            generation_counts[generation] = 0

    generation_percentage = generation_counts.div(generation_counts.sum(axis=1), axis=0) * 100

    # Create Plotly Bar Chart
    fig = px.bar(
        generation_percentage.reset_index().melt(id_vars='unit', var_name='Generation', value_name='Percentage'),
        x='Percentage',
        y='unit',
        color='Generation',
        text='Percentage',
        orientation='h',
        title="Generation Distribution by Unit",
    )
    st.plotly_chart(fig, use_container_width=True)

# Main logic to display the selected page's content
if selected_page == 'Blank':
    display_total_employees()
elif selected_page == 'Gender':
    display_gender_summary()
elif selected_page == 'Generation':
    display_generation_summary()
elif selected_page == 'Religion':
    display_religion_summary()
elif selected_page == 'Tenure':
    display_tenure_summary()
