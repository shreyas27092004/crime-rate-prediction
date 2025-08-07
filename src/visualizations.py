import plotly.express as px

def create_heatmap(df):
    heatmap_data = df.groupby(['DAY_OF_WEEK', 'HOUR']).size().reset_index(name='counts')
    fig = px.density_heatmap(heatmap_data, 
                             x='HOUR', 
                             y='DAY_OF_WEEK', 
                             z='counts', 
                             title='Crime Incidents Heatmap', 
                             labels={'HOUR': 'Hour of Day', 'DAY_OF_WEEK': 'Day of Week'})
    return fig

def create_map(df):
    map_fig = px.scatter_mapbox(df, 
                                lat='Lat', 
                                lon='Long', 
                                hover_name='OFFENSE_DESCRIPTION',
                                color='OFFENSE_CODE_GROUP', 
                                zoom=10, 
                                height=600)
    map_fig.update_layout(mapbox_style="open-street-map")
    return map_fig