import os
import requests
from openai import OpenAI

# 1. 从刚才配置的 GitHub Secrets 环境变量中安全读取密钥
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
WXPUSHER_APP_TOKEN = os.environ.get("WXPUSHER_APP_TOKEN")
WXPUSHER_UID = os.environ.get("WXPUSHER_UID")

# 2. 初始化 DeepSeek 客户端
client = OpenAI(
    api_key=DEEPSEEK_API_KEY, 
    base_url="https://api.deepseek.com"
)

# 3. 定义 AI 提炼函数：让 AI 把英文/硬核内容翻译并降维成大白话
def analyze_with_ai(title, raw_text):
    prompt = (
        f"标题: {title}\n"
        f"内容: {raw_text}\n\n"
        "请忽略专业黑话与文化差异，用通俗易懂的中文总结这段内容的核心亮点、"
        "解决了什么痛点，以及对普通人有什么用，控制在150字以内："
    )
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个擅长把硬核科技翻译成大白话的科技主编。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI 分析失败，请直接查看原文。（错误：{e}）"

# 4. 定义 WxPusher 推送函数：把整理好的结果发到你的手机微信
def send_to_wxpusher(title, ai_summary, source_url):
    wx_url = "https://wxpusher.zjiecode.com/api/send/message"
    
    content = (
        f"### 💡 核心大白话解读\n"
        f"{ai_summary}\n\n"
        f"---\n"
        f"🔗 [点击查看英文原文/项目主页]({source_url})"
    )
    
    payload = {
        "appToken": WXPUSHER_APP_TOKEN,
        "content": content,
        "summary": f"【科技速递】{title}",
        "contentType": 3,  # 3 代表 Markdown 格式
        "uids": [WXPUSHER_UID]
    }
    
    res = requests.post(wx_url, json=payload).json()
    return res

# 5. 主执行逻辑
if __name__ == "__main__":
    print("正在开始执行自动化任务...")
    
    # 示例数据（你后续可以把它替换为你从网页或 RSS 抓取到的真实英文内容）
    news_title = "GitHub Trending: AI Agent Framework"
    news_content = (
        "A new lightweight framework designed to orchestrate multiple LLM agents "
        "for autonomous workflow execution without complex configuration."
    )
    news_url = "https://github.com"

    # 第一步：交由 DeepSeek 大模型提炼
    print("正在呼叫 AI 进行通俗化解读...")
    summary = analyze_with_ai(news_title, news_content)
    
    # 第二步：通过 WxPusher 推送到手机微信
    print("正在推送到微信...")
    result = send_to_wxpusher(news_title, summary, news_url)
    print("推送返回结果：", result)
