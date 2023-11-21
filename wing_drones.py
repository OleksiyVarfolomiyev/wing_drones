import streamlit as st;
st.set_page_config(layout="wide")

import ETL as etl
import data_aggregation_tools as da
import charting_tools

import pandas as pd
import numpy as np
import datetime as dt

import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import iplot
import plotly.figure_factory as ff
import plotly.io as pio
from plotly.subplots import make_subplots

st.title("Wing Drones")

def show_metrics(df):
    """ Show metrics"""

    starting_date = df['Date'].min()
    end_date = df['Date'].max()

    col1, col2, col3 = st.columns(3)
    col1.metric("Days", (end_date - starting_date).days, "1", delta_color="normal")
    col2.metric("Publications", etl.format_money(len(df)), len(df[df['Date'] == end_date  - pd.Timedelta(days=1)]), delta_color="normal")
    #col3.metric("Spending",  etl.format_money(spending_total.UAH.sum()),  spending_latest, delta_color="normal")

df = etl.read_data()
show_metrics(df)

def show_categories_countries_regions(df):
    """Show categories, countries, regions"""
    top_categories = ['UAV: Supercam', 'UAV: Orlan', 'UAV: Zala', 'UAV: Geran', 'UAV: Lantset', 'Aspect: Target', 'Aspect: Camera', 'Aspect: Signal', 'UAV: DJI']
    category_counts = {}

    for category in top_categories:
        count = df['Categories'].str.contains(category).sum()
        category_counts[category] = count

    category_counts_df = pd.DataFrame.from_dict(category_counts, orient='index', columns=['Count'])
    category_counts_df = category_counts_df.reset_index()
    category_counts_df.rename(columns={'index': 'Categories'}, inplace=True)
    category_counts_df = category_counts_df.set_index('Categories')

    fig = charting_tools.pie_plot(category_counts_df, 'Count', 'Top Categories', False)
    st.plotly_chart(fig, use_container_width=True)

    country_counts = df['Country'].value_counts().to_frame(name='Count').sort_values(by='Count', ascending=False)
    country_counts = country_counts.drop('Undefined')
    fig1 = charting_tools.pie_plot(country_counts.head(5), 'Count', 'Country', False)

    region_counts = df['Region'].value_counts().to_frame(name='Count').sort_values(by='Count', ascending=False)
    region_counts = region_counts.dropna()
    region_counts = region_counts.drop('Undefined')
    fig2 = charting_tools.pie_plot(region_counts.head(5), 'Count', "Region", False)

    fig1.write_image("fig/Country.png")
    fig2.write_image("fig/Region.png")

    fig = charting_tools.subplot_horizontal(fig1, fig2, 1, 2, 'domain', 'domain', 'Country', 'Region', False)
    st.plotly_chart(fig, use_container_width=True)

show_categories_countries_regions(df)

def show_publications_by_media_type(df):
    """ Show publications # The `by med` parameter is used to group the data by media type. It is used
    # in the `show_top_profiles_by_publication_count` function to calculate the
    # count of each media type and author combination in the original DataFrame.
    # This allows us to determine the top profiles by publication count in each
    # media type.
    by media type"""
    media_types = df['Media type'].unique().tolist()

    col0, col1, col2 = st.columns(3)
    with col1:
        timeperiod = st.selectbox(' ', ['Daily', 'Weekly', 'Monthly'])

    if timeperiod == 'Monthly':
        count_by_period = df.groupby([df['Date'].dt.to_period('M').dt.start_time, 'Media type'])['Link'].count().unstack().fillna(0)
        count_by_period.index = count_by_period.index.strftime('%Y-%m')

    elif timeperiod == 'Weekly':
        count_by_period = df.groupby([df['Date'].dt.to_period('W').dt.start_time, 'Media type'])['Link'].count().unstack().fillna(0)
        count_by_period.index = count_by_period.index.strftime('%Y-%m-%d')
    else:
        count_by_period = df.groupby([df['Date'].dt.to_period('D').dt.start_time, 'Media type'])['Link'].count().unstack().fillna(0)
        count_by_period.index = count_by_period.index.strftime('%Y-%m-%d')

    fig = go.Figure()
    for category in media_types:
        fig.add_trace(go.Bar(
            x=count_by_period.index,
            y=count_by_period[category],
            name=category
        ))

    fig.update_layout(barmode='stack')#, title='Publications by media type')
    st.plotly_chart(fig, use_container_width=True)

show_publications_by_media_type(df)

# Ring plot - Donations and Spending by Category
def show_sources(df):
    """ Show sources"""
    #starting_date = df['Date'].min()
    #end_date = df['Date'].max()

    source_counts = pd.DataFrame(df['Source'].value_counts()).reset_index()
    source_counts.columns = ['Source', 'Count']
    df_unique_authors = df.drop_duplicates(subset=['Source', 'Profile'])

    df['Audience_or_Followers'] = np.where(df['Audience'].notna(), df['Audience'], df['Followers'])
    df_unique_authors = df.drop_duplicates(subset=['Source', 'Author'])
    df_audience_by_source = df_unique_authors.groupby('Source')['Audience_or_Followers'].sum().reset_index()
    df_audience_by_source = df_audience_by_source[df_audience_by_source['Audience_or_Followers'] > 0]
    df_audience_by_source = df_audience_by_source.sort_values(by='Audience_or_Followers', ascending=False)
    df_audience_by_source['Audience_or_Followers'] = df_audience_by_source['Audience_or_Followers'].apply(etl.format_money)
    df_audience_by_source = df_audience_by_source.rename(columns={'Audience_or_Followers': 'Audience'})
    df_audience_by_source['Audience'] = df_audience_by_source['Audience'].fillna('')
    df_audience_by_source.reset_index(drop=True, inplace=True)

    sources_stats = pd.merge(source_counts, df_audience_by_source, on='Source', how='outer')
    sources_stats = sources_stats[sources_stats['Count'] >=20]
    sources_stats['Audience'] = sources_stats['Audience'].fillna('')

    fig = px.treemap(sources_stats, path=['Source'], values='Count',
                    color='Audience',
                    color_continuous_scale='RdBu',
                    #title='Sources',
                    custom_data=['Count', 'Audience'])

    fig.update_traces(texttemplate='%{label}<br>Count: %{customdata[0]}<br>Audience: %{customdata[1]}',
                    textposition='middle center')

    st.plotly_chart(fig, use_container_width=True)

