import requests

class Region():

    def __init__(self, code, date):
        self.code = code
        self.date = date
        self.data = self.get_data()

        self.cases = self.data['cases']
        self.cumulative_cases = self.data['cumulative_cases']
        self.cumulative_deaths = self.data['cumulative_deaths']
        self.date = self.data['date']
        self.deaths = self.data['deaths']
        self.health_region = self.data['health_region']
        self.province = self.data['province']

    def get_data(self):
        # Gets dictionary of data for code region
        url = f"https://api.opencovid.ca/summary?loc={self.code}&date={self.date}"
        r = requests.get(url)
        data = r.json()['summary']
        clean_data = self.clean_data(data)
        return clean_data

    def clean_data(self, data):
    # Turns list of dictionaries into single dictionary
    # Need to verify province becuase of API errors
        temp = data.copy()
        for item in temp:
            if item['province'] != "Alberta":
                data.remove(item)
        return data[0]