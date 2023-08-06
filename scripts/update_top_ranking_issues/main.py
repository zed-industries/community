import os
import sys
from collections import defaultdict
from datetime import datetime

from github import Github
from pytz import timezone

DATETIME_FORMAT_STRING = "%m/%d/%Y %I:%M %p"
CORE_LABEL_NAMES_LIST = [
    "defect",
    "design",
    "documentation",
    "enhancement",
    "panic / crash",
]
CORE_LABEL_NAMES_SET = set(CORE_LABEL_NAMES_LIST)
IGNORED_LABEL_NAMES_LIST = [
    "meta",
    "linux",
    "web",
    "windows",
]
IGNORED_LABEL_NAMES_SET = set(IGNORED_LABEL_NAMES_LIST)
ISSUES_PER_LABEL = 20


class CommandLineArgumentException(Exception):
    pass


class IssueData:
    def __init__(self, issue):
        self.url = issue.html_url
        self.like_count = issue._rawData["reactions"]["+1"]
        self.creation_datetime = issue.created_at.strftime(DATETIME_FORMAT_STRING)
        # TODO: Change script to support storing labels here, rather than directly in the script
        self.labels = set(label["name"] for label in issue._rawData["labels"])


def main():
    github_access_token = os.getenv("GITHUB_TOKEN")

    if not github_access_token:
        raise CommandLineArgumentException(
            'A GitHub access token must be provided in the env as: "GITHUB_TOKEN"'
        )

    prod_mode = False

    if len(sys.argv) == 2:
        prod_mode_text = "prod_mode"

        if sys.argv[1] == prod_mode_text:
            prod_mode = True
        else:
            raise CommandLineArgumentException(
                f'If first argument is supplied, it must be "{prod_mode_text}"'
            )

    github = Github(github_access_token)

    repo_name = "zed-industries/community"
    repository = github.get_repo(repo_name)

    (
        label_name_to_issue_data_list_map,
        error_message_to_erroneous_issue_data_list_map,
    ) = get_issue_maps(github, repository)

    issue_text = get_issue_text(
        label_name_to_issue_data_list_map,
        error_message_to_erroneous_issue_data_list_map,
    )

    if prod_mode:
        top_ranking_issues_issue = repository.get_issue(number=52)
        top_ranking_issues_issue.edit(body=issue_text)
    else:
        print(issue_text)

    remaining_requests, max_requests = github.rate_limiting
    print(f"Remaining requests: {remaining_requests}")


def get_issue_maps(github, repository):
    label_name_to_issue_list_map = get_label_name_to_issue_list_map(github, repository)
    label_name_to_issue_data_list_map = get_label_name_to_issue_data_list_map(
        label_name_to_issue_list_map
    )

    error_message_to_erroneous_issue_list_map = (
        get_error_message_to_erroneous_issue_list_map(github, repository)
    )
    error_message_to_erroneous_issue_data_list_map = (
        get_error_message_to_erroneous_issue_data_list_map(
            error_message_to_erroneous_issue_list_map
        )
    )

    # Create a new dictionary with labels ordered by the summation the of likes on the associated issues
    label_names = list(label_name_to_issue_data_list_map.keys())

    label_names.sort(
        key=lambda label_name: sum(
            issue_data.like_count
            for issue_data in label_name_to_issue_data_list_map[label_name]
        ),
        reverse=True,
    )

    label_name_to_issue_data_list_map = {
        label_name: label_name_to_issue_data_list_map[label_name]
        for label_name in label_names
    }

    return (
        label_name_to_issue_data_list_map,
        error_message_to_erroneous_issue_data_list_map,
    )


def get_label_name_to_issue_list_map(github, repository):
    label_name_to_issue_list_map = defaultdict(list)

    for label in CORE_LABEL_NAMES_SET:
        query_string = f'repo:{repository.full_name} is:open is:issue label:"{label}" sort:reactions-+1-desc'

        issue_count = 0

        for issue in github.search_issues(query_string):
            labels_on_issue_set = set(
                label["name"] for label in issue._rawData["labels"]
            )
            ignored_labels_on_issue_set = labels_on_issue_set & IGNORED_LABEL_NAMES_SET

            if ignored_labels_on_issue_set:
                continue

            label_name_to_issue_list_map[label].append(issue)

            issue_count += 1

            if issue_count >= ISSUES_PER_LABEL:
                break

    return label_name_to_issue_list_map


