import wget
spacex_launch_dash = wget.download('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv', out="/tmp/")

# Import required libraries
import pandas as pd
import dash
import dash.html as html
import dash.dcc as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv(spacex_launch_dash)
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': ls, 'value': ls} for ls in spacex_df["Launch Site"].unique()]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                        
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                            options=dropdown_options,
                                            value='ALL',
                                            placeholder="Select a Launch Site here",
                                            searchable=True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                                min=min_payload, max=max_payload, step=1000,
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df.copy()
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, values='class', 
        names='Launch Site', 
        title='Total Launches with successful landing by launch site')
        return fig
    else:
        class_count_df = filtered_df[filtered_df["Launch Site"] == entered_site].value_counts('class')
        fig = px.pie(values=class_count_df, 
            names=class_count_df.index, 
            title=f'Landing outcome split for {entered_site} launch site')
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")])
def get_scatter_plot(entered_site, payload_mass):
    filtered_df = spacex_df[(spacex_df["Payload Mass (kg)"] >= payload_mass[0]) & (spacex_df["Payload Mass (kg)"] <= payload_mass[1])].copy()
    title = f'Launch success class vs. payload mass'
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df["Launch Site"] == entered_site]
        title += f' for {entered_site} launch site'
    fig = px.scatter(filtered_df, x="Payload Mass (kg)", y='class', color='Booster Version', title=title)

    return fig
    



# Run the app
if __name__ == '__main__':
    app.run_server()