# Author: Justin Mikhail
# Special thanks to opencovid.ca and https://github.com/ishaberry/Covid19Canada for data
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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
    for prov in prov_list:
        if choice in ['y', "Y", 'yes', 'Yes']:
            # Creates a dataframe for each data name, then creates
            # a table in the database for the dataframe
            for name in data_names:
                df = data_to_df(name)
                province_df_to_db(df, prov, name)
        # Adds province to graph
        plot_province(prov)

    # Graph features
    plt.title("COVID-19 in Canada")
    plt.legend(loc='best')
    plt.xlabel("Dates")
    plt.ylabel("Cumulative Cases")
    plt.gcf().autofmt_xdate() # Handles rotation and date formatting
    plt.show()

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
    prov_df = df[df.province == f"{province}"]
    # Convert date column to datetime type so SQL knows its a date
    prov_df[prov_df.columns[1]] = pd.to_datetime(prov_df[prov_df.columns[1]], format='%d-%m-%Y').dt.date

    engine = create_engine("sqlite:///covid_canada.db", echo=True)
    sqlite_connection = engine.connect()

    # Get rid of spaces in table names so they can be queried correctly
    province = province.replace(" ", "_")
    # Each province gets a table for each set of data (13 * 5 = 65 tables)
    title = f"{csv_name}_{province}"
    # Will replace existing tables in DB so it can be updated each day
    prov_df.to_sql(title, con=engine, if_exists='replace', index=False)
    sqlite_connection.close()

    return


def case_data_for_graph(province):
    """
    Queries DB for date and case data for a province to generate compatible
    graph data
    """
    engine = create_engine("sqlite:///covid_canada.db", echo=True)
    sqlite_connection = engine.connect()

    # Ensure province matches table name format
    province = province.replace(" ", "_")
    # Get data from DB through query
    data = sqlite_connection.execute(f"""
        SELECT date_report, cumulative_cases
        FROM cases_{province}
    """)
    # data is a list with an item = (date, cumulative_case) tuple
    x0 = []
    y = []
    for item in data:
        x0.append(item[0])
        y.append(item[1])

    # Convert to datetime as matplotlib will handle datetime on its own
    x1 = pd.to_datetime(x0, format='%Y-%m-%d')
    sqlite_connection.close()

    return x1, y


def plot_province(province):
    """
    Adds province to graph
    """
    x, y = case_data_for_graph(province)
    plt.plot(x, y, label=province)
    return

main()
