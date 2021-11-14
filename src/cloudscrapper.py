"""cloudscrapper.py BMKG web crawling tool."""
__author__ = "Neek 'Nek0tine' Calvin"
__copyright__ = "Copyright 2021, Cloudscrapper"
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Neek 'Nek0tine' Calvin"
__email__ = "nicholas.juan.kalvin-2020@stmm.unair.ac.id"
__status__ = "Development"

from bs4 import BeautifulSoup
import pandas as pd
import asyncio
import inquirer
import httpx


class cloudscrapper:

    def __init__(self):
        self.bmkg = 'https://www.bmkg.go.id/'

    def _get_cities(self):
        print(f'Requesting to {self.bmkg}')
        _home_page = httpx.get(self.bmkg)

        if _home_page.status_code == 200:
            pass
        else:
            print(f'Request Failed: {_home_page}')

        _home_page_soup = BeautifulSoup((_home_page.text[26715:56509]), 'html.parser')
        _cities_link = _home_page_soup.find_all("a", {"class": "link-block"})
        _cities_link = [f'https://www.bmkg.go.id/{link["href"]}' for link in _cities_link]

        return _cities_link

    def get_weather(self):
        _cities_link = self._get_cities()
        print('Requesting weather forecast for each cities ..')

        async def _get_individual_forecast():
            _htmls = []
            async with httpx.AsyncClient() as client:
                _cities = (client.get(city) for city in _cities_link)
                reqs = await asyncio.gather(*_cities)
            _htmls = [req.text for req in reqs]
            return _htmls

        htmls = asyncio.run(_get_individual_forecast())

        async def _extractor(request):
            r = BeautifulSoup(request, 'html.parser')
            city_name = r.find('title')
            city_name = (" ".join(((str(city_name.text).split('-')[0]).split(' '))[2:]))
            print(f'Extracting {city_name} to {city_name}.csv ')

            table = r.find('div', {'class': 'prakicu-kabkota tab-v1 margin-bottom-30'})
            dates = table.find_all('li')
            date_list = []
            for date in dates:
                date = ((date.text).split(',')[-1]).lstrip()
                date_list.append(date)

            times = r.find_all('h2', {'class': 'kota'})
            times_list = []
            for time in times:
                time = time.text
                times_list.append(time.replace(u'\xa0', u' '))

            conditions = r.find_all('div', {'class': 'kiri'})
            conditions_list = []
            for condition in conditions:
                conditions_list.append((condition.text).strip())

            env_stats = r.find_all('div', {'class': 'kanan'})
            temp_list = []
            humid_list = []
            wind_list = []
            for env_stat in env_stats:
                stats = ((env_stat.text).strip()).split('\n')
                temp_list.append(stats[0])
                humid_list.append(stats[1])
                wind_list.append(((stats[2]).replace(u'\xa0', u' ').split(' ')[0] + ' km/jam'))

            today = pd.DataFrame({'date': date_list[0], 'time': times_list[:-34], 'status': conditions_list[:-34],
                                  'temp': temp_list[:-34], 'humid': humid_list[:-34], 'wind': wind_list[:-34]})
            day2 = pd.DataFrame({'date': date_list[-6], 'time': times_list[-34:-26], 'status': conditions_list[-34:-26],
                                 'temp': temp_list[-34:-26], 'humid': humid_list[-34:-26], 'wind': wind_list[-34:-26]})
            day3 = pd.DataFrame({'date': date_list[-5], 'time': times_list[-26:-18], 'status': conditions_list[-26:-18],
                                 'temp': temp_list[-26:-18], 'humid': humid_list[-26:-18], 'wind': wind_list[-26:-18]})
            day4 = pd.DataFrame({'date': date_list[-4], 'time': times_list[-17:-12], 'status': conditions_list[-17:-12],
                                 'temp': temp_list[-17:-12], 'humid': humid_list[-17:-12], 'wind': wind_list[-17:-12]})
            day5 = pd.DataFrame({'date': date_list[-3], 'time': times_list[-12:-8], 'status': conditions_list[-12:-8],
                                 'temp': temp_list[-12:-8], 'humid': humid_list[-12:-8], 'wind': wind_list[-12:-8]})
            day6 = pd.DataFrame({'date': date_list[-2], 'time': times_list[-8:-4], 'status': conditions_list[-8:-4],
                                 'temp': temp_list[-8:-4], 'humid': humid_list[-8:-4], 'wind': wind_list[-8:-4]})
            day7 = pd.DataFrame(
                {'date': date_list[-1], 'time': times_list[-4:], 'status': conditions_list[-4:], 'temp': temp_list[-4:],
                 'humid': humid_list[-4:], 'wind': wind_list[-4:]})

            forecast = pd.DataFrame()
            forecast = forecast.append([today, day2, day3, day4, day5, day6, day7])

            forecast.to_csv(f'{city_name}.csv', index=False)

        for html in htmls:
            asyncio.run(_extractor(html))


if __name__ == '__main__':
    c = cloudscrapper()
    c.get_weather()