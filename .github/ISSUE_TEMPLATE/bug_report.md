---
name: Bug report
about: Create a report to help us improve
title: 'Title'
labels: 'defect, triage'
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
Copy & paste output of this command:
```sh
echo -e "- Architecture: \`$(uname -m)\`\n- $(sw_vers -productName) Version: \`$(sw_vers -productVersion) ($(sw_vers -buildVersion))\`\n- Zed Version: \`$(/Applications/Zed.app/Contents/MacOS/cli --version | grep --only-matching --extended-regexp '[0-9]+\.[0-9]+\.[0-9]+')\`"
```

**Additional context**
Add any other context about the problem here.
