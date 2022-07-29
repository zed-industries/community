import sys
from collections import defaultdict
from datetime import datetime

from github import Github
from pytz import timezone

DATETIME_FORMAT_STRING = "%m/%d/%Y %I:%M %p"
CORE_LABEL_NAMES_LIST = [
    "defect",
    "documentation",
    "enhancement",
    "panic / crash",
    "polish",
]
CORE_LABEL_NAMES_SET = set(CORE_LABEL_NAMES_LIST)
IGNORED_LABEL_NAMES_LIST = [
    "meta",
    "platform support"
]
IGNORED_LABEL_NAMES_SET = set(IGNORED_LABEL_NAMES_LIST)
ISSUES_PER_LABEL = 5

class CommandLineArgumentException(Exception):
    pass


class IssueData:
    def __init__(self, issue):
        self.url = issue.html_url
        self.like_count = sum(1 for reaction in issue.get_reactions() if reaction.content == "+1")
        self.creation_datetime = issue.created_at.strftime(DATETIME_FORMAT_STRING)
        self.has_assignees = bool(issue.assignees)


def main():
    if len(sys.argv) < 2:
        raise CommandLineArgumentException("A GitHub access token must be supplied")

    dev_mode = False

    if len(sys.argv) == 3:
        dev_mode_text = "dev_mode"

        if sys.argv[2] == dev_mode_text:
            dev_mode = True
        else:
            raise CommandLineArgumentException(f"If second argument is supplied, it must be  \"{dev_mode_text}\"")

    github_access_token = sys.argv[1]
    github = Github(github_access_token)

    repo_name = "zed-industries/feedback"
    repository = github.get_repo(repo_name)

    label_name_to_issue_data_list_map, error_message_to_erroneous_issue_data_list_map = get_issue_maps(github, repository)

    issue_text = get_issue_text(label_name_to_issue_data_list_map, error_message_to_erroneous_issue_data_list_map)

    if dev_mode:
        print(issue_text)
    else:
        top_ranking_issues_issue = repository.get_issue(number=52)
        top_ranking_issues_issue.edit(body=issue_text)


# TODO: Refactor this at some point
def get_issue_maps(github, repository):
    query_string = f"repo:{repository.full_name} is:open is:issue"

    label_name_to_issue_list_map = defaultdict(list)
    error_message_to_erroneous_issue_list_map = defaultdict(list)

    for issue in github.search_issues(query_string):
        labels_on_issue_set = set(label.name for label in issue.labels)
        core_labels_on_issue_set = labels_on_issue_set & CORE_LABEL_NAMES_SET
        ignored_labels_on_issue_set = labels_on_issue_set & IGNORED_LABEL_NAMES_SET

        if ignored_labels_on_issue_set:
            continue

        if len(core_labels_on_issue_set) == 0:
            error_message_to_erroneous_issue_list_map["missing core label"].append(issue)
        elif len(core_labels_on_issue_set) == 1:
            label_name = core_labels_on_issue_set.pop()
            label_name_to_issue_list_map[label_name].append(issue)
        else:
            error_message_to_erroneous_issue_list_map["too many core labels"].append(issue)

    label_name_to_issue_data_list_map = {}

    for label_name in label_name_to_issue_list_map:
        issue_list = label_name_to_issue_list_map[label_name]
        issue_data_list = [IssueData(issue) for issue in issue_list]
        issue_data_list.sort(key=lambda issue_data: (-issue_data.like_count, issue_data.creation_datetime))
        slice_end_index = get_slice_end_index(issue_data_list)
        issue_data_list = issue_data_list[0:slice_end_index]

        if issue_data_list:
            label_name_to_issue_data_list_map[label_name] = issue_data_list

    error_message_to_erroneous_issue_data_list_map = {}

    for label_name in error_message_to_erroneous_issue_list_map:
        issue_list = error_message_to_erroneous_issue_list_map[label_name]
        issue_data_list = [IssueData(issue) for issue in issue_list]
        error_message_to_erroneous_issue_data_list_map[label_name] = issue_data_list

    # Create a new dictionary with labels ordered by the summation the of likes on the associated issues
    label_names = list(label_name_to_issue_data_list_map.keys())

    label_names.sort(
        key=lambda label_name: sum(
            issue_data.like_count for issue_data in label_name_to_issue_data_list_map[label_name]
        ),
        reverse=True
    )

    label_name_to_issue_data_list_map = {
        label_name: label_name_to_issue_data_list_map[label_name] for label_name in label_names
    }

    return label_name_to_issue_data_list_map, error_message_to_erroneous_issue_data_list_map
    

