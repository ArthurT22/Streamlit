import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

st.set_page_config(page_title="DEI Arthur", page_icon=":bar_chart:", layout="wide")

from streamlit_gsheets import GSheetsConnection

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read()

st.sidebar.header('Summary')

# Page selection
pages = ['Select an option...', 'Gender', 'Generation', 'Religion', 'Tenure']
selected_page = st.sidebar.selectbox("Choose the summary you want to display:", pages)

# Sidebar Widgets
st.sidebar.header('Filters')

# Unit, Subunit, and Layer Filters
unit_options = ['All'] + df['unit'].unique().tolist()
subunit_options = ['All'] + df['subunit'].unique().tolist() if 'subunit' in df.columns else []
layer_options = ['All'] + df['layer'].unique().tolist() if 'layer' in df.columns else []

selected_unit = st.sidebar.selectbox("Select Unit", unit_options)
selected_subunit = st.sidebar.selectbox("Select Subunit", subunit_options)
selected_layer = st.sidebar.selectbox("Select Layer", layer_options)

st.sidebar.header('Breakdown Variable')

# Add Breakdown Variable Selection
breakdown_options = ['unit', 'subunit', 'layer']
selected_breakdown = st.sidebar.selectbox("Breakdown Variable", breakdown_options)

# Filter the data based on selected unit, subunit, and layer
filtered_df = df.copy()

if selected_unit != 'All':
    filtered_df = filtered_df[filtered_df['unit'] == selected_unit]

if selected_subunit != 'All' and 'subunit' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['subunit'] == selected_subunit]

if selected_layer != 'All' and 'layer' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['layer'] == selected_layer]

