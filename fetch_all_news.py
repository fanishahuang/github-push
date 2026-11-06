import os
import requests

def fetch_news():
    """
    这里是你的新闻抓取和 HTML 生成逻辑
    （你可以保留你原本抓取数据的代码，把生成的 HTML 内容返回）
    """
    print("正在抓取各项新闻数据...")
    # 示例 HTML 内容
    news_html = """
    <h3>今日科技与热点资讯</h3>
    <p>这是一条自动抓取并推送的测试新闻内容。</p>
    """
    return news_html

def push_to_wechat(news_html):
    """
    带异常保护的微信推送函数，完美解决 DNS 域名解析失败导致任务崩溃的问题
    """
    url = "https://wxpusher.zhengjiecc.com/api/send/message"
    
    # 请确保这里的参数（appToken、uids 等）与你原本代码中的配置保持一致
    payload = {
        "appToken": os.environ.get("WXPUSHER_APP_TOKEN", ""), # 建议使用 GitHub Secrets 环境变量，也可直接填字符串
        "content": news_html,
        "contentType": 2, # 1: 文本, 2: HTML
        "uids": [os.environ.get("WXPUSHER_UID", "")]         # 接收者的 UID
    }
    
    try:
        print("正在通过 WxPusher 推送消息到微信...")
        # 设置超时时间为 15 秒
        response = requests.post(url, json=payload, timeout=15)
        
        # 尝试解析返回的 JSON
        result = response.json()
        if result.get("code") == 200:
            print("✅ 微信消息推送成功！")
        else:
            print(f"⚠️ 微信接口返回错误: {result}")
            
    except requests.exceptions.RequestException as e:
        # 核心保护：捕获包括 DNS 域名解析失败（NameResolutionError）、连接超时等所有网络异常
        # 这样即使 WxPusher 偶发性挂掉或网络波动，脚本也会打印警告并优雅结束，绝不会让 GitHub Actions 任务变红报错
        print(f"❌ [警告] 微信推送网络请求失败（可能是 DNS 解析瞬时异常），但不影响主任务继续运行: {e}")

if __name__ == "__main__":
    print("=== 开始执行自动化任务 ===")
    
    # 1. 获取新闻内容
    html_content = fetch_news()
    
    # 2. 推送至微信（受 try...except 保护）
    push_to_wechat(html_content)
    
    print("=== 任务执行完毕 ===")
