# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Dropdown for launch site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] +
                [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),
    html.Br(),

    # TASK 2: Pie chart to show success counts
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Payload Range Slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 2500)},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Scatter plot to show payload vs success correlation
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback to update pie chart based on dropdown selection
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Count total successful launches per site
        success_counts = spacex_df[spacex_df['class'] == 1]['Launch Site'].value_counts().reset_index()
        success_counts.columns = ['Launch Site', 'Successes']

        fig = px.pie(
            success_counts,
            values='Successes',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
        return fig
    else:
        # Filter data for selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Count success (1) and failure (0)
        site_counts = filtered_df['class'].value_counts().reset_index()
        site_counts.columns = ['Outcome', 'Count']
        site_counts['Outcome'] = site_counts['Outcome'].replace({1: 'Success', 0: 'Failure'})

        fig = px.pie(
            site_counts,
            values='Count',
            names='Outcome',
            title=f'Total Launch Outcomes for site {entered_site}'
        )
        return fig

# TASK 4: Callback to update scatter plot based on dropdown and payload slider
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def get_scatter_plot(entered_site, payload_range):
    low, high = payload_range

    if entered_site == 'ALL':
        filtered_df = spacex_df[
            (spacex_df['Payload Mass (kg)'] >= low) &
            (spacex_df['Payload Mass (kg)'] <= high)
        ]

        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='Class',
            color='Booster Version Category',
            title='Payload vs. Outcome for All Sites'
        )
        return fig

    else:
        filtered_df = spacex_df[
            (spacex_df['Launch Site'] == entered_site) &
            (spacex_df['Payload Mass (kg)'] >= low) &
            (spacex_df['Payload Mass (kg)'] <= high)
        ]

        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Payload vs. Outcome for site {entered_site}'
        )
        return fig

# Run the app
if __name__ == '__main__':
    app.run(port=8060)