# Ensure that an option is selected before displaying content
if selected_page != 'Select an option...':
    # Gender Summary
    if selected_page == 'Gender':
        # If all filters are set to "All", use the entire dataset, else use the filtered data
        if selected_unit == 'All' and selected_subunit == 'All' and selected_layer == 'All':
            display_df = df  # Use entire dataset
        else:
            display_df = filtered_df  # Use filtered dataset
        
        # Group by the selected breakdown variable and calculate gender distribution
        gender_counts = display_df.groupby([selected_breakdown, 'gender']).size().unstack().fillna(0)

        # Error handling: Check if 'Male' and 'Female' exist in the groupby result
        if 'Male' not in gender_counts.columns:
            gender_counts['Male'] = 0
        if 'Female' not in gender_counts.columns:
            gender_counts['Female'] = 0

        # Calculate percentages for each group
        gender_percentage = gender_counts.div(gender_counts.sum(axis=1), axis=0) * 100
        gender_percentage = gender_percentage.reset_index()

        # Define a consistent color scheme for genders
        color_map = {
            'Male': '#90d5ff',       # Blue
            'Female': '#ffb5c0',     # Orange
        }

        # Combine count and percentage data for tooltips by melting the data
        gender_combined = gender_percentage.melt(id_vars=[selected_breakdown], value_vars=['Male', 'Female'],
                                                 var_name='Gender', value_name='Percentage')

        # Merge with the original count data to get the counts for each gender and breakdown group
        gender_combined = gender_combined.merge(
            gender_counts.reset_index().melt(id_vars=[selected_breakdown], value_vars=['Male', 'Female'],
                                             var_name='Gender', value_name='Count'),
            on=[selected_breakdown, 'Gender']
        )

        # Display Title
        if selected_unit == 'All' and selected_subunit == 'All' and selected_layer == 'All':
            title_text = "Gender Summary (All Units)"
        else:
            title_text = f"Gender Summary (Filtered by {selected_unit}, {selected_subunit}, {selected_layer})"

        st.title(title_text)
        st.subheader(f"Percentage of Gender by {selected_breakdown}")

        st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

        # Display male and female percentages and counts (Top Part)
        total_male = gender_counts['Male'].sum()
        total_female = gender_counts['Female'].sum()
        total_people = total_male + total_female
        male_percentage = (total_male / total_people * 100).round(2) if total_people > 0 else 0
        female_percentage = (total_female / total_people * 100).round(2) if total_people > 0 else 0

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            <div style='text-align: center'>
                <h5>Male</h5>
                <h1><strong>{male_percentage}%</strong></h1>
                <p>{int(total_male)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='text-align: center'>
                <h5>Female</h5>
                <h1><strong>{female_percentage}%</strong></h1>
                <p>{int(total_female)}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

        # Horizontal stacked percentage bar chart for Gender Distribution by Breakdown Variable
        bar_chart = alt.Chart(gender_combined).mark_bar().encode(
            x=alt.X('Percentage:Q', title='Percentage', scale=alt.Scale(domain=[0, 100])),  # x-axis is percentage (0-100%)
            y=alt.Y(f'{selected_breakdown}:N', title=selected_breakdown),  # Use the selected breakdown variable (Unit, Subunit, Layer)
            color=alt.Color('Gender:N', scale=alt.Scale(domain=list(color_map.keys()), range=list(color_map.values()))),
            tooltip=[alt.Tooltip(f'{selected_breakdown}:N'), alt.Tooltip('Percentage:Q', format='.2f'),
                     alt.Tooltip('Count:Q', title='Count'), 'Gender:N']
        ).properties(
            title=f'Gender Distribution by {selected_breakdown} (Stacked Bar Chart)',
            width=700,
            height=400
        )

        # Display the bar chart in Streamlit (Bottom Part)
        st.altair_chart(bar_chart, use_container_width=True)

    if selected_page == 'Generation':
        # If all filters are set to "All", use the entire dataset, else use the filtered data
        if selected_unit == 'All' and selected_subunit == 'All' and selected_layer == 'All':
            display_df = df  # Use entire dataset
        else:
            display_df = filtered_df  # Use filtered dataset

        # Group by the selected breakdown variable and calculate generation distribution
        generation_counts = display_df.groupby([selected_breakdown, 'generation']).size().unstack().fillna(0)

        # Define a consistent color scheme for generations
        color_map = {
            'Boomers': '#1f77b4',    # Blue
            'Gen X': '#ff7f0e',      # Orange
            'Gen Y': '#2ca02c',      # Green
            'Gen Z': '#d62728',      # Red
            'Post War': '#9467bd'    # Purple
        }

        # Ensure that all generations exist in the data; if not, add them with a count of 0
        for generation in color_map.keys():
            if generation not in generation_counts.columns:
                generation_counts[generation] = 0

        # Calculate percentages for each group
        generation_percentage = generation_counts.div(generation_counts.sum(axis=1), axis=0) * 100
        generation_percentage = generation_percentage.reset_index()

        # Combine count and percentage data for tooltips by melting the data
        generation_combined = generation_percentage.melt(id_vars=[selected_breakdown], value_vars=list(color_map.keys()),
                                                         var_name='Generation', value_name='Percentage')

        # Merge with the original count data to get the counts for each generation and breakdown group
        generation_combined = generation_combined.merge(
            generation_counts.reset_index().melt(id_vars=[selected_breakdown], value_vars=list(color_map.keys()),
                                                 var_name='Generation', value_name='Count'),
            on=[selected_breakdown, 'Generation']
        )

        # Display Title
        if selected_unit == 'All' and selected_subunit == 'All' and selected_layer == 'All':
            title_text = "Generation Summary (All Units)"
        else:
            title_text = f"Generation Summary (Filtered by {selected_unit}, {selected_subunit}, {selected_layer})"

        st.title(title_text)
        st.subheader(f"Percentage of Generation by {selected_breakdown}")

        st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

        # Display generation percentages and counts (Top Part)
        total_counts = generation_counts.sum().sum()

        # Check if total_counts is 0 to avoid NaN values
        if total_counts == 0:
            # If total is zero, set all percentages to zero
            total_percentage = {generation: 0 for generation in color_map.keys()}
            generation_sums = {generation: 0 for generation in color_map.keys()}
        else:
            generation_sums = generation_counts.sum()
            total_percentage = (generation_sums / total_counts * 100).round(2)

        # Display generation percentage summary with counts
        col1, col2, col3, col4, col5 = st.columns(5)

        col1.markdown(f"<div style='text-align: center'><h5>Boomers</h5><h1><strong>{total_percentage['Boomers']}%</strong></h1><p>{int(generation_sums['Boomers'])}</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div style='text-align: center'><h5>Gen X</h5><h1><strong>{total_percentage['Gen X']}%</strong></h1><p>{int(generation_sums['Gen X'])}</p></div>", unsafe_allow_html=True)
        col3.markdown(f"<div style='text-align: center'><h5>Gen Y</h5><h1><strong>{total_percentage['Gen Y']}%</strong></h1><p>{int(generation_sums['Gen Y'])}</p></div>", unsafe_allow_html=True)
        col4.markdown(f"<div style='text-align: center'><h5>Gen Z</h5><h1><strong>{total_percentage['Gen Z']}%</strong></h1><p>{int(generation_sums['Gen Z'])}</p></div>", unsafe_allow_html=True)
        col5.markdown(f"<div style='text-align: center'><h5>Post War</h5><h1><strong>{total_percentage['Post War']}%</strong></h1><p>{int(generation_sums['Post War'])}</p></div>", unsafe_allow_html=True)

        st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

        # Horizontal stacked percentage bar chart for Generation Distribution by Breakdown Variable
        bar_chart = alt.Chart(generation_combined).mark_bar().encode(
            x=alt.X('Percentage:Q', title='Percentage', scale=alt.Scale(domain=[0, 100])),  # x-axis is percentage (0-100%)
            y=alt.Y(f'{selected_breakdown}:N', title=selected_breakdown),  # Use the selected breakdown variable (Unit, Subunit, Layer)
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

    if selected_page == 'Religion':
        # If all filters are set to "All", use the entire dataset, else use the filtered data
        if selected_unit == 'All' and selected_subunit == 'All' and selected_layer == 'All':
            display_df = df  # Use entire dataset
        else:
            display_df = filtered_df  # Use filtered dataset
        
        # Group by the selected breakdown variable and calculate religion distribution
        religion_counts = display_df.groupby([selected_breakdown, 'Religious Denomination Key']).size().unstack().fillna(0)

        # Define a consistent color scheme for religions
        color_map = {
            'Islam': '#1f77b4',        # Blue
            'Kristen': '#ff7f0e',      # Orange
            'Katholik': '#2ca02c',     # Green
            'Hindu': '#d62728',        # Red
            'Buddha': '#9467bd',       # Purple
            'Kepercayaan': '#8c564b',  # Brown
            'Kong Hu Cu': '#e377c2'    # Pink
        }

        # Ensure that all religions exist in the data; if not, add them with a count of 0
        for religion in color_map.keys():
            if religion not in religion_counts.columns:
                religion_counts[religion] = 0

        # Calculate percentages for each group
        religion_percentage = religion_counts.div(religion_counts.sum(axis=1), axis=0) * 100
        religion_percentage = religion_percentage.reset_index()

        # Combine count and percentage data for tooltips by melting the data
        religion_combined = religion_percentage.melt(id_vars=[selected_breakdown], value_vars=list(color_map.keys()),
                                                     var_name='Religion', value_name='Percentage')

        # Merge with the original count data to get the counts for each religion and breakdown group
        religion_combined = religion_combined.merge(
            religion_counts.reset_index().melt(id_vars=[selected_breakdown], value_vars=list(color_map.keys()),
                                               var_name='Religion', value_name='Count'),
            on=[selected_breakdown, 'Religion']
        )

        # Display Title
        if selected_unit == 'All' and selected_subunit == 'All' and selected_layer == 'All':
            title_text = "Religion Summary (All Units)"
        else:
            title_text = f"Religion Summary (Filtered by {selected_unit}, {selected_subunit}, {selected_layer})"

        st.title(title_text)
        st.subheader(f"Percentage of Religion by {selected_breakdown}")

        st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

        # Display religion percentages and counts (Top Part)
        total_counts = religion_counts.sum().sum()

        # Check if total_counts is 0 to avoid NaN values
        if total_counts == 0:
            # If total is zero, set all percentages to zero
            total_percentage = {religion: 0 for religion in color_map.keys()}
            religion_sums = {religion: 0 for religion in color_map.keys()}
        else:
            religion_sums = religion_counts.sum()
            total_percentage = (religion_sums / total_counts * 100).round(2)

        # Display religion percentage summary with counts
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

        col1.markdown(f"<div style='text-align: center'><h5>Islam</h5><h1><strong>{total_percentage['Islam']}%</strong></h1><p>{int(religion_sums['Islam'])}</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div style='text-align: center'><h5>Kristen</h5><h1><strong>{total_percentage['Kristen']}%</strong></h1><p>{int(religion_sums['Kristen'])}</p></div>", unsafe_allow_html=True)
        col3.markdown(f"<div style='text-align: center'><h5>Katholik</h5><h1><strong>{total_percentage['Katholik']}%</strong></h1><p>{int(religion_sums['Katholik'])}</p></div>", unsafe_allow_html=True)
        col4.markdown(f"<div style='text-align: center'><h5>Hindu</h5><h1><strong>{total_percentage['Hindu']}%</strong></h1><p>{int(religion_sums['Hindu'])}</p></div>", unsafe_allow_html=True)
        col5.markdown(f"<div style='text-align: center'><h5>Buddha</h5><h1><strong>{total_percentage['Buddha']}%</strong></h1><p>{int(religion_sums['Buddha'])}</p></div>", unsafe_allow_html=True)
        col6.markdown(f"<div style='text-align: center'><h5>Kepercayaan</h5><h1><strong>{total_percentage['Kepercayaan']}%</strong></h1><p>{int(religion_sums['Kepercayaan'])}</p></div>", unsafe_allow_html=True)
        col7.markdown(f"<div style='text-align: center'><h5>Kong Hu Cu</h5><h1><strong>{total_percentage['Kong Hu Cu']}%</strong></h1><p>{int(religion_sums['Kong Hu Cu'])}</p></div>", unsafe_allow_html=True)

        st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

        # Horizontal stacked percentage bar chart for Religion Distribution by Breakdown Variable
        bar_chart = alt.Chart(religion_combined).mark_bar().encode(
            x=alt.X('Percentage:Q', title='Percentage', scale=alt.Scale(domain=[0, 100])),  # x-axis is percentage (0-100%)
            y=alt.Y(f'{selected_breakdown}:N', title=selected_breakdown),  # Use the selected breakdown variable (Unit, Subunit, Layer)
            color=alt.Color('Religion:N', scale=alt.Scale(domain=list(color_map.keys()), range=list(color_map.values()))),
            tooltip=[alt.Tooltip(f'{selected_breakdown}:N'), alt.Tooltip('Percentage:Q', format='.2f'),
                     alt.Tooltip('Count:Q', title='Count'), 'Religion:N']
        ).properties(
            title=f'Religion Distribution by {selected_breakdown} (Stacked Bar Chart)',
            width=700,
            height=400
        )

        # Display the bar chart in Streamlit (Bottom Part)
        st.altair_chart(bar_chart, use_container_width=True)

    if selected_page == 'Tenure':
            # If all filters are set to "All", use the entire dataset, else use the filtered data
            if selected_unit == 'All' and selected_subunit == 'All' and selected_layer == 'All':
                display_df = df  # Use entire dataset
            else:
                display_df = filtered_df  # Use filtered dataset

            # Define bins for grouping the years of service
            bins = [-1, 1, 3, 6, 10, 15, 20, 25, float('inf')]
            labels = ['<1 Year', '1-3 Year', '4-6 Year', '6-10 Year', '11-15 Year', '16-20 Year', '20-25 Year', '>25 Year']

            # Create a new column in the DataFrame that categorizes years of service
            display_df['Service_Group'] = pd.cut(display_df['Years'], bins=bins, labels=labels, right=False)

            # Group by the selected breakdown variable and calculate tenure distribution
            tenure_counts = display_df.groupby([selected_breakdown, 'Service_Group']).size().unstack().fillna(0)

            # Define a consistent color scheme for tenure groups
            color_map = {
                '<1 Year': '#1f77b4',       # Blue
                '1-3 Year': '#ff7f0e',      # Orange
                '4-6 Year': '#2ca02c',      # Green
                '6-10 Year': '#d62728',     # Red
                '11-15 Year': '#9467bd',    # Purple
                '16-20 Year': '#8c564b',    # Brown
                '20-25 Year': '#e377c2',    # Pink
                '>25 Year': '#7f7f7f'       # Gray
            }

            # Ensure that all tenure groups exist in the data; if not, add them with a count of 0
            for tenure_group in color_map.keys():
                if tenure_group not in tenure_counts.columns:
                    tenure_counts[tenure_group] = 0

            # Calculate percentages for each group
            tenure_percentage = tenure_counts.div(tenure_counts.sum(axis=1), axis=0) * 100
            tenure_percentage = tenure_percentage.reset_index()

            # Combine count and percentage data for tooltips by melting the data
            tenure_combined = tenure_percentage.melt(id_vars=[selected_breakdown], value_vars=list(color_map.keys()),
                                                    var_name='Tenure Group', value_name='Percentage')

            # Merge with the original count data to get the counts for each tenure group and breakdown group
            tenure_combined = tenure_combined.merge(
                tenure_counts.reset_index().melt(id_vars=[selected_breakdown], value_vars=list(color_map.keys()),
                                                var_name='Tenure Group', value_name='Count'),
                on=[selected_breakdown, 'Tenure Group']
            )

            # Display Title
            if selected_unit == 'All' and selected_subunit == 'All' and selected_layer == 'All':
                title_text = "Tenure Summary (All Units)"
            else:
                title_text = f"Tenure Summary (Filtered by {selected_unit}, {selected_subunit}, {selected_layer})"

            st.title(title_text)
            st.subheader(f"Percentage of Tenure by {selected_breakdown}")

            st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

            # Display tenure percentages and counts (Top Part)
            total_counts = tenure_counts.sum().sum()

            # Check if total_counts is 0 to avoid NaN values
            if total_counts == 0:
                # If total is zero, set all percentages to zero
                total_percentage = {tenure_group: 0 for tenure_group in color_map.keys()}
                tenure_sums = {tenure_group: 0 for tenure_group in color_map.keys()}
            else:
                tenure_sums = tenure_counts.sum()
                total_percentage = (tenure_sums / total_counts * 100).round(2)

            # Display tenure percentage summary with counts
            cols = st.columns(len(color_map.keys()))

            for i, tenure_group in enumerate(color_map.keys()):
                cols[i].markdown(f"<div style='text-align: center'><h5>{tenure_group}</h5>"
                                f"<h1><strong>{total_percentage[tenure_group]}%</strong></h1>"
                                f"<p>{int(tenure_sums[tenure_group])}</p></div>", unsafe_allow_html=True)

            st.markdown("<hr style='border:1px solid #000'>", unsafe_allow_html=True)

            # Horizontal stacked percentage bar chart for Tenure Distribution by Breakdown Variable
            bar_chart = alt.Chart(tenure_combined).mark_bar().encode(
                x=alt.X('Percentage:Q', title='Percentage', scale=alt.Scale(domain=[0, 100])),  # x-axis is percentage (0-100%)
                y=alt.Y(f'{selected_breakdown}:N', title=selected_breakdown),  # Use the selected breakdown variable (Unit, Subunit, Layer)
                color=alt.Color('Tenure Group:N', scale=alt.Scale(domain=list(color_map.keys()), range=list(color_map.values()))),
                tooltip=[alt.Tooltip(f'{selected_breakdown}:N'), alt.Tooltip('Percentage:Q', format='.2f'),
                        alt.Tooltip('Count:Q', title='Count'), 'Tenure Group:N']
            ).properties(
                title=f'Tenure Distribution by {selected_breakdown} (Stacked Bar Chart)',
                width=700,
                height=400
            )

            # Display the bar chart in Streamlit (Bottom Part)
            st.altair_chart(bar_chart, use_container_width=True)