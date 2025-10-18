"""
Example: GitHub Issue Management Workflow

This example demonstrates how to use the GitHub operations tool
to manage issues automatically.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python.helpers.github_api import GitHubHelper


def example_create_and_manage_issue():
    """
    Example workflow: Create an issue, update it, and close it.
    """
    # Set up environment variables
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY", "owner/repo")
    
    if not token:
        print("❌ GITHUB_TOKEN environment variable not set")
        print("Set it with: export GITHUB_TOKEN=your_token_here")
        return
    
    print("=== GitHub Issue Management Example ===\n")
    
    # Initialize GitHub helper
    gh = GitHubHelper(token=token, repo_name=repo)
    
    if not gh.is_valid_repo():
        print(f"❌ Cannot access repository: {repo}")
        return
    
    # 1. Create a new issue
    print("1️⃣ Creating a new issue...")
    issue = gh.create_issue(
        title="Example: Add new feature",
        body="This is an example issue created by the GitHub operations tool.\n\n"
             "**Description:**\n"
             "We need to add a new feature that does XYZ.\n\n"
             "**Requirements:**\n"
             "- [ ] Requirement 1\n"
             "- [ ] Requirement 2\n"
             "- [ ] Requirement 3",
        labels=["enhancement", "example"],
        assignees=[]
    )
    
    if issue:
        print(f"✅ Created issue #{issue['number']}: {issue['title']}")
        print(f"   URL: {issue['url']}\n")
        issue_number = issue['number']
    else:
        print("❌ Failed to create issue")
        return
    
    # 2. Add a comment to the issue
    print("2️⃣ Adding a comment...")
    success = gh.add_issue_comment(
        issue_number=issue_number,
        comment="Starting work on this issue. Will update with progress."
    )
    
    if success:
        print(f"✅ Added comment to issue #{issue_number}\n")
    else:
        print(f"❌ Failed to add comment\n")
    
    # 3. Update the issue (add label, change assignee)
    print("3️⃣ Updating issue labels...")
    updated = gh.update_issue(
        issue_number=issue_number,
        labels=["enhancement", "example", "in-progress"]
    )
    
    if updated:
        print(f"✅ Updated issue #{issue_number} labels\n")
    else:
        print(f"❌ Failed to update issue\n")
    
    # 4. List all open issues
    print("4️⃣ Listing all open issues...")
    issues = gh.list_issues(state="open", limit=5)
    
    if issues:
        print(f"Found {len(issues)} open issues:")
        for i, issue_item in enumerate(issues, 1):
            print(f"   {i}. #{issue_item['number']}: {issue_item['title']}")
            print(f"      Labels: {', '.join(issue_item['labels'])}")
        print()
    
    # 5. Close the issue (cleanup)
    print("5️⃣ Closing the example issue (cleanup)...")
    closed = gh.close_issue(
        issue_number=issue_number,
        comment="This was an example issue. Closing for cleanup."
    )
    
    if closed:
        print(f"✅ Closed issue #{issue_number}\n")
    else:
        print(f"❌ Failed to close issue\n")
    
    print("=== Example Complete ===")


def example_review_and_prioritize():
    """
    Example workflow: Review all open issues and prioritize them.
    """
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY", "owner/repo")
    
    if not token:
        print("❌ GITHUB_TOKEN environment variable not set")
        return
    
    print("=== Issue Review and Prioritization Example ===\n")
    
    gh = GitHubHelper(token=token, repo_name=repo)
    
    if not gh.is_valid_repo():
        print(f"❌ Cannot access repository: {repo}")
        return
    
    # Get all open issues for review
    print("📋 Fetching all open issues...")
    issues = gh.get_repository_issues_for_review()
    
    if not issues:
        print("No open issues found.")
        return
    
    print(f"\nFound {len(issues)} open issues:\n")
    
    # Categorize issues
    bugs = [i for i in issues if 'bug' in i['labels']]
    enhancements = [i for i in issues if 'enhancement' in i['labels']]
    questions = [i for i in issues if 'question' in i['labels']]
    other = [i for i in issues if not any(l in i['labels'] for l in ['bug', 'enhancement', 'question'])]
    
    print("📊 Issue Summary:")
    print(f"   🐛 Bugs: {len(bugs)}")
    print(f"   ✨ Enhancements: {len(enhancements)}")
    print(f"   ❓ Questions: {len(questions)}")
    print(f"   📝 Other: {len(other)}\n")
    
    # Display bugs (highest priority)
    if bugs:
        print("🔴 HIGH PRIORITY - Bugs:\n")
        for bug in bugs[:5]:  # Show first 5
            print(f"   #{bug['number']}: {bug['title']}")
            print(f"   Created: {bug['created_at']}")
            print(f"   Assignees: {', '.join(bug['assignees']) or 'Unassigned'}")
            print()
    
    # Display enhancements
    if enhancements:
        print("🟡 MEDIUM PRIORITY - Enhancements:\n")
        for enhancement in enhancements[:3]:  # Show first 3
            print(f"   #{enhancement['number']}: {enhancement['title']}")
            print(f"   Created: {enhancement['created_at']}")
            print()
    
    print("=== Review Complete ===")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub Issue Management Examples")
    parser.add_argument(
        "--example",
        choices=["create", "review"],
        default="create",
        help="Which example to run"
    )
    
    args = parser.parse_args()
    
    if args.example == "create":
        example_create_and_manage_issue()
    elif args.example == "review":
        example_review_and_prioritize()
