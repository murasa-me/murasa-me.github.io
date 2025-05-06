import os
import requests
from bs4 import BeautifulSoup
import openai
import json
from urllib.parse import urljoin

# ニュースサイトURL
NEWS_URL = "https://news.yahoo.co.jp/topics"
LOG_FILE = "filter_log.txt"

# OpenAI APIキー（GitHub Secretsから）
openai.api_key = os.getenv("OPENAI_API_KEY")

def log(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

def fetch_news():
    res = requests.get(NEWS_URL)
    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select("a.sc-fasEvo.fLbcQi")  # Yahoo!の構造に応じて修正が必要かも

    news_list = []
    for item in items:
        title = item.get_text().strip()
        link = urljoin(NEWS_URL, item.get("href"))
        if title and link:
            news_list.append({
                "title": title,
                "link": link
            })
    return news_list

def is_heartwarming(news_item):
    prompt = (
        "次のニュースのタイトルは心温まる話題（動物、グルメ、前向きな内容など）ですか？\n"
        "YES または NO で答えてください。\n"
        f"タイトル: {news_item['title']}"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message.content.strip().upper()
        result = "YES" if "YES" in answer else "NO"
    except Exception as e:
        result = f"ERROR: {str(e)}"
    log(f"[{result}] {news_item['title']} ({news_item['link']})")
    return result == "YES"

def filter_news(news_list):
    filtered = []
    for news in news_list:
        if is_heartwarming(news):
            filtered.append(news)
    return filtered

def save_json(data, filename="filtered_news.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def clear_log():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("=== News Filter Log ===\n")

if __name__ == "__main__":
    clear_log()
    news = fetch_news()
    log(f"\n取得件数: {len(news)} 件")
    filtered = filter_news(news)
    log(f"フィルター通過件数: {len(filtered)} 件")
    save_json(filtered)
