import pandas as pd
import data_aggregation_tools as da
import streamlit as st

def format_money(value):
    if abs(value) >= 1e6:
        return '{:.2f}M'.format(value / 1e6)
    elif abs(value) >= 1e3:
        return '{:.2f}K'.format(value / 1e3)
    else:
        return '{:.2f}'.format(value)

def read_data():
    import datetime as dt
    dtypes = { 'Link': 'str', 'Title': 'str', 'Date': 'str', 'Time': 'str', 'Media type': 'str', 'Categories': 'str', 'Subcategory': 'str',
              'Language': 'str', 'Country': 'str', 'Region': 'str', 'Source': 'str', 'Audience': 'str', 'Profile': 'str',
              'Followers': 'int', 'Friends': 'int', 'Following': 'int',
              'Comments': 'int', 'Shares': 'int', 'Likes': 'int', 'Views': 'int'}

    df = pd.read_excel('./data/SuperCam 16.08.2023 - 16.11.2023.xlsx', dtype=dtypes, sheet_name = 'Messages', engine='openpyxl')

    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
    # Fill empty cells in 'Audience' column with 0
    df['Audience'] = df['Audience'].fillna(0)
    # Convert 'Audience' column to integer
    df['Audience'] = df['Audience'].astype(int)
    return df
