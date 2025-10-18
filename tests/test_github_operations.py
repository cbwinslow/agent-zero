"""
Test suite for GitHub Operations

This test file validates the GitHub operations tool and helper.
To run tests, set GITHUB_TOKEN and GITHUB_REPOSITORY environment variables.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from unittest.mock import Mock, patch, MagicMock
from python.helpers.github_api import GitHubHelper


def test_github_helper_initialization():
    """Test GitHubHelper initialization with token"""
    # Test without token (should raise error)
    try:
        helper = GitHubHelper()
        assert False, "Should raise ValueError without token"
    except ValueError as e:
        assert "token is required" in str(e).lower()
        print("✓ Correctly raises error without token")


def test_github_helper_with_token():
    """Test GitHubHelper initialization with token"""
    token = os.getenv("GITHUB_TOKEN", "test_token")
    repo = os.getenv("GITHUB_REPOSITORY", "owner/repo")
    
    with patch('python.helpers.github_api.Github') as mock_github:
        mock_repo = MagicMock()
        mock_github.return_value.get_repo.return_value = mock_repo
        
        helper = GitHubHelper(token=token, repo_name=repo)
        
        assert helper.token == token
        assert helper.repo_name == repo
        assert helper.is_valid_repo()
        print("✓ GitHubHelper initialized successfully with token")


def test_create_issue_structure():
    """Test create_issue method structure"""
    token = os.getenv("GITHUB_TOKEN", "test_token")
    repo = os.getenv("GITHUB_REPOSITORY", "owner/repo")
    
    with patch('python.helpers.github_api.Github') as mock_github:
        mock_repo = MagicMock()
        mock_issue = MagicMock()
        mock_issue.number = 123
        mock_issue.title = "Test Issue"
        mock_issue.html_url = "https://github.com/owner/repo/issues/123"
        mock_issue.state = "open"
        mock_issue.created_at.isoformat.return_value = "2024-01-01T00:00:00"
        
        mock_repo.create_issue.return_value = mock_issue
        mock_github.return_value.get_repo.return_value = mock_repo
        
        helper = GitHubHelper(token=token, repo_name=repo)
        result = helper.create_issue(
            title="Test Issue",
            body="Test body",
            labels=["bug"],
            assignees=["testuser"]
        )
        
        assert result is not None
        assert result["number"] == 123
        assert result["title"] == "Test Issue"
        assert result["state"] == "open"
        print("✓ create_issue returns correct structure")


def test_list_issues_structure():
    """Test list_issues method structure"""
    token = os.getenv("GITHUB_TOKEN", "test_token")
    repo = os.getenv("GITHUB_REPOSITORY", "owner/repo")
    
    with patch('python.helpers.github_api.Github') as mock_github:
        mock_repo = MagicMock()
        
        # Create mock issues
        mock_issue1 = MagicMock()
        mock_issue1.number = 1
        mock_issue1.title = "Issue 1"
        mock_issue1.state = "open"
        mock_issue1.pull_request = None
        mock_issue1.labels = []
        mock_issue1.assignees = []
        mock_issue1.html_url = "https://github.com/owner/repo/issues/1"
        mock_issue1.created_at.isoformat.return_value = "2024-01-01T00:00:00"
        
        mock_repo.get_issues.return_value = [mock_issue1]
        mock_github.return_value.get_repo.return_value = mock_repo
        
        helper = GitHubHelper(token=token, repo_name=repo)
        issues = helper.list_issues(state="open", limit=10)
        
        assert isinstance(issues, list)
        assert len(issues) > 0
        assert "number" in issues[0]
        assert "title" in issues[0]
        print("✓ list_issues returns correct structure")


def test_create_pull_request_structure():
    """Test create_pull_request method structure"""
    token = os.getenv("GITHUB_TOKEN", "test_token")
    repo = os.getenv("GITHUB_REPOSITORY", "owner/repo")
    
    with patch('python.helpers.github_api.Github') as mock_github:
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        mock_pr.number = 456
        mock_pr.title = "Test PR"
        mock_pr.html_url = "https://github.com/owner/repo/pull/456"
        mock_pr.state = "open"
        mock_pr.created_at.isoformat.return_value = "2024-01-01T00:00:00"
        
        mock_repo.create_pull.return_value = mock_pr
        mock_github.return_value.get_repo.return_value = mock_repo
        
        helper = GitHubHelper(token=token, repo_name=repo)
        result = helper.create_pull_request(
            title="Test PR",
            body="Test body",
            head="feature-branch",
            base="main"
        )
        
        assert result is not None
        assert result["number"] == 456
        assert result["title"] == "Test PR"
        assert result["state"] == "open"
        print("✓ create_pull_request returns correct structure")


def test_link_issue_to_pr():
    """Test linking issues to pull requests"""
    token = os.getenv("GITHUB_TOKEN", "test_token")
    repo = os.getenv("GITHUB_REPOSITORY", "owner/repo")
    
    with patch('python.helpers.github_api.Github') as mock_github:
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        mock_pr.body = "Original PR body"
        mock_pr.edit = MagicMock()
        
        mock_repo.get_pull.return_value = mock_pr
        mock_github.return_value.get_repo.return_value = mock_repo
        
        helper = GitHubHelper(token=token, repo_name=repo)
        result = helper.link_issue_to_pr(
            pr_number=456,
            issue_numbers=[1, 2, 3]
        )
        
        assert result is True
        mock_pr.edit.assert_called_once()
        print("✓ link_issue_to_pr works correctly")


def test_update_issue():
    """Test updating an issue"""
    token = os.getenv("GITHUB_TOKEN", "test_token")
    repo = os.getenv("GITHUB_REPOSITORY", "owner/repo")
    
    with patch('python.helpers.github_api.Github') as mock_github:
        mock_repo = MagicMock()
        mock_issue = MagicMock()
        mock_issue.number = 123
        mock_issue.title = "Updated Title"
        mock_issue.html_url = "https://github.com/owner/repo/issues/123"
        mock_issue.state = "open"
        mock_issue.updated_at.isoformat.return_value = "2024-01-02T00:00:00"
        
        mock_repo.get_issue.return_value = mock_issue
        mock_github.return_value.get_repo.return_value = mock_repo
        
        helper = GitHubHelper(token=token, repo_name=repo)
        result = helper.update_issue(
            issue_number=123,
            title="Updated Title",
            state="closed"
        )
        
        assert result is not None
        assert result["title"] == "Updated Title"
        print("✓ update_issue works correctly")


def test_close_issue():
    """Test closing an issue"""
    token = os.getenv("GITHUB_TOKEN", "test_token")
    repo = os.getenv("GITHUB_REPOSITORY", "owner/repo")
    
    with patch('python.helpers.github_api.Github') as mock_github:
        mock_repo = MagicMock()
        mock_issue = MagicMock()
        
        mock_repo.get_issue.return_value = mock_issue
        mock_github.return_value.get_repo.return_value = mock_repo
        
        helper = GitHubHelper(token=token, repo_name=repo)
        result = helper.close_issue(
            issue_number=123,
            comment="Closing this issue"
        )
        
        assert result is True
        mock_issue.create_comment.assert_called_once_with("Closing this issue")
        mock_issue.edit.assert_called_once_with(state="closed")
        print("✓ close_issue works correctly")


def run_tests():
    """Run all tests"""
    print("\n=== Running GitHub Operations Tests ===\n")
    
    tests = [
        test_github_helper_initialization,
        test_github_helper_with_token,
        test_create_issue_structure,
        test_list_issues_structure,
        test_create_pull_request_structure,
        test_link_issue_to_pr,
        test_update_issue,
        test_close_issue,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {failed} test(s) failed")
    
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
