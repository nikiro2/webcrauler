import requests
from bs4 import BeautifulSoup
import os
import csv

def get_page_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.HTTPError as http_err:
        print(f"HTTP error: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

def get_authors(url):
    content = get_page_content(url)
    if content is None:
        return []

    soup = BeautifulSoup(content, 'html.parser')
    links = soup.find_all('a', class_='recomlink')
    return [('https://stihi.ru' + link['href'], link.text) for link in links]

def get_poems(author_url):
    content = get_page_content(author_url)
    if content is None:
        return []

    soup = BeautifulSoup(content, 'html.parser')
    links = soup.find_all('a', class_='poemlink')
    return ['https://stihi.ru' + link['href'] for link in links]

def clean_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename

def save_poem(poem_url, author_folder, session_log):
    content = get_page_content(poem_url)
    if content is None:
        return

    soup = BeautifulSoup(content, 'html.parser')
    title = clean_filename(soup.find('h1').text.strip())
    poem = soup.find('div', class_='text').text.strip()
    file_path = os.path.join(author_folder, f"{title}.txt")
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(poem)
    
    # Запись в текстовый файл журнала
    with open(session_log, 'a', encoding='utf-8') as log_file:
        log_file.write(f"{author_folder},{title},{poem_url}\n")

def web_crawler(start_url, session_log):
    authors = get_authors(start_url)
    if not authors:
        return

    # Загрузка уже скачанных стихов из текстового файла журнала
    downloaded_poems = set()
    if os.path.exists(session_log):
        with open(session_log, 'r', encoding='utf-8') as log_file:
            for line in log_file:
                poem_url = line.strip().split(',')[-1]
                downloaded_poems.add(poem_url)

    for author_url, author_name in authors:
        author_folder = os.path.join('Authors', author_name)
        os.makedirs(author_folder, exist_ok=True)

        poems = get_poems(author_url)
        for poem_url in poems:
            if poem_url not in downloaded_poems:
                save_poem(poem_url, author_folder, session_log)

session_log = 'session_log.txt'
start_url = 'https://stihi.ru/authors/editor.html?year=2023&month=11&day=8'
web_crawler(start_url, session_log)