def get_slice_end_index(issue_data_list):
    slice_end_index = 0
    issues_without_assignees_count = 0

    for issue_data in issue_data_list:
        slice_end_index += 1
        
        if not issue_data.has_assignees:
            issues_without_assignees_count += 1

            if issues_without_assignees_count == ISSUES_PER_LABEL:
                break

    return slice_end_index


def get_issue_text(label_name_to_issue_data_list_dictionary, error_message_to_erroneous_issue_data_list_map):
    tz = timezone("america/new_york")
    current_datetime = datetime.now(tz).strftime(f"{DATETIME_FORMAT_STRING} (%Z)")

    highest_ranking_issues_lines = get_highest_ranking_issues_lines(label_name_to_issue_data_list_dictionary)

    issue_text_lines = [
        "The main purpose of this issue is to provide the data of what testers might need in order to be able to use Zed more.  It should be noted that this issue's existence does not imply that anything will be prioritized differently; the Zed devs likely have their own process for how things are prioritized - this is simply a data set that *can* be used.\n",
        "**If there are defects / missing features that are slowing you down or preventing you from using Zed, make sure to file issues and vote on them, to bubble them up.  This list becomes more useful the more votes issues get.**\n",
        "---\n",
        f"*Updated on {current_datetime}*",
        *highest_ranking_issues_lines,
        "\n"
        "---\n",
    ]

    erroneous_issues_lines = get_erroneous_issues_lines(error_message_to_erroneous_issue_data_list_map)

    if erroneous_issues_lines:
        core_label_names_string = ", ".join(f"\"{core_label_name}\"" for core_label_name in CORE_LABEL_NAMES_LIST)
        ignored_label_names_string = ", ".join(f"\"{ignored_label_name}\"" for ignored_label_name in IGNORED_LABEL_NAMES_LIST)

        issue_text_lines.extend([
            "## errors with issues (this section only shows when there are errors with issues)\n",
            f"This script expects every issue to have only one of the following core labels: {core_label_names_string}",
            f"This script currently ignores issues that have one of the following labels: {ignored_label_names_string}\n",
            "### what to do?\n",
            "- Adjust the core labels on an issue to put it into a correct state or add a currently-ignored label to the issue",
            "- Adjust the core and ignored labels registered in this script",
            *erroneous_issues_lines,
            "\n"
            "---\n",
        ])

    issue_text_lines.extend([
        f"Issues that are italicized and decorated with a `*` have an assignee / are in progress and do not count towards the limit of {ISSUES_PER_LABEL} issues per label.\n",
        "*For details on how this issue is generated, [see the script](https://github.com/zed-industries/feedback/blob/main/scripts/update_top_ranking_issues/main.py)*"
    ])

    return "\n".join(issue_text_lines)


def get_highest_ranking_issues_lines(label_name_to_issue_data_list_dictionary):
    highest_ranking_issues_lines = []

    if label_name_to_issue_data_list_dictionary:
        for label, issue_data_list in label_name_to_issue_data_list_dictionary.items():
            highest_ranking_issues_lines.append(f"\n## {label}\n")

            for issue_data in issue_data_list:
                markdown_bullet_point = f"{issue_data.url} ({issue_data.like_count} :thumbsup:, {issue_data.creation_datetime} :calendar:)"
                                    
                if issue_data.has_assignees:
                    markdown_bullet_point = f"*{markdown_bullet_point}* *"
                
                markdown_bullet_point = f"- {markdown_bullet_point}"
                    
                highest_ranking_issues_lines.append(markdown_bullet_point)

    return highest_ranking_issues_lines


def get_erroneous_issues_lines(error_message_to_erroneous_issue_data_list_map):
    erroneous_issues_lines = []

    if error_message_to_erroneous_issue_data_list_map:
        for error_message, erroneous_issue_data_list in error_message_to_erroneous_issue_data_list_map.items():
            erroneous_issues_lines.append(f"\n#### {error_message}\n")

            for errorneous_issue_data in erroneous_issue_data_list:
                erroneous_issues_lines.append(f"- {errorneous_issue_data.url}")

    return erroneous_issues_lines


if __name__ == "__main__":
    main()

# TODO: Progress prints
# - "Gathering issues..."
