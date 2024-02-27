import json
import requests
import os
import subprocess

# JSONファイルを読み込む
with open('corrected_analysis_results.json', 'r') as file:
    comments_list = json.load(file)

# GitHub APIのリクエストボディの形式に変換
github_comments = []
for comment in comments_list:
    github_comment = {
        "path": comment["file_path"],
        "body": comment["comment"],
        "start_line": comment["start_line"],
    }
    if comment["start_line"] != comment["line"]:
        github_comment["line"] = comment["line"]
    else:
        github_comment["line"] = comment["start_line"] + 1
    github_comments.append(github_comment)

commit_id = os.getenv('COMMIT_ID')

# 変換されたコメントリストを含むGitHub APIのリクエストボディ
request_body = {
    "commit_id": commit_id,
    "body": "The commets are generated by ai_tool.",
    "comments": github_comments
}

print(request_body)

# GitHub APIのURLを設定
repo_owner = os.getenv('REPO_OWNER')  # リポジトリのオーナー名
repo_name = os.getenv('REPO_NAME').split('/')[-1]    # リポジトリ名
pull_number = os.getenv('PULL_NUMBER')  # プルリクエスト番号
url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pull_number}/reviews'

# POSTリクエストを送信
headers = {
    'Authorization': f'Bearer {os.getenv("PERSONAL_ACCESS_TOKEN")}',
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28'
}
response = requests.post(url, headers=headers, json=request_body)

# レスポンスを表示
print(response.status_code)
print(response.json())
print(response.request.body)