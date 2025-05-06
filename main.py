import os
import requests
from bs4 import BeautifulSoup
import openai
import json
from urllib.parse import urljoin

# ニュースサイトURL
NEWS_URL = "https://news.yahoo.co.jp/topics"

# OpenAI APIキー（GitHub ActionsではSecretsに設定する）
openai.api_key = os.getenv("OPENAI_API_KEY")

def fetch_news():
    res = requests.get(NEWS_URL)
    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select("li a")  # 適宜変更

    news_list = []
    for item in items:
        title = item.get_text().strip()
        link = urljoin(NEWS_URL, item.get("href"))
        if title:
            news_list.append({
                "title": title,
                "link": link
            })
    return news_list

def is_heartwarming(title):
    prompt = (
        "次のニュースのタイトルは心温まる話題（動物、グルメ、前向きな内容など）ですか？\n"
        "YES または NO で答えてください。\n"
        f"タイトル: {title}"
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    answer = response.choices[0].message.content.strip().upper()
    return "YES" in answer

def filter_news(news_list):
    filtered = []
    for news in news_list:
        try:
            if is_heartwarming(news["title"]):
                filtered.append(news)
        except Exception as e:
            print(f"Error filtering: {e}")
    return filtered

def save_json(data, filename="filtered_news.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    news = fetch_news()
    print(f"取得したニュース数: {len(news)} 件")
    filtered = filter_news(news)
    print(f"フィルター通過数: {len(filtered)} 件")
    save_json(filtered)
