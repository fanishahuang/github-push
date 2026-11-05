import os
import requests
import feedparser

WXPUSHER_APP_TOKEN = os.environ.get("WXPUSHER_APP_TOKEN")
WXPUSHER_UID = os.environ.get("WXPUSHER_UID")

# 选用响应最快的几个稳定源，并采用 requests 获取内容再解析
RSS_FEEDS = {
    "🔥 IT之家": "https://www.ithome.com/rss/",
    "💻 少数派": "https://sspai.com/feed",
    "🚀 36Kr": "https://36kr.com/feed"
}

def fetch_multi_platform_news():
    content_list = []
    
    for source_name, url in RSS_FEEDS.items():
        try:
            print(f"正在获取: {source_name}...")
            # 加上 timeout=5 防卡死
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                items = feed.entries[:2]
                if items:
                    content_list.append(f"<h4>{source_name}</h4>")
                    for entry in items:
                        title = entry.get('title', '无标题')
                        link = entry.get('link', '#')
                        content_list.append(f"• <a href='{link}'>{title}</a><br>")
        except Exception as e:
            print(f"获取 {source_name} 超时或失败: {e}")
            
    return "".join(content_list)

def push_to_wechat(html_content):
    if not WXPUSHER_APP_TOKEN or not WXPUSHER_UID:
        print("错误: 缺少密钥！")
        return

    url = "https://wxpusher.zhengjiecon.cn/api/send/message"
    payload = {
        "appToken": WXPUSHER_APP_TOKEN,
        "content": f"<h3>🌍 科技情报早报</h3><hr>{html_content}",
        "contentType": 2,
        "uids": [WXPUSHER_UID]
    }
    
    response = requests.post(url, json=payload, timeout=5)
    print("推送结果:", response.json())

if __name__ == "__main__":
    news_html = fetch_multi_platform_news()
    if news_html:
        push_to_wechat(news_html)
    else:
        print("没有抓取到任何新内容。")
