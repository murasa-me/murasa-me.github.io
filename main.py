import feedparser
import openai
import json

# ニュースフィードのURL
NEWS_FEED_URLS = [
    "https://news.yahoo.co.jp/rss/topics/domestic.xml",
    "https://news.yahoo.co.jp/rss/topics/science.xml",
    "https://news.yahoo.co.jp/rss/topics/life.xml",
    "https://news.yahoo.co.jp/rss/topics/strange.xml"
]

# フィルター対象のキーワード
NG_KEYWORDS = ["事件", "殺人", "逮捕", "死亡", "政治", "選挙", "戦争", "紛争", "炎上", "トラブル", "不祥事", "事故", "抗議", "犯罪"]

# ChatGPT に渡すプロンプト
def make_prompt(title, summary):
    return f"""
以下のニュース記事タイトルと要約を読んでください。

タイトル: {title}
要約: {summary}

内容が「事件・政治・痛ましい話題」などネガティブなものであれば 'NO'、動物や飲食など穏やかで心温まる内容であれば 'YES' だけを出力してください。
"""

# ChatGPT に問い合わせてフィルタリング
def is_heartwarming(title, summary):
    prompt = make_prompt(title, summary)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        answer = response['choices'][0]['message']['content'].strip().upper()
        return "YES" in answer
    except Exception as e:
        print("Error:", e)
        return False

# ニュース取得＆フィルタリング
def fetch_and_filter_news():
    filtered_news = []

    for url in NEWS_FEED_URLS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.title
            summary = entry.get("summary", "")
            link = entry.link

            if any(ng in title for ng in NG_KEYWORDS):
                continue

            if is_heartwarming(title, summary):
                filtered_news.append({
                    "title": title,
                    "link": link
                })

    with open("filtered_news.json", "w", encoding="utf-8") as f:
        json.dump(filtered_news, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    fetch_and_filter_news()
