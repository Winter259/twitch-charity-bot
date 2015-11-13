import urllib.request

CHARITY_URL = r'http://pmhf3.akaraisin.com/Donation/Event/Home.aspx?seid=11349&mid=8'

request = urllib.request.Request(
    CHARITY_URL,
    data=None,
    headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
)

f = urllib.request.urlopen(request)
html = f.read().decode('utf-8')
print(html)
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, 'lxml')
td = soup.findAll('td', {'class': 'ThermometerAchived', 'align': 'Right'})  # class is spelt wrongly...
achieved_amount = td[0].text  # get just the text
print('[+] Current amount:', achieved_amount)