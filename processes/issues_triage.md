# Issue triage

All issue templates automatically add the `triage` label to new issues.  This makes it easy to see what we need to read, respond to, and label.  After a issue is triaged, we remove this label.  If we add future maintainers, we will need to use a different system that prevents issues triaged by community maintainers from being difficult to discover as "new" issues; we still want to read everything submitted by users so that we can keep a pulse on what the community wants.  [Flutter uses a primary and secondary triage label system](https://medium.com/flutter/managing-issues-in-a-large-scale-open-source-project-b3be6eecae2b), maybe this could be adopted, in some form, to represent different groups having seen the issue.

## Duplicates

We try to close out duplicates when we spot them.  This isn't always easy - things slip through the cracks at times, but we try our best.  The rule we've adopted for closing duplicates is to close out the issue containing fewer upvotes.  This is almost always the older issue, but that isn't always the case.  If both issues have the same number of upvotes, we close the newer one.  We then usually leave a comment to encourage anyone following that issue to upvote the other issue and provide a link to it as well.

Note: [Add a GitHub action that will automate closing duplicate issues](https://github.com/zed-industries/community/issues/1440)

## Core Labels and Top-Ranking Issues

Every issue needs a "core" label.  You can find these by searching through the [labels with descriptions of `[core label]`](https://github.com/zed-industries/community/labels).  All of our issue templates automatically add some core label by default, but users sometimes open issues without using any template.  We have [a script that uses these labels](https://github.com/zed-industries/community/blob/main/scripts/update_top_ranking_issues/main.py) to to generate a [Top-Ranking Issues report](https://github.com/zed-industries/community/issues/52).  If an issue is missing a core label, it will be displayed at the bottom of the report on next generation, and will persist until a label has been added to an issue.  All of our issue templates automatically add some core label by default, but users sometimes open issues without using the templates.  Looking through the labels again, you'll see some that have a description of `[ignored label]`.  Any issue with one of these labels will be skipped when the script generates the report.  The majority of issues will get either an `enhancement` or `defect` core label.  All other labels in the repository are modifier labels.  These are used to to group similar issue or help to provide more specific details about the issue.  These include labels that point to a specific part of Zed, like `editor`, or a specific featureset, like `vim`.

## Languages

For languages we support, we always include:

1. Either the `enhancement` or `defect` core labe
2. The generic `language` label
3. The specific language label (`rust`, `python`, etc.).

For languages that we don't support, we use the same labels as in steps 1 and 2, but we add `unsupported` as a third generic label.  We don't create labels for specific languages that we don't support, as it adds a lot of clutter.

## Convert to issues to discussions

Once in a while, users will make issues that ask questions that are better served as discussions.  Since we are trying to build up our community [Q&A](https://github.com/zed-industries/community/discussions/categories/q-a), we've been trying to identify and convert these.
