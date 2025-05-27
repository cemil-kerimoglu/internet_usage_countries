# app.py
import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Global Internet Usage (2015)",
    layout="wide",
    initial_sidebar_state="auto",
)

# Cache data loading & processing
@st.cache_data
def load_and_prepare(year_threshold, path_internet_usage, path_countries):
    internet_usage = pd.read_csv(path_internet_usage)
    countries = gpd.read_file(path_countries)

    # Clean datasets: drop OWID aggregates & NaNs
    internet_usage_clean = internet_usage[~internet_usage['Code'].isin(['OWID_WRL', 'OWID_KOS'])].copy()
    valid_iso = set(internet_usage_clean['Code'].str.upper())
    countries_clean = countries[countries['ISO_A3'].isin(valid_iso)].copy()
    internet_usage_clean = internet_usage_clean.dropna(subset=['Code'])

    # Filter to Years ≥ year threshold and find common year
    countries_internet = countries_clean.merge(internet_usage_clean, left_on='ISO_A3', right_on='Code', how='inner', validate='one_to_many').drop(columns=['Code', 'Entity'])
    # total number of countries in the cleaned set
    n_countries = countries_internet['ISO_A3'].nunique()

    # count how many distinct countries have data in each year
    counts_by_year = (
        countries_internet
        .groupby('Year')['ISO_A3']
        .nunique()
    )

    # restrict to years ≥ 2015 where count == total countries
    eligible = counts_by_year[counts_by_year == n_countries]
    eligible = eligible[eligible.index >= year_threshold]

    # pick the latest such year if eligible is not empty
    if not eligible.empty:
        common_year = int(eligible.index.max())
    else:
        coverage_by_year = counts_by_year[counts_by_year.index >= year_threshold]
        if not coverage_by_year.empty:
            best_year = coverage_by_year.idxmax()
            common_year = int(best_year)
        else:
            # Default to the existing common_year if already defined, otherwise use latest available
            common_year = int(counts_by_year.index.max())

    # Subset to that year
    df_plot = countries_internet[countries_internet['Year'] == common_year].copy()
    return df_plot, common_year, countries.__geo_interface__

# Build the Plotly figure
@st.cache_data(show_spinner=False)
def make_figure(_df_plot, common_year, world_geo):
    fig = px.choropleth(
        _df_plot,
        geojson=world_geo,
        locations="ISO_A3",
        featureidkey="properties.ISO_A3",
        color="Individuals using the Internet (% of population)",
        hover_name="ADMIN",
        projection="natural earth",
        color_continuous_scale="Viridis",
        labels={"Individuals using the Internet (% of population)": "Usage (%)"},
        title=f"Internet Usage by Country, {common_year}",
    )
    fig.update_geos(
        showcountries=True,
        coastlinecolor="Gray",
        showcoastlines=True,
        lataxis_showgrid=True,
        lonaxis_showgrid=True,
    )
    fig.update_layout(
        margin={"r":0, "t":50, "l":0, "b":20},
        coloraxis_colorbar=dict(
            title="Usage (%)",
            ticks="outside",
            ticklen=3,
            x=0.8,            
            xanchor="left",
            y=0.5,
            yanchor="middle",
            len=0.85,
        ),
        font=dict(family="Helvetica, Arial", size=12),
    )
    return fig

# Main page
def main():
    
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 1rem;">
          <h1>🌐 Global Internet Usage by Country, 2015</h1>
          <p style="font-size:16px; color: #444;">
            This interactive dashboard shows the share of individuals using the Internet  
            in each country for the year 2015. Data source: Our World in Data.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Load & prepare data
    df_plot, common_year, world_geo = load_and_prepare(2015, "./data/internet_usage.csv", "./data/countries.geojson")

    # Create and display the interactive Plotly map
    fig = make_figure(df_plot, common_year, world_geo)
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},  # hide extra toolbar if you like
    )


if __name__ == "__main__":
    main()
