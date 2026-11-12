import os
import requests
import feedparser

def fetch_news():
    print("=== 开始抓取各平台自动化资讯 ===")
    news_html = "<h3>🌍 全球 AI 与前沿科技雷达</h3><br>"
    
    # 1. 抓取 OpenAI & Claude 官方更新日志 (通过官方 RSS)
    ai_sources = {
        "OpenAI 官方动态": "https://openai.com/news/rss.xml",
        "Anthropic (Claude) 博客": "https://www.anthropic.com/rss.xml"
    }
    
    for name, url in ai_sources.items():
        try:
            feed = feedparser.parse(url)
            news_html += f"<h4>📌 {name}</h4><ul>"
            for entry in feed.entries[:2]:  # 每个源取最新 2 条
                news_html += f"<li><a href='{entry.link}'>{entry.title}</a></li>"
            news_html += "</ul>"
        except Exception as e:
            news_html += f"<p>{name} 抓取异常: {e}</p>"

    # 2. 抓取 Google 资讯 (以 AI 与前沿科技为例)
    try:
        g_url = "https://news.google.com/rss/search?q=AI+technology+OR+OpenAI+OR+Claude&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(g_url)
        news_html += "<h4>🔍 Google 科技精选</h4><ul>"
        for entry in feed.entries[:3]:  # 取最新 3 条
            news_html += f"<li><a href='{entry.link}'>{entry.title}</a></li>"
        news_html += "</ul>"
    except Exception as e:
        news_html += f"<p>Google 资讯抓取异常: {e}</p>"

    # 3. 抓取 Reddit 热门讨论 (以 r/technology 和 r/LocalLLaMA 为例)
    reddit_subs = ["technology", "LocalLLaMA"]
    for sub in reddit_subs:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            r_url = f"https://www.reddit.com/r/{sub}/hot.json?limit=3"
            r_res = requests.get(r_url, headers=headers, timeout=10)
            if r_res.status_code == 200:
                posts = r_res.json()['data']['children']
                news_html += f"<h4>🔥 Reddit (r/{sub}) 热门</h4><ul>"
                for post in posts:
                    title = post['data']['title']
                    permalink = "https://www.reddit.com" + post['data']['permalink']
                    news_html += f"<li><a href='{permalink}'>{title}</a></li>"
                news_html += "</ul>"
        except Exception as e:
            news_html += f"<p>Reddit r/{sub} 抓取异常: {e}</p>"

    # 4. 通过 RSSHub 接入其他社媒/平台 (如 X 某个特定账号或平台标签)
    # 注：如果你部署了自己的 RSSHub 实例，可以把下面的 https://rsshub.app 换成你自己的域名
    rsshub_sources = {
        "X (Twitter) 热门趋势": "https://rsshub.app/twitter/trending/it" 
    }
    
    for name, url in rsshub_sources.items():
        try:
            feed = feedparser.parse(url)
            news_html += f"<h4>🐦 {name}</h4><ul>"
            for entry in feed.entries[:2]:
                news_html += f"<li><a href='{entry.link}'>{entry.title}</a></li>"
            news_html += "</ul>"
        except Exception as e:
            news_html += f"<p>{name} 抓取异常（可能需检查RSSHub实例）: {e}</p>"

    print("=== 新闻抓取完毕 ===")
    return news_html

def push_to_wechat(news_html):
    """
    通过 WxPusher 将聚合后的 HTML 资讯推送到微信
    """
    url = "https://wxpusher.zjiecode.com/api/send/message"
    
    payload = {
        "appToken": os.environ.get("WXPUSHER_APP_TOKEN", ""),
        "content": news_html,
        "contentType": 2,  # 2 表示 HTML 格式
        "uids": [os.environ.get("WXPUSHER_UID", "")]
    }
    
    try:
        print("正在通过 WxPusher 推送消息到微信...")
        response = requests.post(url, json=payload, timeout=15)
        print("微信接口返回结果:", response.json())
    except Exception as e:
        print(f"[警告] 微信推送网络请求失败: {e}")

if __name__ == "__main__":
    html_content = fetch_news()
    push_to_wechat(html_content)
