import os
import re
from datetime import datetime
from github import Github

# 환경 변수에서 GitHub 토큰 가져오기
GITHUB_TOKEN = os.getenv('MY_GITHUB_TOKEN')
REPO_OWNER = 'your_repo_owner'  # 리포지토리 소유자 이름으로 바꾸세요
REPO_NAME = 'your_repo_name'    # 리포지토리 이름으로 바꾸세요

# 참여 인원 목록
participants = ["김동환", "우동협", "장윤영", "정명훈", "진태완", "최종렬", "한서연"]

# GitHub API 클라이언트 생성
g = Github(GITHUB_TOKEN)
repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")

# PR 제목에서 주차와 참여자 이름 추출하는 함수
def extract_info_from_title(title):
    match = re.match(r"Week_([0-9]+)\s+(.*)", title)
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
                if participant == name:
                    line = line.replace(f"|          |", f"|    ✅    |", 1)
        new_lines.append(line)

    with open('README.md', 'w') as file:
        file.writelines(new_lines)

    # README.md 파일 커밋 및 푸시
    contents = repo.get_contents("README.md")
    repo.update_file(contents.path, f"Update submission status for Week {week}, {name}", ''.join(new_lines), contents.sha)

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
