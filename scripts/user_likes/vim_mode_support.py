import sys
from datetime import datetime

from github import Github
from pytz import timezone

DATETIME_FORMAT_STRING = "%m/%d/%Y %I:%M %p"


class CommandLineArgumentException(Exception):
    pass


class IssueData:
    def __init__(self, issue):
        self.title = issue.title
        self.url = issue.html_url
        self.like_users = set(
            reaction.user
            for reaction in issue.get_reactions()
            if reaction.content == "+1"
        )
        self.like_count = issue._rawData["reactions"]["+1"]
        self.creation_datetime = issue.created_at.strftime(DATETIME_FORMAT_STRING)
        # TODO: Change script to support storing labels here, rather than directly in the script
        self.labels = set(label["name"] for label in issue._rawData["labels"])


def main():
    if len(sys.argv) < 2:
        raise CommandLineArgumentException("A GitHub access token must be supplied")

    github_access_token = sys.argv[1]
    github = Github(github_access_token)

    repo_name = "zed-industries/community"
    repository = github.get_repo(repo_name)

    query_string = (
        f"repo:{repository.full_name} is:issue is:open label:vim"
    )

    issue_data_list = [IssueData(issue) for issue in github.search_issues(query_string)]

    issue_data_list.sort(key=lambda issue_data: issue_data.like_count, reverse=True)

    for issue_data in issue_data_list:
        print(f"{issue_data.title}: {issue_data.like_count} 👍")

    print("-----------")

    like_sum = sum(issue_data.like_count for issue_data in issue_data_list)
    unique_users = set(
        user for issue_data in issue_data_list for user in issue_data.like_users
    )

    print(f"{len(unique_users)} unique users")
    print(f"{like_sum} 👍")


if __name__ == "__main__":
    start_time = datetime.now()
    main()
    run_duration = datetime.now() - start_time
    print(run_duration)
