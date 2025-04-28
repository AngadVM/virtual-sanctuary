import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import webbrowser
import os
from datetime import datetime
import time

def get_gbif_data(animal_name):
    """Fetch animal data from GBIF API"""
    url = f"https://api.gbif.org/v1/occurrence/search?q={animal_name}&hasCoordinate=true&hasGeospatialIssue=false"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

def get_inaturalist_data(animal_name):
    """Fetch animal data from iNaturalist API"""
    url = f"https://api.inaturalist.org/v1/observations/species_counts?q={animal_name}&has_photos=true&verifiable=true"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

def get_animal_data(animal_name):
    """Fetch and combine data from multiple sources"""
    print("Fetching data from GBIF...")
    gbif_data = get_gbif_data(animal_name)
    
    print("Fetching data from iNaturalist...")
    inat_data = get_inaturalist_data(animal_name)
    
    # Process GBIF data
    gbif_records = []
    for record in gbif_data:
        try:
            lat = float(record.get('decimalLatitude', 0))
            lon = float(record.get('decimalLongitude', 0))
            year = int(record.get('year', 0))
            
            # Validate coordinates
            if -90 <= lat <= 90 and -180 <= lon <= 180 and 1800 <= year <= 2024:
                gbif_records.append({
                    'latitude': lat,
                    'longitude': lon,
                    'year': year,
                    'source': 'GBIF',
                    'country': record.get('country', 'Unknown'),
                    'basisOfRecord': record.get('basisOfRecord', 'Unknown')
                })
        except (ValueError, TypeError):
            continue
    
    # Process iNaturalist data
    inat_records = []
    for record in inat_data:
        try:
            lat = float(record.get('latitude', 0))
            lon = float(record.get('longitude', 0))
            year = int(record.get('observed_on', '2000').split('-')[0])
            
            # Validate coordinates
            if -90 <= lat <= 90 and -180 <= lon <= 180 and 1800 <= year <= 2024:
                inat_records.append({
                    'latitude': lat,
                    'longitude': lon,
                    'year': year,
                    'source': 'iNaturalist',
                    'country': record.get('place_guess', 'Unknown'),
                    'basisOfRecord': 'Human observation'
                })
        except (ValueError, TypeError):
            continue
    
    # Combine data from both sources
    all_records = gbif_records + inat_records
    
    if not all_records:
        print("No valid data found from any source")
        return None
    
    print(f"Found {len(gbif_records)} valid records from GBIF")
    print(f"Found {len(inat_records)} valid records from iNaturalist")
    
    return all_records

