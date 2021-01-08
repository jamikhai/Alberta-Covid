# Author: Justin Mikhail
# Special thanks to: opencovid.ca and https://github.com/ishaberry/Covid19Canada for COVID data,
# Stats Canada for population data: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1710000901
import sqlite3
from graphs import *
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine


def main():
    data_names = ["active", "cases", "mortality", "recovered", "testing"]
    prov_list = [
        "Alberta", "BC",
        "Manitoba", "New Brunswick",
        "NL", "Nova Scotia",
        "Ontario", "PEI",
        "Quebec", "Saskatchewan",
        "NWT", "Nunavut", "Yukon"
    ]

    # Give choice to update database to save time
    choice  = input("Update database? (y/n) ")
    if choice.lower() in ["y", "yes"]:
        update_database(prov_list, data_names)

    province_populations = read_province_population()

    recent_date = get_last_updated()

    #line_cumulative(prov_list, recent_date)

    #pie_chart(prov_list, recent_date)

    bar_active_per_hundred_thou(prov_list, recent_date, province_populations)

    bar_province_fatality(prov_list, recent_date, province_populations)

    line_active(prov_list, recent_date)

    return


def update_database(prov_list, data_names):
    """
    Updates SQLite3 DB by replacing existing tables or creating them
    """
    for prov in prov_list:
            # Creates a dataframe for each data name, then creates
            # a table in the database for the dataframe
            print(f"Updating {prov}")
            for name in data_names:
                df = data_to_df(name)
                province_df_to_db(df, prov, name)
    return


def data_to_df(csv_name):
    """
    Takes online csv and turns it into a dataframe
    """
    url = f"https://raw.githubusercontent.com/ishaberry/Covid19Canada/master/timeseries_prov/{csv_name}_timeseries_prov.csv"
    df = pd.read_csv(url)

    return df


def province_df_to_db(df, province, csv_name):
    """
    Creates a table in the database for the province called
    """
    # Filter for rows that match the province
    #prov_df = df[df.province == f"{province}"]
    prov_df = df.loc[df.loc[:, "province"] == f"{province}", :].copy()
    # Convert date column to datetime type so SQL knows its a date
    #prov_df[prov_df.columns[1]] = pd.to_datetime(prov_df[prov_df.columns[1]], format='%d-%m-%Y').dt.date
    prov_df.iloc[:, 1] = pd.to_datetime(prov_df.iloc[:, 1], format='%d-%m-%Y').dt.date

    engine = create_engine("sqlite:///covid_canada.db")
    sqlite_connection = engine.connect()

    # Get rid of spaces in table names so they can be queried correctly
    province = province.replace(" ", "_")
    # Each province gets a table for each set of data (13 * 5 = 65 tables)
    title = f"{csv_name}_{province}"
    # Will replace existing tables in DB so it can be updated each day
    prov_df.to_sql(title, con=engine, if_exists='replace', index=False)
    sqlite_connection.close()

    return


def get_last_updated():
    """
    Gets the most recent date the database was updated
    """
    engine = create_engine("sqlite:///covid_canada.db")
    sqlite_connection = engine.connect()

    data = sqlite_connection.execute(f"""
        SELECT date_report
        FROM cases_BC
        ORDER BY date_report DESC
        LIMIT 1
    """)
    date = pd.to_datetime(data.fetchone()[0], format='%Y-%m-%d').date()
    return date


def read_province_population():
    """
    Reads csv and returns a dictionary of region: population pairs
    """
    # Read in population data into a dataframe
    pop_df = pd.read_csv("canada_populations.csv")
    # Create dictionary of province: population (key: value)
    populations = {}
    for i in range(len(pop_df)):
        region = pop_df["GEO"][i]
        number = int(pop_df["VALUE"][i])
        populations[region] = number

    # Update keys so they are compatible with prov_list
    populations["BC"] = populations.pop("British Columbia")
    populations["NL"] = populations.pop("Newfoundland and Labrador")
    populations["PEI"] = populations.pop("Prince Edward Island")
    populations["NWT"] = populations.pop("Northwest Territories")

    return populations

if __name__ == '__main__':
    main()
