from sentinelsat import SentinelAPI
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import calendar

# grab credentials
usr = input('sentinelsat username: ')
pwd = input('sentinelsat password: ')

# grab coordinates
lat = float(input('lat: '))
lon = float(input('lon: '))

# additional user input
get_data = input('get data [y/n]? ')

# instantiate connection
api = SentinelAPI(usr, pwd, 'https://apihub.copernicus.eu/apihub')

if get_data == 'y':
    
    # query metadata for specific point, time range
    products_df = api.query(
        footprint=f'intersects({lat}, {lon})',
        date=('20140101', datetime.datetime.now()),
        platformname='Sentinel-2',
        processinglevel='Level-2A')
    
    # keep only relevant columns to reduce amount of data
    keepcols = ['filename', 'beginposition', 'relativeorbitnumber', 'cloudcoverpercentage', 'orbitdirection']
    products_df = api.to_dataframe(products_df)
    products_df = products_df[keepcols]
    
    # keep data for only one tileid, because the same acquisition is sometimes put onto different tiles,
    # even though it's the exact same data. this happens when the area of interest lies in the
    # overlap zone of different tiles, which becomes bigger in higher latitudes
    products_df['tileid'] = products_df['filename'].apply(lambda x: x.split('_')[5])
    unique_tileid = products_df['tileid'].unique()[0]
    products_df = products_df[products_df['tileid'] == unique_tileid]
    
    # create unique tileid_acquisitiondate strings from product filenames.
    # this allows keeping only single acquisitions and avoiding repeated data
    # (because the same acquisition may have been used to create different products)
    def get_tileid_and_acquisition_date(i):
        i_split = i.split('_')
        return f'{i_split[5]}_{i_split[2]}'
    products_df['tileid_acquisitiondate'] = products_df['filename'].apply(
        get_tileid_and_acquisition_date)
    products_df.drop_duplicates(subset='tileid_acquisitiondate', keep='first', inplace=True)
    
    # make separate columns for month, year and julian day (day of year)
    # used for plotting years in separate curves
    products_df['month'] = products_df['beginposition'].apply(
        lambda x: x.strftime('%m'))
    products_df['day_of_year'] = products_df['beginposition'].apply(
        lambda x: x.strftime('%j'))
    products_df['year'] = products_df['beginposition'].apply(
        lambda x: x.strftime('%Y'))

    # save data to dataframe locally
    products_df.to_csv('/data/prods.csv')
    
    # delete object
    del products_df

# get data from local disk
products_df = pd.read_csv('/data/prods.csv')

# plot median cloudiness per month
years = products_df['year'].unique()
fig, ax = plt.subplots(figsize=(10, 4))
for year in years:
    data = products_df[products_df['year'] == year].sort_values(by='day_of_year')
    data_months = data.groupby('month')
    monthly_medians = data_months['cloudcoverpercentage'].median()
    months = data_months['month'].first()
    ax.plot(months, monthly_medians, label=year)
    ax.set_ylabel('Image cloudiness %, median')
    ax.set_xticks(range(1, 13)); ax.set_xticklabels(calendar.month_abbr[1:])
plt.legend()
plt.savefig('/data/monthlycloudcover.png')


