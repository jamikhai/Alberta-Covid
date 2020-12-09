# Author: Justin Mikhail
# Special thanks to opencovid.ca and https://github.com/ishaberry/Covid19Canada for data
import sqlite3
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

    recent_date = get_last_updated()

    line_graph_cumulative(prov_list, recent_date)

    pie_chart(prov_list, recent_date)

    bar_graph(prov_list, recent_date)

    line_graph_active(prov_list, recent_date)

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


def line_graph_cumulative(prov_list, recent_date):
    """
    Adds province to graph of cumulative cases over time
    """
    # Get and plot each provinces data
    current_cumulative = []
    for prov in prov_list:
        x, y = data_for_line_cumulative(prov)
        current_cumulative.append(y[-1])
        plt.plot(x, y, label=prov)

    # Graph features
    plt.title(f"Cumulative Cases Over Time of COVID-19 in Canada\nCurrent Cumulative Cases: {sum(current_cumulative):,}")
    plt.legend(loc='best')
    plt.xlabel(f"Dates\n\nDate of Data: {recent_date}")
    plt.ylabel("Cumulative Cases")
    plt.gcf().autofmt_xdate() # Handles rotation and date formatting
    plt.show()
    plt.clf()
    return


def data_for_line_cumulative(province):
    """
    Queries DB for date and case data for a province to generate compatible
    graph data
    """
    engine = create_engine("sqlite:///covid_canada.db")
    sqlite_connection = engine.connect()

    # Ensure province matches table name format
    province = province.replace(" ", "_")
    # Get data from DB through query
    data = sqlite_connection.execute(f"""
        SELECT date_report, cumulative_cases
        FROM cases_{province}
    """)
    # data is a list with an item = (date, cumulative_case) tuple
    dates0 = []
    cases = []
    for item in data:
        dates0.append(item[0])
        cases.append(item[1])

    # Convert to datetime as matplotlib will handle datetime on its own
    dates1 = pd.to_datetime(dates0, format='%Y-%m-%d')
    sqlite_connection.close()

    return dates1, cases


def pie_chart(prov_list, recent_date):
    """
    Plots all provinces on a pie chart
    """
    # Labels for chart, same order as prov_list
    prov_abbreivations = [
        "AB", "BC", "MB", "NB",
        "NL", "NS", "ON", "PEI",
        "QC", "SK", "NWT", "NU",
        "YK"
    ]

    # List of number of cumulative cases for each province, in the order of prov_list
    values = []
    for prov in prov_list:
        values.append(data_for_pie(prov))

    # Plot pie chart based of values
    wedges, texts = plt.pie(values)

    # Gets percentages of values and sorts them (preserving province) in
    # descending order by province case percentage for the legend
    percents = [num/(sum(values))*100 for num in values]
    legend_labels = [f'{prov} - {percent:.2f} %' for prov, percent in zip(prov_abbreivations, percents)]
    wedges, legend_labels = zip(*sorted(zip(wedges, legend_labels), key=lambda x: float(x[-1].split()[-2]), reverse=True))

    date_text = f"Date of Data: {recent_date}"
    # Graph features
    plt.legend(wedges, legend_labels, title='Provinces', loc='best')
    plt.title(f"Percentages of Cumulative COVID-19 Cases in Canada\nTotal Cumulative Cases: {sum(values):,}")
    plt.figtext(0.4, 0.10, date_text)
    plt.show()
    plt.cla()
    return


def data_for_pie(province):
    """
    Connects to database, queries for cumulative cases for each province
    """
    engine = create_engine("sqlite:///covid_canada.db")
    sqlite_connection = engine.connect()
    province = province.replace(" ", "_")

    data = sqlite_connection.execute(f"""
        SELECT cumulative_cases FROM cases_{province}
        ORDER BY date_report DESC
        LIMIT 1
        """)

    data1 = data.fetchone()
    sqlite_connection.close()
    return data1[0]


def bar_graph(prov_list, recent_date):
    """
    Plots a bar graph comparing current cases in each province
    """
    prov_abbreivations = [
        "AB", "BC", "MB", "NB",
        "NL", "NS", "ON", "PEI",
        "QC", "SK", "NWT", "NU",
        "YK"
    ]

    # Data values for each province
    values = []
    for prov in prov_list:
        values.append(data_for_bar(prov))

    # Graph features
    plt.bar(prov_abbreivations, values)
    plt.ylabel("Active Cases")
    plt.xlabel(f"Province\n\nDate of Data: {recent_date}")
    plt.title(f"Current Active Cases of COVID-19 in Canada: {sum(values):,}")
    plt.show()
    plt.cla()
    return


def data_for_bar(province):
    """
    Queries database for active cases data and returns it for a province
    """
    engine = create_engine("sqlite:///covid_canada.db")
    sqlite_connection = engine.connect()
    province = province.replace(" ", "_")

    # Get DB data
    data = sqlite_connection.execute(f"""
        SELECT active_cases FROM active_{province}
        ORDER BY date_active DESC
        LIMIT 1
        """)

    cases = data.fetchone()
    sqlite_connection.close()
    return cases[0]


def line_graph_active(prov_list, recent_date):
    """
    Adds province to graph of active cases over time
    """
    current_active = []
    # Get and plot each provinces data
    for prov in prov_list:
        x, y = data_for_line_active(prov)
        current_active.append(y[-1])
        plt.plot(x, y, label=prov)

    most_recent = pd.to_datetime(x[-1], format='%Y-%m-%d').date()
    # Graph features
    plt.title(f"Active Cases Over Time of COVID-19 in Canada\nCurrent Active Cases: {sum(current_active):,}")
    plt.legend(loc='best')
    plt.xlabel(f"Dates\n\nDate of Data: {most_recent}")
    plt.ylabel("Active Cases")
    plt.gcf().autofmt_xdate() # Handles rotation and date formatting
    plt.show()
    plt.clf()
    return


def data_for_line_active(province):
    """
    Queries DB for date and case data for a province to generate compatible
    graph data
    """
    engine = create_engine("sqlite:///covid_canada.db")
    sqlite_connection = engine.connect()

    # Ensure province matches table name format
    province = province.replace(" ", "_")
    # Get data from DB through query
    data = sqlite_connection.execute(f"""
        SELECT date_active, active_cases
        FROM active_{province}
    """)
    # data is a list with an item = (date, cumulative_case) tuple
    dates0 = []
    cases = []
    for item in data:
        dates0.append(item[0])
        cases.append(item[1])

    # Convert to datetime as matplotlib will handle datetime on its own
    dates1 = pd.to_datetime(dates0, format='%Y-%m-%d')
    sqlite_connection.close()

    return dates1, cases


if __name__ == '__main__':
    main()
