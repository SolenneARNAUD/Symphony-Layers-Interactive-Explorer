import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from streamlit_plotly_events import plotly_events

#############
# Load Data #
#############

# File paths
doc_path = r"C:\Users\PC\Documents\Ecole\2A\Stage_2A\RISE\Gap_Analysis"
df_SYMPHONY_LAYERS = "df_SYMPHONY_LAYERS.xlsx"
df_recommendation_related_parameters = "df_recommendation_related_parameters.xlsx"
SYMPHONY_LAYERS_path = f"{doc_path}/{df_SYMPHONY_LAYERS}"
recommendation_related_parameters_path = f"{doc_path}/{df_recommendation_related_parameters}"

# Load data
df_SYMPHONY_LAYERS = pd.read_excel(SYMPHONY_LAYERS_path)
df_recommendation_related_parameters = pd.read_excel(recommendation_related_parameters_path)

valuability_smiley = []
data_availability_smiley = []
for _, row in df_SYMPHONY_LAYERS.iterrows():
    if row["Data availability index"] >= 67:
        data_availability_smiley += [':books:']
    elif row["Data availability index"] <= 30:
        data_availability_smiley += [':notebook:']
    else :
        data_availability_smiley += [':page_facing_up:']

    if row["Valuability"] == 'Highly Valuable':
        valuability_smiley += [':bangbang:']
    elif row["Valuability"] == 'Moderately Valuable':
        valuability_smiley += [':exclamation:']
    else :
        valuability_smiley += [':grey_exclamation:']
df_SYMPHONY_LAYERS["Valuability smiley"] = valuability_smiley
df_SYMPHONY_LAYERS["Data availability smiley"] = data_availability_smiley


# Filter and sort data
category = "Ecosystem"
df_filtered = df_SYMPHONY_LAYERS[df_SYMPHONY_LAYERS["Symphony_category"] == category].sort_values(by=["Symphony_theme", "Title"])


###############
# Description #
###############

# Color map for inner pie chart categories
color_map = {
    'Birds': "#5b9bd5",
    'Fish': "#ed7d31",
    'Fish function': '#a5a5a5',
    'Habitat': '#ffc000',
    'Marine Mammals': '#4472c4',
    'Plants': '#70ad47',
}


#############
# Functions #
#############

def get_inner_labels_and_values(df):
    labels = df["Symphony_theme"].unique()
    values = [df["Symphony_theme"].tolist().count(label) for label in labels]
    return labels, values

def get_outer_labels_and_colors(df, inner_labels):
    outer_labels = []
    outer_colors = []
    for label in inner_labels:
        titles = df[df["Symphony_theme"] == label]["Title"].tolist()
        outer_labels.extend(titles)
        outer_colors.extend([color_map[label]] * len(titles))
    return outer_labels, outer_colors

#############
# Pie Chart #
#############

# Prepare data for charts
inner_labels, inner_values = get_inner_labels_and_values(df_filtered)
outer_labels, outer_colors = get_outer_labels_and_colors(df_filtered, inner_labels)
outer_values = [1] * len(outer_labels)  # Equal weight for each outer slice
inner_colors = [color_map[label] for label in inner_labels]

# Plotly donut chart
fig = go.Figure()

# Outer pie
fig.add_trace(go.Pie(
    labels=outer_labels,
    values=outer_values,
    textinfo='label',
    insidetextorientation='radial',
    hole=0.6,
    showlegend=False,
    marker=dict(colors=outer_colors),
    textfont=dict(size=8.5),
))

# Inner pie
fig.add_trace(go.Pie(
    labels=inner_labels,
    values=inner_values,
    textinfo='label',
    insidetextorientation='radial',
    hole=0.4,
    showlegend=False,
    domain={'x': [0.2, 0.8], 'y': [0.2, 0.8]},
    marker=dict(colors=inner_colors),
    sort=False,
    rotation=-20.5,
    textfont=dict(size=10)
))

########
# Plot #
########

st.title('Symphony Layers Interactive Explorer')
st.write('Welcome to the Symphony Layer Interactive Explorer! Simply **click on the layers of the Symphony wheel** below to learn more.')

selected_outer = plotly_events(fig, click_event=True, select_event=False, override_height=780, override_width=780)


if selected_outer:
    point_number = selected_outer[0].get("pointNumber")
    curve_number = selected_outer[0].get("curveNumber")
    if point_number is not None and curve_number == 0:
        clicked_label = outer_labels[point_number]
        row = df_filtered[df_filtered["Title"] == clicked_label].iloc[0]
        df_parameters = df_recommendation_related_parameters[
            df_recommendation_related_parameters["Title"] == clicked_label
            ][[
                'Detailled_parameters_Full_name',
                'Parameter availability index (%)',
                'Horizontal resolution (%)',
                'Spatial coverage (%)',
                'Time coverage (%)',
                'Recent (%)'
            ]]
        st.markdown(
            f"""
            ### {row['Title']}
            {row['Valuability smiley']} {row['Valuability']} {row['Data availability smiley']} **Data availability index (%) :** {row['Data availability index']}
            #### Summary:
            <p style='text-align: justify;'>{row['Summary']}</p>

            #### Recommendation for data improvement :
            <p style='text-align: justify;'>{row['Recommendation']}</p>

            #### Related parameter list :
            <p style='text-align: justify;'>Click on a parameter row to explore the related datasets.</p>

            """,
            unsafe_allow_html=True
        )
        st.dataframe(df_parameters.reset_index(drop=True))
    else:
        st.warning(f"Clicked data: {selected_outer[0]}\nNo label found for the clicked slice.")