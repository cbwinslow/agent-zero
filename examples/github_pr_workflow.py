"""
Example: GitHub Pull Request Workflow

This example demonstrates how to create and manage pull requests
with automatic issue linking.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python.helpers.github_api import GitHubHelper
from python.helpers.git import GitHelper


def example_create_pr_with_issue_link():
    """
    Example workflow: Create a branch, make changes, create PR, and link to issues.
    """
    gh_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY", "owner/repo")
    
    if not gh_token:
        print("❌ GITHUB_TOKEN environment variable not set")
        print("Set it with: export GITHUB_TOKEN=your_token_here")
        return
    
    print("=== GitHub Pull Request Workflow Example ===\n")
    
    # Initialize GitHub helper
    gh = GitHubHelper(token=gh_token, repo_name=repo_name)
    
    if not gh.is_valid_repo():
        print(f"❌ Cannot access repository: {repo_name}")
        return
    
    # 1. Create an issue to fix
    print("1️⃣ Creating an issue to fix...")
    issue = gh.create_issue(
        title="Example: Fix documentation typo",
        body="There's a typo in the README that needs to be fixed.",
        labels=["documentation", "bug"]
    )
    
    if not issue:
        print("❌ Failed to create issue")
        return
    
    issue_number = issue['number']
    print(f"✅ Created issue #{issue_number}: {issue['title']}")
    print(f"   URL: {issue['url']}\n")
    
    # 2. Create a pull request
    print("2️⃣ Creating pull request...")
    pr = gh.create_pull_request(
        title=f"Fix: Documentation typo (#{issue_number})",
        body=f"This PR fixes the documentation typo reported in issue #{issue_number}.\n\n"
             f"**Changes:**\n"
             f"- Fixed typo in README\n"
             f"- Updated documentation\n\n"
             f"Fixes #{issue_number}",
        head="example-fix-branch",
        base="main",
        draft=False
    )
    
    if pr:
        print(f"✅ Created PR #{pr['number']}: {pr['title']}")
        print(f"   URL: {pr['url']}\n")
        pr_number = pr['number']
    else:
        print("❌ Failed to create PR")
        print("Note: Branch 'example-fix-branch' must exist in the repository")
        # Cleanup the issue
        gh.close_issue(issue_number, "PR creation failed, closing issue")
        return
    
    # 3. Link additional issues if needed
    print("3️⃣ Linking issues to PR...")
    linked = gh.link_issue_to_pr(
        pr_number=pr_number,
        issue_numbers=[issue_number]
    )
    
    if linked:
        print(f"✅ Linked issue #{issue_number} to PR #{pr_number}\n")
    
    # 4. List all open PRs
    print("4️⃣ Listing all open pull requests...")
    prs = gh.list_pull_requests(state="open", limit=5)
    
    if prs:
        print(f"Found {len(prs)} open pull requests:")
        for i, pr_item in enumerate(prs, 1):
            print(f"   {i}. #{pr_item['number']}: {pr_item['title']}")
            print(f"      {pr_item['head']} → {pr_item['base']}")
        print()
    
    # 5. Update PR (add more details)
    print("5️⃣ Updating PR details...")
    updated_pr = gh.update_pull_request(
        pr_number=pr_number,
        body=f"This PR fixes the documentation typo reported in issue #{issue_number}.\n\n"
             f"**Changes:**\n"
             f"- Fixed typo in README\n"
             f"- Updated documentation\n"
             f"- Added tests\n\n"
             f"**Testing:**\n"
             f"- Verified documentation builds correctly\n"
             f"- Checked all links\n\n"
             f"Fixes #{issue_number}"
    )
    
    if updated_pr:
        print(f"✅ Updated PR #{pr_number}\n")
    
    print("=== Example Complete ===")
    print(f"\n📝 Note: Remember to close or merge PR #{pr_number} and issue #{issue_number} manually")


def example_review_prs():
    """
    Example workflow: Review all open pull requests.
    """
    gh_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY", "owner/repo")
    
    if not gh_token:
        print("❌ GITHUB_TOKEN environment variable not set")
        return
    
    print("=== Pull Request Review Example ===\n")
    
    gh = GitHubHelper(token=gh_token, repo_name=repo_name)
    
    if not gh.is_valid_repo():
        print(f"❌ Cannot access repository: {repo_name}")
        return
    
    # Get all open PRs
    print("📋 Fetching all open pull requests...")
    prs = gh.list_pull_requests(state="open", limit=20)
    
    if not prs:
        print("No open pull requests found.")
        return
    
    print(f"\nFound {len(prs)} open pull requests:\n")
    
    for pr in prs:
        print(f"PR #{pr['number']}: {pr['title']}")
        print(f"   Branch: {pr['head']} → {pr['base']}")
        print(f"   Created: {pr['created_at']}")
        print(f"   URL: {pr['url']}")
        print()
    
    print("=== Review Complete ===")


def example_automated_merge_workflow():
    """
    Example: Automated workflow for merging approved PRs.
    
    Note: This is a demonstration. In production, you should have
    proper review and approval processes before merging.
    """
    gh_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY", "owner/repo")
    
    if not gh_token:
        print("❌ GITHUB_TOKEN environment variable not set")
        return
    
    print("=== Automated PR Merge Workflow Example ===\n")
    print("⚠️  This is a demonstration only. Do not use in production without proper reviews!\n")
    
    gh = GitHubHelper(token=gh_token, repo_name=repo_name)
    
    if not gh.is_valid_repo():
        print(f"❌ Cannot access repository: {repo_name}")
        return
    
    # Get PRs ready to merge (this is just a demo, in reality you'd check approvals)
    prs = gh.list_pull_requests(state="open", limit=10)
    
    if not prs:
        print("No open pull requests found.")
        return
    
    print(f"Found {len(prs)} open pull requests\n")
    
    # In a real scenario, you would:
    # 1. Check if PR has required approvals
    # 2. Check if all CI checks pass
    # 3. Check if there are no merge conflicts
    # 4. Then merge
    
    print("Example steps for automated merge:")
    print("1. ✅ Check PR approvals")
    print("2. ✅ Verify CI/CD checks pass")
    print("3. ✅ Confirm no merge conflicts")
    print("4. 🔄 Merge PR using appropriate method (merge/squash/rebase)")
    print("5. ✅ Close linked issues")
    print("6. 📧 Notify relevant parties")
    
    print("\n=== Workflow Complete ===")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub Pull Request Examples")
    parser.add_argument(
        "--example",
        choices=["create", "review", "merge"],
        default="create",
        help="Which example to run"
    )
    
    args = parser.parse_args()
    
    if args.example == "create":
        example_create_pr_with_issue_link()
    elif args.example == "review":
        example_review_prs()
    elif args.example == "merge":
        example_automated_merge_workflow()
