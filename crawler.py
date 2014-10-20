# -*- coding: utf-8 -*-
import re
import requests
from bs4 import BeautifulSoup
import lxml
import csv
import codecs

url = "http://repetitory.freeads.kz/ru-i-classifieds-i-page-i-31-4-i-index.html"

voc = [u'язик',
       u'скому',
       u'цкому',
       u'цкий',
       u'ский',
       u'ского',
       u'цкого',
        ]


from BeautifulSoup import UnicodeDammit
# http://scriptcult.com/subcategory_176/article_852-use-beautifulsoup-unicodedammit-with-lxml-html.html
def decode_html(html_string):
    converted = UnicodeDammit(html_string, isHTML=True)
    if not converted.unicode:
        raise UnicodeDecodeError(
            "Failed to detect encoding, tried [%s]",
            ', '.join(converted.triedEncodings))
    return converted.unicode

def phonify(phone, code = '7'):

    non_decimal = re.compile(r'[^\d]+')
    phone = non_decimal.sub('', phone)
    if len(phone) == 11:
        return "+" + phone
    if len(phone) == 10:
        return "+" + str(code) + phone
    return None

def get_page():
    j = 1
    for i in range(35):
        yield "http://repetitory.freeads.kz/ru-i-classifieds-i-page-i-"+str(i+1)+"-"+str(j)+"-i-index.html"
        if (i + 1) % 10 == 0:
            j += 1

def get_profile_url(base):
    source_code = requests.get(base)
    plain_text = decode_html(source_code.content)
    soup = BeautifulSoup(plain_text)
    for link in soup.findAll('a'):
        href = link.get('href')
        if u'Подробнее' in link.get_text("|", strip=True):
            if u'ru-i-offer' in href:
                yield href

def get_data(item_url):

    source_code = requests.get(item_url)
    plain_text = decode_html(source_code.content)
    soup = BeautifulSoup(plain_text)  # windows-1251

    li = item_url.find('.')

    name = " "
    phone1 = "not found"
    phone2 = "not found"
    subject = "not found"
    languages = False
    city = item_url[7:li]
    if city == 'almaty': city = u'Алматы'
    if city == 'astana': city = u'Астана'
    if city == 'semipalatinsk': city = u'Семипалатинск'


    for offer in soup.findAll('div', {'class':'offerdetail'}):
        subject = offer.h1.get_text("|", strip=True)[0:-13]
    for l in voc:
        if l in subject.lower():
            languages = True
            break
    for boxheader in soup.findAll('div', {'class': 'boxheader'}):
        if u'Контактные' in boxheader.b.string:
            pass
            tb = boxheader.next_sibling.next_sibling.table
            for tr in tb.findAll('tr'):
                a = []
                for i in tr.stripped_strings:
                    a.append(i)
                if u'Имя' in a[0]:
                    name = a[1]
                if u'Контактный телефон' in a[0]:
                    phone1 = a[1]
                if u'Мобильный телефон' in a[0]:
                    phone2 = a[1]


    return name.encode('utf-8'), phone1.encode('utf-8'), phone2.encode('utf-8'), subject.encode('utf-8'), languages, city.encode('utf-8')

f = csv.writer(open("kz3.csv", "wb"))
f.writerow(["name", "phone", "languages", "city", "subject"])

for page in get_page():
    for pu in get_profile_url(page):
        a,b,c,d,e,g = get_data(pu)
        phones = b.split(',') + c.split(',')
        for ph in phones:
            pretty = phonify(ph, '7')
            if pretty:
                f.writerow((a, pretty, e, g, d))
                # print a, pretty, e, g, d

