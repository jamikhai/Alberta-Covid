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
was to create visualizations of conclusions pulled from data that are accurate and easy to read. Because of the large database, there is plenty of information available for all kinds of representations and inferences.

Files:

    covid_canada.py -> main
    graphs.py -> functions for graphing and pulling data
    covid_canada.db - > sample database

Run Instructions (Command Line):

    python3 covid_canada.py

    If running for the first time (or first time that day), select 'y' to update database (covid_canada.db). If not downloaded, it will create one

Libraries:

    pandas
    matplotlib
    sqlalchemy
    sqlite3

Data Sources:

    https://github.com/ishaberry/Covid19Canada
    https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1710000901
