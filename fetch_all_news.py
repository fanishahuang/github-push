import os
import feedparser
import requests
from openai import OpenAI

# 1. 从环境变量安全读取密钥
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
WXPUSHER_APP_TOKEN = os.environ.get("WXPUSHER_APP_TOKEN")
WXPUSHER_UID = os.environ.get("WXPUSHER_UID")

# 2. 初始化 DeepSeek 客户端
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# 3. 定义全球无反爬、最高价值的科技与AI资讯源（包含 GitHub、OpenAI、Google、Anthropic、ComfyUI 等）
RSS_SOURCES = {
    "🔥 GitHub Trending": "https://github.trending.rss.workers.dev", # 热门开源项目聚合
    "🤖 OpenAI 官方动态": "https://openai.com/news/rss.xml",
    "🧠 Google AI 实验室": "https://blog.google/technology/ai/rss/",
    "⚡ Anthropic (Claude)": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
    "🎨 ComfyUI 动态": "https://github.com/comfyanonymous/ComfyUI/releases.atom",
    "🚀 Hugging Face 前沿": "https://huggingface.co/blog/feed.xml",
    "💡 Hacker News 头条": "https://news.ycombinator.com/rss"
}

def fetch_all_sources():
    """聚合抓取各大平台的最新动态"""
    all_items = []
    for source_name, url in RSS_SOURCES.items():
        try:
            feed = feedparser.parse(url)
            # 每个源取前 2 条最热内容，保证信息量大而不冗余
            for entry in feed.entries[:2]:
                title = entry.get("title", "无标题")
                link = entry.get("link", "")
                summary = entry.get("summary", entry.get("description", ""))[:400] # 截取摘要
                all_items.append({
                    "source": source_name,
                    "title": title,
                    "link": link,
                    "summary": summary
                })
        except Exception as e:
            print(f"抓取 {source_name} 失败: {e}")
    return all_items

def analyze_with_deepseek(items):
    """让 DeepSeek 批量翻译、去粗取精并解析含金量"""
    if not items:
        return "今日暂无抓取到有效科技资讯。"

    raw_text = ""
    for idx, item in enumerate(items, 1):
        raw_text += f"[{idx}] 来源：{item['source']}\n标题：{item['title']}\n摘要：{item['summary']}\n链接：{item['link']}\n\n"

    prompt = f"""你是一个顶尖的科技与AI行业情报分析专家。请对以下抓取自全球各大前沿平台（GitHub、OpenAI、Google、Anthropic等）的资讯进行深度处理：
1. 逐条进行精准的中文翻译与提炼。
2. 为每一条资讯提供犀利的「💡 含金量与痛点解析」（说明它为什么重要、解决了什么痛点）。
3. 必须保留原始的编号和链接，排版格式为标准的 Markdown，确保每一条都可以通过链接点击查看原文。
4. 语言风格要专业、干练、直击核心，拒绝空洞的官方辞令。

待处理资讯：
{raw_text}"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个精通全球前沿科技与AI生态的硬核情报分析师。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"DeepSeek 解析失败: {e}")
        return "DeepSeek 解析失败，请检查 API Key 或余额。"

def send_to_wxpusher(content):
    """将深度解析后的内容推送到 WxPusher"""
    url = "https://wxpusher.zjiecode.com/api/send/message"
    payload = {
        "appToken": WXPUSHER_APP_TOKEN,
        "content": content,
        "summary": "🌍 全球前沿科技与开源情报速递",
        "contentType": 3,  # 3 代表 Markdown 格式（支持超链接和富文本）
        "uids": [WXPUSHER_UID]
    }
    try:
        res = requests.post(url, json=payload).json()
        print("WxPusher 推送返回结果:", res)
    except Exception as e:
        print(f"WxPusher 发送异常: {e}")

if __name__ == "__main__":
    print("正在开始执行多源科技情报聚合与AI解析任务...")
    items = fetch_all_sources()
    print(f"成功抓取到 {len(items)} 条源资讯，正在调用 DeepSeek 进行深度含金量解析...")
    
    final_markdown = analyze_with_deepseek(items)
    print("正在推送到微信...")
    send_to_wxpusher(final_markdown)
    print("任务执行完毕！")
