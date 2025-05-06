import feedparser
import openai
import json
import os
from datetime import datetime

openai.api_key = os.getenv("OPENAI_API_KEY")

def fetch_news(feeds):
    entries = []
    for url in feeds:
        feed = feedparser.parse(url.strip())
        for entry in feed.entries:
            entries.append({
                "title": entry.title,
                "link": entry.link,
                "summary": entry.summary if "summary" in entry else "",
            })
    return entries

def filter_news(entries):
    filtered = []
    for entry in entries:
        prompt = (
            "以下の記事が心温まる内容かを判断してください。"
            "事件・政治・暴力・不幸・不快感を与える内容であれば 'NO'、"
            "動物や飲食など穏やかで心温まる内容であれば 'YES' だけを出力してください。

"
            f"タイトル: {entry['title']}
本文: {entry['summary']}"
        )
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=5,
            )
            decision = response.choices[0].message.content.strip().upper()
            if decision == "YES":
                filtered.append(entry)
        except Exception as e:
            print("OpenAI API error:", e)
    return filtered

def save_to_json(filtered_entries):
    with open("filtered_news.json", "w", encoding="utf-8") as f:
        json.dump(filtered_entries, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    with open("news_sources.txt", "r", encoding="utf-8") as f:
        feeds = f.readlines()
    entries = fetch_news(feeds)
    filtered = filter_news(entries)
    save_to_json(filtered)
