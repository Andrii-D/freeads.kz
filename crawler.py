# -*- coding: utf-8 -*-
import re
import requests
from bs4 import BeautifulSoup
import lxml
import csv
import codecs

host = 'http://www.znania.ru'
url = host + "/rep_sites/rep_sel.asp"
patt1 = r'http://www\.znania\.ru/rep_sites/rep\.asp\?type=[\w]'
patt2 = r'http://www\.znania\.ru/rep_sites/repxx\.asp\?id=[\w]'

def gather_subjects(base, pattern):
    p = re.compile(pattern)
    source_code = requests.get(base)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, 'lxml', from_encoding='windows-1251')  # windows-1251
    for link in soup.findAll('a'):
        href = host + str(link.get('href'))
        if p.match(href):
            yield href

def gather_urls(base, pattern):
    p = re.compile(pattern)
    source_code = requests.get(base)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text)
    for link in soup.findAll('a'):
        href = host + "/rep_sites/" + link.get('href')
        if p.match(href):
            yield href

def get_data(item_url):
    source_code = requests.get(item_url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, 'lxml', from_encoding='cp1251')  # windows-1251
    name = "not found"
    email = "not found"
    phone = "not found"
    subject = "not found"
    for bc in soup.findAll('a', {'class': 'breadcrumps'}):
        if 'rep.asp?type=' in bc['href']:
            subject = bc.string
            break
    for span in soup.findAll('span', {'class': 'txt2'}):
        if 'E-mail' in span.b.string:
            email = span.b.next_sibling.next_sibling.string
        if "." in span.b.string:
            phone = span.b.next_sibling.string

    for d in soup.findAll('p', {'align': 'justify'}):
        name =  d.contents[-1]
        break

    yield name.encode('utf-8'), email.encode('utf-8'), phone.encode('utf-8'), subject.encode('utf-8')


f = csv.writer(open("znania_ru.csv", "wb"))
f.writerow(["name", "email", "phone", "subject"])

for s in gather_subjects(url, patt1):
    for u in gather_urls(s, patt2):
        for (a, b, c, d) in get_data(u):
            f.writerow((a, b, c, d))




