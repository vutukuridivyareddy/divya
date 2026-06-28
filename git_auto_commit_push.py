"""Helper script to configure Git user details, add a remote, commit changes, and push."""

import argparse
import subprocess
import sys


def run_git_command(args, cwd=None):
    result = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout, end="")
        print(result.stderr, end="", file=sys.stderr)
        raise RuntimeError(f"Git command failed: git {' '.join(args)}")
    return result.stdout.strip()


def configure_git_user(name: str, email: str, cwd: str = None) -> None:
    if name:
        run_git_command(["config", "user.name", name], cwd=cwd)
        print(f"Set git user.name={name}")
    if email:
        run_git_command(["config", "user.email", email], cwd=cwd)
        print(f"Set git user.email={email}")


def add_remote(name: str, url: str, cwd: str = None) -> None:
    existing = run_git_command(["remote"], cwd=cwd).splitlines()
    if name in existing:
        run_git_command(["remote", "set-url", name, url], cwd=cwd)
        print(f"Updated remote '{name}' to {url}")
    else:
        run_git_command(["remote", "add", name, url], cwd=cwd)
        print(f"Added remote '{name}' pointing to {url}")


def commit_changes(message: str, all_changes: bool, cwd: str = None) -> None:
    if all_changes:
        run_git_command(["add", "-A"], cwd=cwd)
    else:
        print("No files staged. Use --all to add all changes.")
        sys.exit(1)

    run_git_command(["commit", "-m", message], cwd=cwd)
    print(f"Committed changes: {message}")


def push_changes(remote: str, branch: str, cwd: str = None) -> None:
    run_git_command(["push", remote, branch], cwd=cwd)
    print(f"Pushed branch '{branch}' to remote '{remote}'")


def main():
    parser = argparse.ArgumentParser(description="Configure Git and auto commit/push to a remote.")
    parser.add_argument("--user-name", help="Git user.name for commits.")
    parser.add_argument("--user-email", help="Git user.email for commits.")
    parser.add_argument("--remote-name", default="origin", help="Remote name to push to.")
    parser.add_argument("--remote-url", help="Remote URL to add or update.")
    parser.add_argument("--branch", default="main", help="Branch name to push.")
    parser.add_argument("--message", help="Commit message.")
    parser.add_argument("--all", action="store_true", help="Stage all changes before committing.")
    parser.add_argument("--no-push", action="store_true", help="Only commit, do not push.")
    args = parser.parse_args()

    if args.user_name or args.user_email:
        configure_git_user(args.user_name, args.user_email)

    if args.remote_url:
        add_remote(args.remote_name, args.remote_url)

    if args.message:
        commit_changes(args.message, args.all)
        if not args.no_push:
            push_changes(args.remote_name, args.branch)
    else:
        print("No commit message provided. Use --message to commit changes.")
        sys.exit(1)


if __name__ == "__main__":
    main()
