# Canada-Covid

Description:

This project gathers covid information from a large dataset to get province-specific
info for all of Canada. The data is pulled from online, parsed, and placed in a SQLite database.
Each table for each province shows different types of data:

    active: cumulative cases, cumulative recoveries, cumulative deaths, active cases, active cases change
    cases: daily cases, cumulative cases
    mortality: deaths, cumulative deaths
    recovered: daily recoveries, cumulative recoveries
    testing: daily testing, cumulative testing, testing info

I chose to keep the tables in this project separate to keep the data uncluttered. The end goal for this project
was to create visualizations of the data that are accurate and easy to read. Becuase of the large database, there is plenty
of information available for all kinds of representations.

Files:

    covid_canada.py -> python code
    covid_canada.db -> sample database

Run Instructions (Command Line):

    python3 covid_canada.py

Libraries:

    pandas
    matplotlib
    sqlalchemy
    sqlite3

Data Sources:

    https://github.com/ishaberry/Covid19Canada
