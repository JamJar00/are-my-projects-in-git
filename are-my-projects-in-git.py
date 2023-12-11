#!/usr/bin/env python3

import argparse
import os
import subprocess

TICK_EMOJI = "\U00002705"
CROSS_EMOJI = "\U0000274C"


def is_git_project(path):
    res = subprocess.run(["git", "-C", path, "rev-parse", "--is-inside-work-tree"], capture_output=True)
    return res.stdout.strip().decode() == "true"


def is_unstaged_changes(path):
    res = subprocess.run(["git", "-C", path, "diff-index", "--quiet", "HEAD", "--"], capture_output=True)
    return res.returncode != 0


def is_untracked_files(path):
    res = subprocess.run(["git", "-C", path, "status", "--untracked-files", "--porcelain"], capture_output=True)
    return len(res.stdout.strip()) != 0


def is_missing_remote(path):
    res = subprocess.run(["git", "-C", path, "remote", "get-url", "origin"], capture_output=True)
    return res.returncode != 0


def is_unpushed_changes(path):
    res = subprocess.run(["git", "-C", path, "log", "@{u}.."], capture_output=True)
    return res.returncode != 0 or len(res.stdout.strip()) != 0


def test(path, name):
    if is_git_project(path):
        print(f"{name.ljust(32)} is using git {TICK_EMOJI}")
        if is_unstaged_changes(path):
            print(f"{name.ljust(32)} has unstaged changes {CROSS_EMOJI}")
        else:
            print(f"{name.ljust(32)} has no unstaged changes {TICK_EMOJI}")

            # TODO make work if there are unstaged changes and then deindent
            if is_untracked_files(path):
                print(f"{name.ljust(32)} has untracked files {CROSS_EMOJI}")
            else:
                print(f"{name.ljust(32)} has no untracked files {TICK_EMOJI}")

        if is_missing_remote(path):
            print(f"{name.ljust(32)} has no remote {CROSS_EMOJI}")
        else:
            print(f"{name.ljust(32)} has a remote {TICK_EMOJI}")

            if is_unpushed_changes(path):
                print(f"{name.ljust(32)} has unpushed changes {CROSS_EMOJI}")
            else:
                print(f"{name.ljust(32)} has no unpushed changes {TICK_EMOJI}")
    else:
        print(f"{name.ljust(32)} is not using git {CROSS_EMOJI}")
    print()


parser = argparse.ArgumentParser()
parser.add_argument('root_directory')
args = parser.parse_args()
print("Scanning " + args.root_directory)

if is_git_project(args.root_directory):
    test(args.root_directory, os.path.basename(os.path.abspath(args.root_directory)))
else:
    directories = [ item for item in os.listdir(args.root_directory) if os.path.isdir(os.path.join(args.root_directory, item)) ]
    for directory in directories:
        full_path = os.path.join(args.root_directory, directory)
        test(full_path, directory)
