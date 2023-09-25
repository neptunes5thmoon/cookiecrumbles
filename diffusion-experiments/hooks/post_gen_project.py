# SPDX-FileCopyrightText: 2023-present Larissa Heinrich <heinrichl@janelia.hhmi.org>
#
# SPDX-License-Identifier: MIT

import os
import re
import subprocess

import git


def get_git_url(dependency_string):
    github_url_pattern = r"(git\+[^:]+://[^/]+/[^/]+/[^/]+|git://[^/]+/[^/]+/[^/]+|https?://github\.com/[^/]+/[^/]+)"
    match = re.search(github_url_pattern, dependency_string)
    if match:
        github_url = match.group(1)
        return github_url
    else:
        raise ValueError(f"Could not decode git url from dependency {dependency_string}")


def get_latest_commit_hash(repo_url, branch):
    
    g = git.cmd.Git()
    # Get the latest commit hash without cloning the repository
    commits = g.ls_remote("--heads", repo_url).split("\n")
    for commit in commits:
        hash, reference = commit.split("\t")
        if reference.endswith(f"/{branch}"):
            return hash
    raise ValueError(f"Branch '{branch}' not found in the remote repository {repo_url}")

def edit_pyproject_toml(dependency_url, branch, latest_commit_hash):
    modified_lines = []
    with open("pyproject.toml", "r") as f:
        for line in f.readlines():
            if f"{dependency_url}@{branch}" in line:
                modified_line = line.replace(f"{branch}", latest_commit_hash)
                modified_lines.append(modified_line)
                print(f"Changing {line} to {modified_line} in pyproject.toml")
            else:
                modified_lines.append(line)
    with open("pyproject.toml", "w") as f:
        f.writelines(modified_lines)

def main():
    if {{cookiecutter.my_repo_use_latest_commit}}:
        repo_url = get_git_url("{{cookiecutter.my_repo_dep}}")
        latest_commit_hash = get_latest_commit_hash(repo_url, "{{cookiecutter.my_repo_dep_branch}}")
        edit_pyproject_toml("{{cookiecutter.my_repo_dep}}", "{{cookiecutter.my_repo_dep_branch}}", latest_commit_hash)        
if __name__ == "__main__":
    main()