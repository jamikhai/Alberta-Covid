import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine


# Line Graphs
def line_cumulative(prov_list, recent_date):
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


def line_active(prov_list, recent_date):
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


# Pie Charts
def pie_cumulative(prov_list, recent_date):
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
        values.append(data_for_pie_cumulative(prov))

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


def data_for_pie_cumulative(province):
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


# Bar Graphs
def bar_active_per_hundred_thou(prov_list, recent_date, populations):
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
        values.append(data_for_bar_active_per_hundred_thou(prov))

    per_hundred_thousand = []
    for province, value_of_province in zip(prov_list, values):
        new_value = value_of_province / populations[province] * 100_000
        per_hundred_thousand.append(new_value)

    # Graph features
    plt.bar(prov_abbreivations, per_hundred_thousand)
    plt.ylabel("Active Cases Per 100,000")
    plt.xlabel(f"Province\n\nDate of Data: {recent_date}")
    plt.title(f"Cases Per 100,000 in Canada\nCurrent Total Active Cases: {sum(values):,}")
    plt.show()
    plt.cla()
    return


def data_for_bar_active_per_hundred_thou(province):
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


def bar_province_fatality(prov_list, recent_date, populations):
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
        values.append(data_for_bar_province_fatality(prov))

    fatalities = []
    for deaths, cases in values:
        fatalities.append(deaths / cases * 100)

    # Graph features
    plt.bar(prov_abbreivations, fatalities)
    plt.ylabel("Fatality Rate (%)")
    plt.xlabel(f"Province\n\nDate of Data: {recent_date}")
    plt.title(f"Fatality Rate of COVID-19 in Canada")
    plt.show()
    plt.cla()
    return


def data_for_bar_province_fatality(province):
    """
    Queries database for cumulative death and case data a returns it for a province
    """
    engine = create_engine("sqlite:///covid_canada.db")
    sqlite_connection = engine.connect()
    province = province.replace(" ", "_")

    data = sqlite_connection.execute(f"""
        SELECT cumulative_deaths, cumulative_cases
        FROM mortality_{province}
        JOIN cases_{province}
        ON mortality_{province}.date_death_report = cases_{province}.date_report
        ORDER BY date_report DESC
        LIMIT 1
        """)

    data = list(data)[0]
    sqlite_connection.close()
    return data