import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

def fetch_gbif_data(species_name, limit=2000):
    """Fetch occurrence data for a species from GBIF"""
    print(f"Fetching data from GBIF for {species_name}...")
    base_url = "https://api.gbif.org/v1/occurrence/search"
    
    params = {
        'scientificName': species_name,
        'limit': limit,
        'hasCoordinate': 'true',
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if 'results' not in data:
        return pd.DataFrame()
    
    # Extract coordinates and other relevant information
    occurrences = []
    for record in data['results']:
        if 'decimalLatitude' in record and 'decimalLongitude' in record:
            occurrences.append({
                'latitude': record['decimalLatitude'],
                'longitude': record['decimalLongitude'],
                'source': 'GBIF',
                'country': record.get('country', 'Unknown'),
                'year': record.get('year', None)
            })
    
    return pd.DataFrame(occurrences)

def fetch_inaturalist_data(species_name, limit=2000):
    """Fetch occurrence data for a species from iNaturalist"""
    print(f"Fetching data from iNaturalist for {species_name}...")
    base_url = "https://api.inaturalist.org/v1/observations"
    
    # Convert species name to query format
    query_name = species_name.replace(" ", "+")
    
    params = {
        'q': query_name,
        'per_page': min(limit, 200),  # iNaturalist limits per page
        'quality_grade': 'research',
        'identifications': 'most_agree',
        'geo': 'true',
    }
    
    all_results = []
    page = 1
    total_results = 0
    max_pages = limit // 200 + (1 if limit % 200 > 0 else 0)
    
    while page <= max_pages and total_results < limit:
        params['page'] = page
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if 'results' not in data or not data['results']:
            break
            
        all_results.extend(data['results'])
        total_results += len(data['results'])
        page += 1
        
        # Be nice to the API
        time.sleep(0.5)
    
    # Extract coordinates and other relevant information
    occurrences = []
    for record in all_results:
        if record.get('geojson') and record['geojson'].get('coordinates'):
            coords = record['geojson']['coordinates']
            place = None
            try:
                place = record.get('place_guess', '')
            except:
                place = 'Unknown'
                
            year = None
            try:
                if record.get('observed_on'):
                    year = int(record['observed_on'].split('-')[0])
            except:
                year = None
                
            occurrences.append({
                'latitude': coords[1],
                'longitude': coords[0],
                'source': 'iNaturalist',
                'country': place,
                'year': year
            })
    
    return pd.DataFrame(occurrences)

def create_density_grid(df, resolution=0.5):
    """Create a density grid for heatmap visualization with higher resolution"""
    if df.empty:
        return pd.DataFrame()
        
    # Round coordinates to create grid cells
    df['lat_bin'] = np.round(df['latitude'] / resolution) * resolution
    df['lon_bin'] = np.round(df['longitude'] / resolution) * resolution
    
    # Count occurrences in each grid cell
    density = df.groupby(['lat_bin', 'lon_bin']).size().reset_index(name='count')
    
    return density

def visualize_species_distribution(species_name):
    """Create an optimized, high-resolution map showing species distribution"""
    print(f"Analyzing distribution for: {species_name}")
    start_time = time.time()
    
    # Fetch data from both sources
    gbif_data = fetch_gbif_data(species_name)
    inaturalist_data = fetch_inaturalist_data(species_name)
    
    # Combine the data
    combined_data = pd.concat([gbif_data, inaturalist_data], ignore_index=True)
    
    if combined_data.empty:
        print(f"No occurrence data found for {species_name}")
        return None
    
    print(f"Processing {len(combined_data)} occurrence records...")
    
    # Clean data - remove invalid coordinates and duplicates
    combined_data = combined_data[(combined_data['latitude'] >= -90) & 
                                 (combined_data['latitude'] <= 90) &
                                 (combined_data['longitude'] >= -180) &
                                 (combined_data['longitude'] <= 180)]
    
    # Round coordinates to 4 decimal places (~11m precision) to identify duplicates
    combined_data['lat_rounded'] = np.round(combined_data['latitude'], 4)
    combined_data['lon_rounded'] = np.round(combined_data['longitude'], 4)
    combined_data = combined_data.drop_duplicates(subset=['lat_rounded', 'lon_rounded', 'source'])
    
    # Create density grid for heatmap - higher resolution
    density_data = create_density_grid(combined_data, resolution=0.5)
    
    # Calculate center and appropriate zoom level
    lat_range = combined_data['latitude'].max() - combined_data['latitude'].min()
    lon_range = combined_data['longitude'].max() - combined_data['longitude'].min()
    
    center_lat = combined_data['latitude'].mean()
    center_lon = combined_data['longitude'].mean()
    
    # Determine appropriate zoom based on data spread
    zoom_level = 2  # Default global view
    if lat_range < 20 and lon_range < 20:
        zoom_level = 5  # Regional view
    elif lat_range < 40 and lon_range < 40:
        zoom_level = 4  # Continental view
    elif lat_range < 60 and lon_range < 100:
        zoom_level = 3  # Multi-continental view
    
    # Create the figure - using a single full-screen map for clarity
    fig = go.Figure()
    
    # Add base point layer - use smaller points and optimize for performance
    if len(combined_data) > 5000:
        # For large datasets, sample points to improve performance
        sampled_data = combined_data.sample(5000)
    else:
        sampled_data = combined_data
    
    for source, color in [('GBIF', 'rgba(65, 105, 225, 0.7)'), ('iNaturalist', 'rgba(34, 139, 34, 0.7)')]:
        source_data = sampled_data[sampled_data['source'] == source]
        if not source_data.empty:
            fig.add_trace(
                go.Scattermap(
                    lat=source_data['latitude'],
                    lon=source_data['longitude'],
                    mode='markers',
                    marker=dict(
                        size=4,
                        color=color,
                        opacity=0.7
                    ),
                    text=[
                        f"Source: {row['source']}<br>"
                        f"Location: {row['country']}<br>"
                        f"Year: {row['year'] if pd.notnull(row['year']) else 'Unknown'}<br>"
                        f"Coordinates: {row['latitude']:.5f}, {row['longitude']:.5f}"
                        for _, row in source_data.iterrows()
                    ],
                    hoverinfo='text',
                    name=source
                )
            )
    
    # Add density heatmap as the primary visualization
    if not density_data.empty:
        fig.add_trace(
            go.Densitymap(
                lat=density_data['lat_bin'],
                lon=density_data['lon_bin'],
                z=density_data['count'],
                radius=10,  # Smaller radius for higher resolution
                colorscale=[
                    [0, 'rgba(0,0,255,0)'],      # Transparent for low values
                    [0.1, 'rgba(0,0,255,0.3)'],  # Light blue
                    [0.3, 'rgba(0,0,255,0.5)'],  # Medium blue
                    [0.5, 'rgba(0,0,255,0.7)'],  # Darker blue
                    [0.7, 'rgba(0,0,128,0.8)'],  # Navy
                    [1.0, 'rgba(0,0,128,1)']     # Solid navy
                ],
                zmin=1,
                zmax=max(density_data['count'].max(), 10),
                showscale=True,
                colorbar=dict(
                    title=dict(
                        text='Observation<br>Density',
                        font=dict(size=14)
                    ),
                    thickness=20,
                    len=0.6,
                    y=0.5,
                    yanchor='middle',
                    x=0.98,
                    xanchor='right',
                    tickfont=dict(size=12)
                ),
                name='Species Density'
            )
        )
    
    # Add year-based analysis if data is available
    years_data = combined_data[pd.notnull(combined_data['year'])]
    if not years_data.empty:
        min_year = int(years_data['year'].min())
        max_year = int(years_data['year'].max())
        median_year = int(years_data['year'].median())
        
        # Add a custom annotation about temporal distribution
        fig.add_annotation(
            x=0.01,
            y=0.97,
            xref="paper",
            yref="paper",
            text=f"Temporal range: {min_year} - {max_year} (median: {median_year})",
            showarrow=False,
            font=dict(size=12, color="black"),
            align="left",
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="black",
            borderwidth=1,
            borderpad=4
        )
    
    # Define the optimized map settings
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",  # Clean base map style
            center={"lat": center_lat, "lon": center_lon},
            zoom=zoom_level,
            pitch=0,  # 2D view for clearer distribution pattern
        ),
        height=800,  # Larger height for better resolution
        width=1200,
        margin=dict(l=0, r=0, t=50, b=0),
        title=dict(
            text=f'Distribution of {species_name}',
            x=0.5,
            font=dict(size=20)
        ),
        legend=dict(
            orientation='h',
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="black",
            borderwidth=1
        )
    )
    
    # Add data source info
    source_counts = combined_data['source'].value_counts()
    gbif_count = source_counts.get('GBIF', 0)
    inat_count = source_counts.get('iNaturalist', 0)
    
    fig.add_annotation(
        x=0.01,
        y=0.03,
        xref="paper",
        yref="paper",
        text=f"Data sources: GBIF ({gbif_count} records) and iNaturalist ({inat_count} records)",
        showarrow=False,
        font=dict(size=10),
        align="left",
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="black",
        borderwidth=1,
        borderpad=4
    )
    
    # Save the map as HTML with high resolution
    output_file = f"{species_name.replace(' ', '_')}_distribution_map.html"
    config = {
        'toImageButtonOptions': {
            'format': 'png',
            'filename': f'{species_name.replace(" ", "_")}_map',
            'height': 1200,
            'width': 1800,
            'scale': 2  # High resolution for exports
        },
        'displayModeBar': True,
        'modeBarButtonsToAdd': ['toImage']
    }
    
    fig.write_html(output_file, config=config)
    
    elapsed_time = time.time() - start_time
    print(f"Map created in {elapsed_time:.2f} seconds")
    print(f"Interactive map saved to {output_file}")
    
    return fig

def main():
    """Main function to run the visualization"""
    import plotly.io as pio
    pio.renderers.default = "browser"
    
    species_name = input("Enter a species name (scientific name preferred, e.g., 'Panthera tigris'): ")
    fig = visualize_species_distribution(species_name)
    
    if fig:
        # Open the visualization in browser
        fig.show()
        print(f"Analysis complete for {species_name}")

if __name__ == "__main__":
    main()