show_sources(df)

def donations_spending_by_period_by_category(donations_total_by_category, spending_total_by_category,
                                            large_donations_by_category, large_spending_by_category,
                                            donations_below_large_by_category, spending_below_large_by_category):
    """Donations/Spending by time period (d, w, m) and large/regular amounts"""
    #main_donation_categories = donations_total_by_category.groupby('Category')['UAH'].sum().sort_values(ascending = False).index[:4].tolist()
    main_donation_categories = donations_total_by_category.groupby('Category')['UAH'].sum().sort_values(ascending=False).index.tolist()
    #main_spending_categories = spending_total_by_category.groupby('Category')['UAH'].sum().sort_values(ascending = False).index[:4].tolist()
    main_spending_categories = spending_total_by_category.groupby('Category')['UAH'].sum().sort_values(ascending = False).index.tolist()
    col0, col1, col2 = st.columns(3)
    with col0:
        amount = st.selectbox(' ',[' all ', '>100K', '<100K'])
    with col1:
        selected_period = st.selectbox(' ',['monthly', 'weekly', 'daily', 'yearly'])
    with col2:
        donations_spending = st.selectbox(' ', ['donations', 'spending'])

    if amount == '>100K':
        donations_by_category = large_donations_by_category
        spending_by_category = large_spending_by_category
    elif amount == '<100K':
        donations_by_category = donations_below_large_by_category
        spending_by_category = spending_below_large_by_category
    else:
        donations_by_category = donations_total_by_category
        spending_by_category = spending_total_by_category

    if donations_spending == 'donations':
        main_categories = main_donation_categories
        tx_by_category = donations_by_category
    else:
        main_categories = main_spending_categories
        tx_by_category = spending_by_category

    fig = charting_tools.chart_by_period(tx_by_category, main_categories, selected_period[0],
                                        f'{selected_period} {amount} {donations_spending}')
    st.plotly_chart(fig, use_container_width=True)

# donations_spending_by_period_by_category(donations_total_by_category, spending_total_by_category,
#                                                                         large_donations_by_category, large_spending_by_category,
#                                                                         donations_below_large_by_category, spending_below_large_by_category)

#st.markdown("Visit [Dignitas Fund](https://dignitas.fund/)")


def show_top_profiles_by_publication_count(df):

    df.loc[df['Media type'] == 'Social Networks', 'Media type'] = df['Source']
    # Create a list to store the top authors DataFrames
    top_authors_list = []
    # Calculate the value counts of 'Media type'
    media_type_counts = df['Media type'].value_counts()

    # Calculate the count of each 'Media type' and 'Author' combination in the original DataFrame
    author_counts = df.groupby(['Media type', 'Profile']).size()

    # Loop through each 'Media type' sorted by the total count
    for media_type in media_type_counts.index:
        # Select the counts for the current 'Media type'
        counts = author_counts[media_type]

        # Sort authors by count and select the top 10
        top_authors = counts.sort_values(ascending=False).head(10).reset_index()

        # Rename the 0 column to 'Count'
        top_authors.rename(columns={0: 'Count'}, inplace=True)

        # Append the total count to the 'Media type' column
        top_authors['Media type'] = f"{media_type}"

        # Append the top authors DataFrame to the list
        top_authors_list.append(top_authors)

    # Concatenate all DataFrames in the list
    top_authors_df = pd.concat(top_authors_list)

    # Define the new order of columns
    columns_order = ['Media type', 'Profile', 'Count']

    # Re-order the columns
    top_authors_df = top_authors_df[columns_order]

    # Merge top_authors_df with df to add 'Followers', 'Friends', and 'Following'
    top_authors_df = pd.merge(top_authors_df, df[['Media type', 'Profile', 'Followers', 'Friends', 'Following']], how='left', on=['Media type', 'Profile'])

    # Remove duplicate rows
    top_authors_df = top_authors_df.drop_duplicates(subset='Profile')

    # Group df by 'Media type' and 'Profile' and calculate the sum of 'Shares', 'Likes', and 'Views'
    df_grouped = df.groupby(['Media type', 'Profile'])[['Shares', 'Likes', 'Views']].sum().reset_index()

    # Merge top_authors_df with df_grouped
    top_authors_df = pd.merge(top_authors_df, df_grouped, how='left', on=['Media type', 'Profile'])

    st.subheader("Top profiles by publication count (in each media type)")
    st.dataframe(top_authors_df)
    return top_authors_df

top_authors_df = show_top_profiles_by_publication_count(df)


def show_top_publications_by_profile(top_authors_df, df):
    """Show publications in top profile"""
    selected_profile = st.selectbox('Select top profile to view publications', top_authors_df['Profile'])
    filtered_df = df[df['Profile'] == selected_profile][['Date', 'Link', 'Title']]
    filtered_df['Date'] = filtered_df['Date'].dt.date

    st.dataframe(filtered_df)

show_top_publications_by_profile(top_authors_df, df)