def create_visualization(animal_name):
    """Create and save visualization for an animal"""
    # Get data
    data = get_animal_data(animal_name)
    if not data:
        print(f"No valid data found for {animal_name}")
        return None

    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Create output directory if it doesn't exist
    # Make sure the visualizations directory is in the root folder
    visualization_dir = 'visualizations'
    if not os.path.exists(visualization_dir):
        os.makedirs(visualization_dir)

    # Create HTML file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_animal_name = animal_name.replace(' ', '_')
    filename = f"{safe_animal_name}_{timestamp}.html"
    filepath = os.path.join(visualization_dir, filename)
    
    # Create the HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{animal_name} Distribution</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f0f2f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .plot {{ background: white; padding: 20px; border-radius: 10px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #1a237e; margin-bottom: 30px; }}
            h2 {{ color: #303f9f; }}
            .stats {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .stat-item {{ margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
            .source-info {{ font-size: 0.9em; color: #666; margin-top: 10px; }}
            .legend {{ background: white; padding: 10px; border-radius: 5px; position: absolute; bottom: 20px; right: 20px; z-index: 1000; }}
            .legend-item {{ display: inline-block; margin: 0 10px; }}
            .legend-color {{ display: inline-block; width: 12px; height: 12px; margin-right: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{animal_name} Distribution Analysis</h1>
            
            <div class="stats">
                <h2>Statistics</h2>
                <div class="stat-item">Total Observations: {len(data)}</div>
                <div class="stat-item">Countries: {df['country'].nunique()}</div>
                <div class="stat-item">Years: {df['year'].nunique()}</div>
                <div class="stat-item">Most Recent Observation: {df['year'].max()}</div>
                <div class="stat-item">Oldest Observation: {df['year'].min()}</div>
                <div class="stat-item">Data Sources: {df['source'].nunique()}</div>
            </div>

            <div class="plot">
                <h2>Global Distribution</h2>
                {create_map(df)._repr_html_()}
                <div class="source-info">Data sources: GBIF and iNaturalist</div>
            </div>

            <div class="plot">
                <h2>Observations Over Time</h2>
                {create_temporal_plot(df)._repr_html_()}
            </div>
        </div>
    </body>
    </html>
    """

    # Save the HTML file
    with open(filepath, 'w') as f:
        f.write(html_content)

    print(f"Visualization file created at: {filepath}")
    
    # Return just the filename (not the full path)
    # This makes it easier to serve via Flask's static file handler
    return filename

def create_map(df):
    """Create a scatter map showing animal distribution"""
    # Create figure with OpenStreetMap
    fig = go.Figure()
    
    # Add OpenStreetMap as base layer
    fig.add_trace(go.Scattergeo(
        lat=df['latitude'],
        lon=df['longitude'],
        mode='markers',
        marker=dict(
            size=8,
            color=df['year'],
            colorscale='Viridis',
            colorbar=dict(
                title='Year',
                x=0.95,
                y=0.95,
                thickness=15,
                len=0.5
            ),
            opacity=0.8,
            line=dict(
                color='white',
                width=1
            )
        ),
        text=df.apply(lambda row: f"Year: {row['year']}<br>Country: {row['country']}<br>Source: {row['source']}<br>Type: {row['basisOfRecord']}", axis=1),
        hoverinfo='text'
    ))
    
    # Calculate center and zoom level based on data
    lat_center = df['latitude'].mean()
    lon_center = df['longitude'].mean()
    
    # Update layout with better map styling
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            showcountries=True,
            countrycolor='gray',
            coastlinecolor='gray',
            projection_type='mercator',
            fitbounds='locations',
            center=dict(lat=lat_center, lon=lon_center),
            scope='world',
            subunitcolor='gray',
            subunitwidth=1,
            landcolor='rgb(243, 243, 243)',
            oceancolor='rgb(204, 229, 255)'
        ),
        height=700,
        margin={"r":0,"t":30,"l":0,"b":0},
        showlegend=False,
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    # Add title
    fig.update_layout(
        title=dict(
            text='Global Distribution of Observations',
            x=0.5,
            y=0.95,
            xanchor='center',
            yanchor='top',
            font=dict(size=20)
        )
    )
    
    return fig

def create_temporal_plot(df):
    """Create a plot showing observations over time"""
    # Group by year and count observations
    yearly_counts = df.groupby('year').size()
    
    fig = px.line(
        x=yearly_counts.index,
        y=yearly_counts.values,
        title='Observations Over Time',
        labels={'x': 'Year', 'y': 'Number of Observations'},
        color_discrete_sequence=['#1a237e']
    )
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#303f9f'),
        height=400,
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray'
        )
    )
    
    return fig

def main():
    print("\n=== Animal Distribution Visualization Tool ===")
    print("This tool will show you where and when different animals have been observed.")
    print("Example: 'Panthera leo' (Lion), 'Elephas maximus' (Asian Elephant)\n")
    
    while True:
        animal_name = input("Enter animal name (or 'q' to quit): ").strip()
        
        if animal_name.lower() == 'q':
            print("\nThank you for using the Animal Distribution Visualization Tool!")
            break
            
        if not animal_name:
            print("Please enter a valid animal name.")
            continue
            
        print(f"\nGenerating visualization for {animal_name}...")
        try:
            file_path = create_visualization(animal_name)
            
            if file_path:
                print(f"\nVisualization created successfully!")
                print(f"File saved as: visualizations/{file_path}")
                
                # Open the visualization in the default web browser
                absolute_path = os.path.abspath(os.path.join('visualizations', file_path))
                webbrowser.open('file://' + absolute_path)
                print("Opening visualization in your web browser...\n")
            
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}\n")

if __name__ == "__main__":
    main()