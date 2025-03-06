#!/usr/bin/env python3

import argparse
import os
import subprocess

TICK_EMOJI = "\U00002705"
CROSS_EMOJI = "\U0000274C"
WARN_EMOJI = "\U000026A0\U0000FE0F"


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
    print(name.ljust(32), end='')
    if is_git_project(path):
        print(TICK_EMOJI, end='    ')

        # Running a git status seems to help make the following commands more accurate
        subprocess.run(["git", "-C", path, "status"], capture_output=True)

        if is_unstaged_changes(path):
            print(WARN_EMOJI, end='    ')
            print("  ", end='    ');
        else:
            print(TICK_EMOJI, end='    ')

            # TODO make work if there are unstaged changes and then deindent
            if is_untracked_files(path):
                print(WARN_EMOJI, end='    ')
            else:
                print(TICK_EMOJI, end='    ')

        if is_missing_remote(path):
            print(WARN_EMOJI, end='    ')
            print("  ", end='    ');
        else:
            print(TICK_EMOJI, end='    ')

            if is_unpushed_changes(path):
                print(WARN_EMOJI, end='    ')
            else:
                print(TICK_EMOJI, end='    ')
    else:
        print(CROSS_EMOJI, end='    ')
    print()


parser = argparse.ArgumentParser()
parser.add_argument('root_directory')
args = parser.parse_args()
print("Scanning " + args.root_directory)

print((" " * 11) + "No Unpushed Changes ━━━━━━━━━━━━━━━━━━━━━━━━━┓")
print((" " * 11) + "         Has Remote ━━━━━━━━━━━━━━━━━━━┓     ┃")
print((" " * 11) + " No Untracked Files ━━━━━━━━━━━━━┓     ┃     ┃")
print((" " * 11) + "No Unstaged Changes ━━━━━━━┓     ┃     ┃     ┃")
print((" " * 11) + "           Uses Git ━┓     ┃     ┃     ┃     ┃")

if is_git_project(args.root_directory):
    test(args.root_directory, os.path.basename(os.path.abspath(args.root_directory)))
else:
    directories = [ item for item in os.listdir(args.root_directory) if os.path.isdir(os.path.join(args.root_directory, item)) ]
    for directory in directories:
        full_path = os.path.join(args.root_directory, directory)
        test(full_path, directory)
