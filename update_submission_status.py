import os
import re
import requests
from datetime import datetime
from github import Github

# 환경 변수에서 GitHub 토큰 가져오기
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_OWNER = 'forwarder1121'
REPO_NAME = '10th_Study_CS231n'

# 참여 인원 목록
participants = ["김동환", "김명훈", "우동협", "장윤영", "진태완", "최종렬", "한서연"]

# GitHub API 클라이언트 생성
g = Github(GITHUB_TOKEN)
repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")

# PR 제목에서 주차와 참여자 이름 추출하는 함수
def extract_info_from_title(title):
    match = re.match(r"Week_(\d+)\s+(.*)", title)
    if match:
        week = int(match.group(1))
        name = match.group(2).strip()
        return week, name
    return None, None

# 제출 상태 업데이트 함수
def update_submission_status(week, name):
    with open('README.md', 'r') as file:
        lines = file.readlines()

    # 제출 상태를 업데이트할 텍스트 생성
    new_lines = []
    for line in lines:
        if f"| Week {week} |" in line:
            for participant in participants:
                if participant == name and f"| {participant} " in line:
                    line = line.replace(f"| {participant} ", f"|    ✅    | {participant} ")
        new_lines.append(line)

    with open('README.md', 'w') as file:
        file.writelines(new_lines)

# PR 이벤트 처리 함수
def handle_pr_event():
    pr_title = os.getenv('GITHUB_HEAD_REF', '')
    pr_created_at = datetime.strptime(os.getenv('GITHUB_EVENT_PR_CREATED_AT'), "%Y-%m-%dT%H:%M:%SZ")
    pr_cutoff_time = datetime.strptime(f"{pr_created_at.year}-07-08T23:59:00Z", "%Y-%m-%dT%H:%M:%SZ")

    # PR이 기한 내에 생성되었는지 확인
    if pr_created_at <= pr_cutoff_time:
        week, name = extract_info_from_title(pr_title)
        if week and name:
            update_submission_status(week, name)
            print(f"Updated submission status for {name} in Week {week}")
        else:
            print("PR title format is incorrect")
    else:
        print("PR was created after the cutoff time")

if __name__ == "__main__":
    handle_pr_event()
