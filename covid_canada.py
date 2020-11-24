# Author: Justin Mikhail
# Special thanks to opencovid.ca and https://github.com/ishaberry/Covid19Canada for data
import pandas as pd
import sqlite3
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

    for prov in prov_list:
        for name in data_names:
            df = data_to_df(name)
            province_df_to_db(df, prov, name)

    return


def data_to_df(csv_name):
    # Takes online csv and turns it into a dataframe
    url = f"https://raw.githubusercontent.com/ishaberry/Covid19Canada/master/timeseries_prov/{csv_name}_timeseries_prov.csv"
    df = pd.read_csv(url)
    return df


def province_df_to_db(df, province, csv_name):
    # Creates a table in the database for the province called
    prov_df = df[df.province == f"{province}"]
    prov_df[prov_df.columns[1]] = pd.to_datetime(prov_df[prov_df.columns[1]]).dt.date

    engine = create_engine("sqlite:///covid_canada.db", echo=True)
    sqlite_connection = engine.connect()

    province = province.replace(" ", "_")
    title = f"{csv_name}_{province}"
    prov_df.to_sql(title, con=engine, if_exists='replace', index=False)
    sqlite_connection.close()
    return


main()