def get_label_name_to_issue_data_list_map(label_name_to_issue_list_map):
    label_name_to_issue_data_list_map = {}

    for label_name in label_name_to_issue_list_map:
        issue_list = label_name_to_issue_list_map[label_name]
        issue_data_list = [IssueData(issue) for issue in issue_list]
        issue_data_list.sort(
            key=lambda issue_data: (
                -issue_data.like_count,
                issue_data.creation_datetime,
            )
        )

        if issue_data_list:
            label_name_to_issue_data_list_map[label_name] = issue_data_list

    return label_name_to_issue_data_list_map


def get_error_message_to_erroneous_issue_list_map(github, repository):
    error_message_to_erroneous_issue_list_map = defaultdict(list)

    filter_labels = CORE_LABEL_NAMES_SET.union(IGNORED_LABEL_NAMES_SET)
    filter_labels_string = " ".join([f'-label:"{label}"' for label in filter_labels])
    query_string = (
        f"repo:{repository.full_name} is:open is:issue {filter_labels_string}"
    )

    for issue in github.search_issues(query_string):
        error_message_to_erroneous_issue_list_map["missing core label"].append(issue)

    return error_message_to_erroneous_issue_list_map


def get_error_message_to_erroneous_issue_data_list_map(
    error_message_to_erroneous_issue_list_map,
):
    error_message_to_erroneous_issue_data_list_map = {}

    for label_name in error_message_to_erroneous_issue_list_map:
        issue_list = error_message_to_erroneous_issue_list_map[label_name]
        issue_data_list = [IssueData(issue) for issue in issue_list]
        error_message_to_erroneous_issue_data_list_map[label_name] = issue_data_list

    return error_message_to_erroneous_issue_data_list_map


def get_issue_text(
    label_name_to_issue_data_list_dictionary,
    error_message_to_erroneous_issue_data_list_map,
):
    tz = timezone("america/new_york")
    current_datetime = datetime.now(tz).strftime(f"{DATETIME_FORMAT_STRING} (%Z)")

    highest_ranking_issues_lines = get_highest_ranking_issues_lines(
        label_name_to_issue_data_list_dictionary
    )

    issue_text_lines = [
        f"*Updated on {current_datetime}*",
        *highest_ranking_issues_lines,
        "",
        "---\n",
    ]

    erroneous_issues_lines = get_erroneous_issues_lines(
        error_message_to_erroneous_issue_data_list_map
    )

    if erroneous_issues_lines:
        core_label_names_string = ", ".join(
            f'"{core_label_name}"' for core_label_name in CORE_LABEL_NAMES_SET
        )
        ignored_label_names_string = ", ".join(
            f'"{ignored_label_name}"' for ignored_label_name in IGNORED_LABEL_NAMES_SET
        )

        issue_text_lines.extend(
            [
                "## errors with issues (this section only shows when there are errors with issues)\n",
                f"This script expects every issue to have at least one of the following core labels: {core_label_names_string}",
                f"This script currently ignores issues that have one of the following labels: {ignored_label_names_string}\n",
                "### what to do?\n",
                "- Adjust the core labels on an issue to put it into a correct state or add a currently-ignored label to the issue",
                "- Adjust the core and ignored labels registered in this script",
                *erroneous_issues_lines,
                "",
                "---\n",
            ]
        )

    issue_text_lines.extend(
        [
            "*For details on how this issue is generated, [see the script](https://github.com/zed-industries/community/blob/main/scripts/update_top_ranking_issues/main.py)*",
        ]
    )

    return "\n".join(issue_text_lines)


def get_highest_ranking_issues_lines(label_name_to_issue_data_list_dictionary):
    highest_ranking_issues_lines = []

    if label_name_to_issue_data_list_dictionary:
        for label, issue_data_list in label_name_to_issue_data_list_dictionary.items():
            highest_ranking_issues_lines.append(f"\n## {label}\n")

            for issue_data in issue_data_list:
                markdown_bullet_point = (
                    f"{issue_data.url} ({issue_data.like_count} :thumbsup:)"
                )
                markdown_bullet_point = f"- {markdown_bullet_point}"
                highest_ranking_issues_lines.append(markdown_bullet_point)

    return highest_ranking_issues_lines


def get_erroneous_issues_lines(error_message_to_erroneous_issue_data_list_map):
    erroneous_issues_lines = []

    if error_message_to_erroneous_issue_data_list_map:
        for (
            error_message,
            erroneous_issue_data_list,
        ) in error_message_to_erroneous_issue_data_list_map.items():
            erroneous_issues_lines.append(f"\n#### {error_message}\n")

            for errorneous_issue_data in erroneous_issue_data_list:
                erroneous_issues_lines.append(f"- {errorneous_issue_data.url}")

    return erroneous_issues_lines


if __name__ == "__main__":
    start_time = datetime.now()
    main()
    run_duration = datetime.now() - start_time
    print(run_duration)
