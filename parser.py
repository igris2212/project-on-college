import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import time

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

    def get_article_content(self, url):
        """Заходит внутрь статьи и забирает первые 3 абзаца текста"""
        try:
            # Небольшая пауза, чтобы сайт нас не забанил за частые запросы
            time.sleep(1) 
            res = requests.get(url, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # На сайте python.org основной текст статьи обычно в div.article-content или div.p-main
            # Но самый надежный способ - просто собрать все теги <p> внутри основной секции
            content_div = soup.find('div', class_='main-content') or soup.find('section', class_='main-content')
            if not content_div:
                return "Краткое содержание недоступно (не удалось найти блок текста)."
            
            paragraphs = content_div.find_all('p')
            # Берем первые 3 содержательных абзаца
            text_parts = []
            for p in paragraphs:
                text = p.text.strip()
                if len(text) > 40: # Игнорируем слишком короткие строки (даты, подписи)
                    text_parts.append(text)
                if len(text_parts) >= 3: # Лимит: 3 абзаца
                    break
            
            if not text_parts:
                return "Краткое содержание недоступно."
                
            return "\n\n".join(text_parts)
        except Exception as e:
            return f"Не удалось загрузить содержание статьи ({e})."

    # --- ИСТОЧНИК 1: Python.org (Теперь с заходом внутрь) ---
    def parse_python_org(self):
        print("Сканирую Python.org...")
        url = "https://www.python.org/blogs/"
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            posts = soup.find('ul', class_='list-recent-posts').find_all('li')
            
            current_data = self.get_local_data()
            existing_titles = [e['title'] for e in current_data]
            
            results = []
            for p in posts[:5]: # Берем только последние 5 новостей за раз, чтобы не нагружать сайт
                link_tag = p.find('a')
                title = link_tag.text
                article_url = link_tag['href']
                
                # Если такой новости еще нет в базе, заходим внутрь
                if title not in existing_titles:
                    print(f"  -> Захожу в статью: {title}")
                    full_content = self.get_article_content(article_url)
                    
                    results.append({
                        "title": title,
                        "category": "Язык Программирование",
                        "content": f"{full_content}\n\nПолный источник: {article_url}",
                        "date": p.find('time').get('datetime')[:10]
                    })
                else:
                    print(f"  (Пропуск: {title} уже есть)")
            return results
        except:
            print("Ошибка парсинга Python.org")
            return []

    # --- ИСТОЧНИК 2: Hacker News ---
    def parse_hacker_news(self):
        print("Сканирую Hacker News...")
        url = "https://news.ycombinator.com/"
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            lines = soup.find_all('tr', class_='athing')
            
            results = []
            for line in lines[:10]:
                title_line = line.find('span', class_='titleline')
                link_tag = title_line.find('a')
                
                results.append({
                    "title": link_tag.text,
                    "category": "Новости IT",
                    "content": f"Популярное обсуждение на Hacker News.\n\nСсылка на источник: {link_tag['href']}",
                    "date": datetime.now().strftime("%Y-%m-%d")
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
        print(f"Общая работа завершена. Добавлено: {added_count} новых глубоких записей.")

if __name__ == "__main__":
    parser = NewsParser()
    parser.run_all()
