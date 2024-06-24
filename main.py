import requests
from bs4 import BeautifulSoup
import re
import os


def save_data(country, domain, data):
    os.makedirs(os.path.join(country, domain), exist_ok=True)
    file_path = os.path.join(country, domain, 'rental_object.json')

    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f"{data}\n")


def extract_numbers(text):
    numbers = re.findall(r'\d+', text)
    if len(numbers) >= 2:
        return int(numbers[2]) // int(numbers[1]) + 1
    return None


def get_beautiful_soup_item():
    url = 'https://kelm-immobilien.de/immobilien'

    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')
    page = soup.find(class_='num-posts col-xs-12 col-sm-5').text
    num_page = extract_numbers(page)
    url += f'/page/{str(num_page)}/'
    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')

    return soup


def all_url():
    url_list = []
    soup = get_beautiful_soup_item()
    container = soup.find_all('div', class_='property-container')
    for item in container:
        url_list.append(item.a['href'])

    return url_list


def scrap_page():
    data = []
    for page in all_url():
        details = {}
        response = requests.get(page)
        soup = BeautifulSoup(response.text, 'html.parser')
        # images = soup.find_all('div', id='immomakler-galleria')
        # images = soup.find_all('a', href=True, attrs={'rel': 'nofollow'})
        images = soup.find_all('img', class_='nolazyload disable-lazyload skip-lazy')
        title = soup.find('title').text
        img_list = [img['data-big'] for img in images]
        price = soup.find('li', class_='list-group-item data-kaufpreis')
        if price:
            price = price.find('div', class_='dd col-sm-7')
            if price:
                price = price.text
                price = float(price.replace("EUR", "").replace("\u202f", "").replace(".", ""))
        status_1 = soup.find('li', class_='list-group-item data-verfuegbar_ab')
        if status_1:
            status_1 = status_1.find('div', class_='dt col-sm-5')
        status_2 = soup.find('li', class_='list-group-item data-verfuegbar_ab')
        if status_2:
            status_2 = status_2.find('div', class_='dd col-sm-7')
        if status_1 and status_2:
            status = status_1.text + ' ' + status_2.text
        else:
            status = None

        outer_container = soup.find_all('div', class_='panel-body')
        result = [div for div in outer_container if div.find('h3') and div.find('p')]
        description = ''
        for text in result:
           description = description + text.text

        phone = soup.find('div', class_='dd col-sm-7 p-tel value')
        if phone:
            phone = phone.text
        else:
            phone = None

        mail = soup.find('div', class_='dd col-sm-7 u-email value')
        if mail:
            mail = mail.text
        else:
            mail = None
        data.append(
            {
                'url': page,
                'title': title,
                'status': status,
                'picture': img_list,
                'buy_price': price,
                'description': description,
                'phone_number': phone,
                'email': mail,
            }
        )

    save_data('Germany', 'kelm-immobilien.de', data)


if __name__ == "__main__":
    scrap_page()

