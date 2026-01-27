import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

class NewsParser:
    def __init__(self):
        self.data_file = "data.json"
        
    def get_local_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_local_data(self, data):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # --- ИСТОЧНИК 1: Python.org ---
    def parse_python_org(self):
        print("Сканирую Python.org...")
        url = "https://www.python.org/blogs/"
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            # Ищем конкретно их список новостей
            posts = soup.find('ul', class_='list-recent-posts').find_all('li')
            
            results = []
            for p in posts:
                link = p.find('a')
                results.append({
                    "title": link.text,
                    "category": "Язык Программирование",
                    "content": f"Новость с официального блога Python. Ссылка: {link['href']}",
                    "date": p.find('time').get('datetime')[:10]
                })
            return results
        except:
            print("Ошибка парсинга Python.org")
            return []

    # --- ИСТОЧНИК 2: Hacker News (Программирование) ---
    def parse_hacker_news(self):
        print("Сканирую Hacker News...")
        url = "https://news.ycombinator.com/"
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            # На Hacker News статьи лежат в таблице с классом 'titleline'
            posts = soup.find_all('span', class_='titleline')
            
            results = []
            for p in posts[:15]: # берем первые 15 новостей
                link = p.find('a')
                results.append({
                    "title": link.text,
                    "category": "Новости IT",
                    "content": f"Популярная тема из Hacker News. Ссылка: {link['href']}",
                    "date": datetime.now().strftime("%Y-%m-%d") # HN не всегда дает дату в списке
                })
            return results
        except:
            print("Ошибка парсинга Hacker News")
            return []

    def run_all(self):
        all_new_news = []
        all_new_news.extend(self.parse_python_org())
        all_new_news.extend(self.parse_hacker_news())
        
        current_data = self.get_local_data()
        existing_titles = [e['title'] for e in current_data]
        last_id = max([e['id'] for e in current_data], default=0)
        
        added_count = 0
        for item in all_new_news:
            if item['title'] not in existing_titles:
                last_id += 1
                item['id'] = last_id
                current_data.append(item)
                added_count += 1
        
        self.save_local_data(current_data)
        print(f"Общая работа завершена. Добавлено: {added_count} записей.")

if __name__ == "__main__":
    parser = NewsParser()
    parser.run_all()
