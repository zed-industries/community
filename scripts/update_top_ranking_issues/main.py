import sys
from datetime import datetime

from github import Github
from pytz import timezone

DATETIME_FORMAT_STRING = "%m/%d/%Y %I:%M %p"


class IssueData:
    def __init__(self, issue):
        self.url = issue.html_url
        self.like_count = sum(1 for reaction in issue.get_reactions() if reaction.content == "+1")
        self.creation_datetime = issue.created_at.strftime(DATETIME_FORMAT_STRING)


def main():
    github_access_token = sys.argv[1]
    github = Github(github_access_token)

    repo_name = "zed-industries/feedback"
    repository = github.get_repo(repo_name)

    label_name_inclusion_set = {
        "defect",
        "documentation",
        "enhancement",
        "polish",
    }
    label_name_to_issue_data_list_dictionary = get_label_name_to_issue_data_list_dictionary(github, repository, label_name_inclusion_set=label_name_inclusion_set)

    top_ranking_issues_body_text = get_top_ranking_issues_body_text(label_name_to_issue_data_list_dictionary)
    top_ranking_issues_issue = repository.get_issue(number=52)
    top_ranking_issues_issue.edit(body=top_ranking_issues_body_text)


def get_label_name_to_issue_data_list_dictionary(github, repository, label_name_inclusion_set={}, max_issues_per_label=5):
    labels = repository.get_labels()
    label_names = [label.name for label in labels if label.name in label_name_inclusion_set]

    label_name_to_issue_data_list_dictionary = {}

    for label_name in label_names:
        query_string = f"repo:{repository.full_name} is:open is:issue label:\"{label_name}\""
        issues = list(github.search_issues(query_string))
        issues = issues[0:max_issues_per_label]

        if issues:
            issue_data_list = [IssueData(issue) for issue in issues]
            issue_data_list.sort(key=lambda issue_data: (issue_data.like_count, issue_data.creation_datetime))
            label_name_to_issue_data_list_dictionary[label_name] = issue_data_list

    # Create a new dictionary with labels ordered by the summation the of likes on the associated issues
    label_names = list(label_name_to_issue_data_list_dictionary.keys())

    label_names.sort(
        key=lambda label_name: sum(
            issue_data.like_count for issue_data in label_name_to_issue_data_list_dictionary[label_name]
        ),
        reverse=True
    )

    return {label_name: label_name_to_issue_data_list_dictionary[label_name] for label_name in label_names}


def get_top_ranking_issues_body_text(label_name_to_issue_data_list_dictionary):
    tz = timezone("america/new_york")
    current_datetime = datetime.now(tz).strftime(f"{DATETIME_FORMAT_STRING} (%Z)")

    highest_ranking_issues_lines = []

    for label, issue_data_list in label_name_to_issue_data_list_dictionary.items():
        highest_ranking_issues_lines.append(f"\n## {label}\n")

        for issue_data in issue_data_list:
            markdown_bullet_point = f"- {issue_data.url} ({issue_data.like_count} :thumbsup:, {issue_data.creation_datetime} :calendar:)"
            highest_ranking_issues_lines.append(markdown_bullet_point)

    top_ranking_issues_text = "\n".join(highest_ranking_issues_lines)

    top_ranking_issues_body_text = f"""
The main purpose of this issue is to provide the data of what testers might need in order to be able to use Zed more.  It should be noted that this issue's existence does not imply that anything will be prioritized differently; the Zed devs likely have their own process for how things are prioritized - this is simply a data set that *can* be used.

**If there are defects / missing features that are slowing you down or preventing you from using Zed, make sure to file issues and vote on them, to bubble them up.  This list becomes more useful the more votes issues get.**

---

*Updated on {current_datetime}*
{top_ranking_issues_text}

---

*For details on how this issue is generated, [see the script](https://github.com/zed-industries/feedback/blob/main/scripts/update_top_ranking_issues/main.py)*
"""

    return top_ranking_issues_body_text


if __name__ == "__main__":
    main()
