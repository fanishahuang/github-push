import os
import feedparser
import requests
from bs4 import BeautifulSoup
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

# 3. 定义全球无反爬、高价值科技与AI资讯源
RSS_SOURCES = {
    "🔥 GitHub Trending": "https://github.trending.rss.workers.dev",
    "🤖 OpenAI 官方动态": "https://openai.com/news/rss.xml",
    "🧠 Google AI 实验室": "https://blog.google/technology/ai/rss/",
    "⚡ Anthropic (Claude)": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
    "🎨 ComfyUI 动态": "https://github.com/comfyanonymous/ComfyUI/releases.atom",
    "🚀 Hugging Face 前沿": "https://huggingface.co/blog/feed.xml",
    "💡 Hacker News 头条": "https://news.ycombinator.com/rss"
}

def clean_html(raw_html):
    """清理 HTML 标签，提取纯英文文本"""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return " ".join(text.split())

def fetch_article_snippet(url):
    """尝试深入抓取网页正文的前几段英文，增加可学习的英文信息量"""
    if not url or "github.com" in url or "news.ycombinator.com" in url:
        return ""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=8)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 60]
            return " ".join(paragraphs[:3])[:600]
    except Exception:
        pass
    return ""

def fetch_all_sources():
    """聚合抓取各大平台的最新动态"""
    all_items = []
    for source_name, url in RSS_SOURCES.items():
        try:
            feed = feedparser.parse(url)
            # 【已升级】每个源从 2 条提升到 3 条，让资讯更丰富
            for entry in feed.entries[:3]:
                title = entry.get("title", "No Title")
                link = entry.get("link", "")
                raw_summary = entry.get("summary", entry.get("description", ""))
                clean_summary = clean_html(raw_summary)[:500]

                # 如果 RSS 自带的摘要太短，尝试进入原文链接抓取正文前几段
                if len(clean_summary) < 120:
                    extra_text = fetch_article_snippet(link)
                    if extra_text:
                        clean_summary = extra_text

                all_items.append({
                    "source": source_name,
                    "title": title,
                    "link": link,
                    "summary": clean_summary if clean_summary else title
                })
        except Exception as e:
            print(f"抓取 {source_name} 失败: {e}")
    return all_items

def analyze_with_deepseek(items):
    """让 DeepSeek 按照『沉浸式句对句双语对照』格式处理并解析含金量"""
    if not items:
        return "今日暂无抓取到有效科技资讯。"

    raw_text = ""
    for idx, item in enumerate(items, 1):
        raw_text += f"[{idx}] 来源：{item['source']}\n英文标题：{item['title']}\n英文正文摘要：{item['summary']}\n链接：{item['link']}\n\n"

    prompt = f"""你是一个顶尖的科技情报专家，同时也是精通双语对照的英语教育专家。
请对以下抓取自全球前沿平台的资讯进行深度处理，并严格按照以下『永久稳定、无需点开链接即可直接阅读』的沉浸式双语对照格式输出：

对于每一条资讯，请严格按以下结构输出：
### [编号] 来源分类
**双语标题：**
英文原版标题
*中文精准翻译*

**沉浸式双语精读正文：**
（请将该文章的核心摘要提炼并拆分为 2~4 个关键英文句子。必须严格采用“句对句”对照排版：每一句英文原句单独成行，紧接着下一行用斜体写出精准的中文翻译，形成完美的双语交替，绝对不要把中英文混在同一段里！）

**💡 含金量与痛点解析：**
用犀利、干练的中文总结这条资讯为什么重要、解决了什么痛点（控制在 2~3 句话）。

**🔗 原始直达：** [查看英文原文](链接)

---

待处理资讯：
{raw_text}"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a top-tier tech intelligence analyst and bilingual English-Chinese reading coach."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"DeepSeek 解析失败: {e}")
        return f"DeepSeek 解析失败: {e}"

def send_to_wxpusher(content):
    """将双语解析内容推送到 WxPusher"""
    url = "https://wxpusher.zjiecode.com/api/send/message"
    payload = {
        "appToken": WXPUSHER_APP_TOKEN,
        "content": content,
        "summary": "🌍 全球前沿科技双语精读与情报速递",
        "contentType": 3,  # 3 代表 Markdown 格式
        "uids": [WXPUSHER_UID]
    }
    try:
        res = requests.post(url, json=payload).json()
        print("WxPusher 推送返回结果:", res)
    except Exception as e:
        print(f"WxPusher 发送异常: {e}")

if __name__ == "__main__":
    print("正在开始执行多源科技情报聚合与双语解析任务...")
    items = fetch_all_sources()
    print(f"成功抓取到 {len(items)} 条源资讯，正在调用 DeepSeek 进行沉浸式句对句双语处理...")
    
    final_markdown = analyze_with_deepseek(items)
    print("正在推送到微信...")
    send_to_wxpusher(final_markdown)
    print("任务执行完毕！")
