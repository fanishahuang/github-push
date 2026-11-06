import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def push_to_wechat(news_html):
    url = "https://wxpusher.zhengjiecc.com/api/send/message"
    
    # 构造请求体参数（请根据你原本的代码填写实际的 appToken、uids 等内容）
    payload = {
        # "appToken": "你的appToken",
        # "content": news_html,
        # "contentType": 2, # 1: 文本, 2: html
        # "uids": ["你的uid"]
    }
    
    # 配置带有重试机制的 session（应对偶发网络抖动、DNS瞬时解析失败）
    session = requests.Session()
    retries = Retry(
        total=3,          # 最多重试 3 次
        backoff_factor=2, # 每次重试等待时间（秒）
        status_forcelist=[500, 502, 503, 504],
        raise_on_status=False
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.mount("http://", HTTPAdapter(max_retries=retries))

    try:
        # 设置超时时间为 15 秒
        response = session.post(url, json=payload, timeout=15)
        
        # 尝试解析返回的 JSON
        try:
            result = response.json()
            if result.get("code") == 200:
                print("✅ 微信消息推送成功！")
            else:
                print(f"⚠️ 微信接口返回错误: {result}")
        except ValueError:
            print(f"⚠️ 微信接口响应非 JSON 格式: {response.text}")
            
    except requests.exceptions.RequestException as e:
        # 即使发生 DNS 解析失败、连接超时等严重网络异常，也只会打印警告，不会导致整个脚本异常退出 (exit code 1)
        print(f"❌ [警告] 微信推送网络请求失败（可能是 DNS 解析瞬时异常），但不影响主任务继续运行: {e}")

if __name__ == "__main__":
    # 你的主流程代码
    news_html = "<p>测试新闻内容</p>"
    push_to_wechat(news_html)
