import os
import json
import openai
import feedparser

LOG_FILE = "filter_log.txt"
OUTPUT_FILE = "filtered_news.json"

# OpenAI APIキー
openai.api_key = os.getenv("OPENAI_API_KEY")

# 利用するRSSフィード（今後ここに増やせます）
RSS_FEEDS = [
    "https://www.fashion-press.net/news/headline/rss",  # ファッション系
    "https://www.cafeglobe.com/rss/index.xml",          # ライフスタイル系
    "https://gigazine.net/news/rss_2.0/",               # テック・食なども含む
    "https://www.excite.co.jp/feed/news/bit/bit.xml",   # 面白系
    "https://news.yahoo.co.jp/rss/topics/novel.xml"     # やや前向きな話題が多い
]

def log(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

def clear_log():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("=== News Filter Log ===\n\n")

def fetch_rss_news():
    news_list = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            if title and link:
                news_list.append({"title": title, "link": link})
    return news_list

def is_heartwarming(news_item):
    prompt = (
        "次のニュースのタイトルは、心温まる話題（動物、グルメ、生活の癒しなど）ですか？"
        "事件、政治、災害、差別、戦争などに関係するなら NO を答えてください。\n"
        f"タイトル: {news_item['title']}\n"
        "回答は YES または NO のみ。"
    )
    try:
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = res.choices[0].message.content.strip().upper()
        result = "YES" if "YES" in answer else "NO"
    except Exception as e:
        result = f"ERROR: {str(e)}"
    log(f"[{result}] {news_item['title']} ({news_item['link']})")
    return result == "YES"

def filter_news(news_list):
    return [news for news in news_list if is_heartwarming(news)]

def save_json(data):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    clear_log()
    news = fetch_rss_news()
    log(f"取得件数: {len(news)} 件")
    filtered = filter_news(news)
    log(f"フィルター通過件数: {len(filtered)} 件")
    save_json(filtered)
