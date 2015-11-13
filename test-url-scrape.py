import urllib.request

CHARITY_URL = r'http://pmhf3.akaraisin.com/Donation/Event/Home.aspx?seid=11349&mid=8'

with urllib.request.urlopen(CHARITY_URL) as response:
    html = response.read()
print(html)
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, 'lxml')
td = soup.findAll('td', {'class': 'ThermometerAchived', 'align': 'Right'})  # class is spelt wrongly...
achieved_amount = td[0].text  # get just the text
print('[+] Current amount:', achieved_amount)