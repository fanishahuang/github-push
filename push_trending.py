import os
import requests
from bs4 import BeautifulSoup

# 1. 抓取 GitHub Trending 榜单
url = 'https://github.com/trending'
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

repos = soup.find_all('article', class_='Box-row', limit=10)
content_list = []

for idx, repo in enumerate(repos, 1):
    title_tag = repo.find('h2')
    if not title_tag:
        continue
    repo_name = "".join(title_tag.text.split())
    repo_url = f"https://github.com/{repo_name}"
    
    desc_tag = repo.find('p', class_='col-9')
    desc = desc_tag.text.strip() if desc_tag else "无描述信息"
    
    content_list.append(f"<b>{idx}. <a href=' '>{repo_name}</a ></b><br/>{desc}<br/>")

html_content = "<h2>🔥 GitHub 今日热门开源项目</h2><hr/>" + "<br/>".join(content_list)

# 2. 调用 WxPusher 推送
app_token = os.environ.get('WXPUSHER_APP_TOKEN')
uid = os.environ.get('WXPUSHER_UID')

push_url = "https://wxpusher.zjiecode.com/api/send/message"
payload = {
    "appToken": app_token,
    "content": html_content,
    "contentType": 2, # HTML格式
    "uids": [uid]
}
res = requests.post(push_url, json=payload)
print("推送结果:", res.json())
