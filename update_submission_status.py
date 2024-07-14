import os
import re
from datetime import datetime
from github import Github

# 환경 변수에서 GitHub 토큰 가져오기
GITHUB_TOKEN = os.getenv('MY_GITHUB_TOKEN')
REPO_OWNER = 'konkuk-kuggle'
REPO_NAME = '10th_Study_CS231n'

# GitHub 토큰 값 출력 (디버깅용, 이후 삭제)
print(f"GITHUB_TOKEN: {GITHUB_TOKEN}")

# 참여 인원 목록
participants = ["김동환", "우동협", "장윤영", "정명훈", "진태완", "최종렬", "한서연"]

# 주차별 시작 날짜와 종료 날짜
weeks = {
    1: ('2024-07-08', '2024-07-14'),
    2: ('2024-07-15', '2024-07-21'),
    3: ('2024-07-22', '2024-07-28'),
    4: ('2024-07-29', '2024-08-04'),
    5: ('2024-08-05', '2024-08-11'),
    6: ('2024-08-12', '2024-08-18'),
    7: ('2024-08-19', '2024-08-25'),
    8: ('2024-08-26', '2024-09-01'),
}

# GitHub API 클라이언트 생성
g = Github(GITHUB_TOKEN)
repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")

# PR 제목에서 주차와 참여자 이름 추출하는 함수
def extract_info_from_title(title):
    match = re.match(r"Week_([0-9]+)\ (.*)", title)
    if match:
        week = int(match.group(1))
        name = match.group(2).strip()
        return week, name
    return None, None

# 제출 상태 업데이트 함수
def update_submission_status(week, name):
    print(f"Updating submission status for Week {week}, {name}")
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
    print(f"PR Title: {pr_title}, Created At: {pr_created_at}")

    week, name = extract_info_from_title(pr_title)
    if week and name:
        start_date, end_date = weeks[week]
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date + ' 23:59:59', "%Y-%m-%d %H:%M:%S")

        # PR 생성 시간이 해당 주차의 시작 날짜와 종료 날짜 사이인지 확인
        if start_datetime <= pr_created_at <= end_datetime:
            update_submission_status(week, name)
            print(f"Updated submission status for {name} in Week {week}")
        else:
            print(f"PR was created outside the valid date range for Week {week}")
    else:
        print("PR title format is incorrect")

if __name__ == "__main__":
    handle_pr_event()
