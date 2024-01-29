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
        raise ValueError(
            f"Could not decode git url from dependency {dependency_string}"
        )


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


def process_dep(dependency):
    if dependency["use_latest_commit"]:
        repo_url = get_git_url(dependency["repo"])
        latest_commit_hash = get_latest_commit_hash(repo_url, dependency["branch"])
        edit_pyproject_toml(
            dependency["repo"], dependency["branch"], latest_commit_hash
        )


def main():
    deps_dict_of_lists = {{cookiecutter.my_repo_deps}}
    n_deps = len(list(deps_dict_of_lists.values())[0])
    deps_list_of_dicts = [
        {key: value[i] for key, value in deps_dict_of_lists.items()}
        for i in range(n_deps)
    ]

    for dep in deps_list_of_dicts:
        process_dep(dep)


if __name__ == "__main__":
    main()
