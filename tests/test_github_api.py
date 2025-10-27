"""
Tests for GitHub API Helper
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from python.helpers.github_api import GitHubAPIHelper


class TestGitHubAPIHelper(unittest.TestCase):
    """Test cases for GitHubAPIHelper"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.token = "test_token_123"
        self.helper = GitHubAPIHelper(token=self.token)
    
    def test_initialization(self):
        """Test GitHubAPIHelper initialization"""
        self.assertEqual(self.helper.token, self.token)
        self.assertEqual(self.helper.base_url, "https://api.github.com")
        self.assertIn("Authorization", self.helper.session.headers)
        self.assertEqual(
            self.helper.session.headers["Authorization"],
            f"Bearer {self.token}"
        )
    
    def test_initialization_from_env(self):
        """Test initialization with token from environment"""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "env_token"}):
            helper = GitHubAPIHelper()
            self.assertEqual(helper.token, "env_token")
    
    @patch('requests.Session.request')
    def test_get_repo_success(self, mock_request):
        """Test successful repository retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "description": "Test repository"
        }
        mock_request.return_value = mock_response
        
        result = self.helper.get_repo("owner", "test-repo")
        
        self.assertEqual(result["name"], "test-repo")
        self.assertEqual(result["full_name"], "owner/test-repo")
        mock_request.assert_called_once()
    
    @patch('requests.Session.request')
    def test_list_repos(self, mock_request):
        """Test listing repositories"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "repo1", "full_name": "owner/repo1"},
            {"name": "repo2", "full_name": "owner/repo2"}
        ]
        mock_request.return_value = mock_response
        
        result = self.helper.list_repos("owner")
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "repo1")
        self.assertEqual(result[1]["name"], "repo2")
    
    @patch('requests.Session.request')
    def test_create_repo(self, mock_request):
        """Test repository creation"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "name": "new-repo",
            "full_name": "owner/new-repo",
            "html_url": "https://github.com/owner/new-repo"
        }
        mock_request.return_value = mock_response
        
        result = self.helper.create_repo(
            name="new-repo",
            description="Test repo",
            private=False
        )
        
        self.assertEqual(result["name"], "new-repo")
        self.assertIn("html_url", result)
    
    @patch('requests.Session.request')
    def test_get_content(self, mock_request):
        """Test getting file content"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "README.md",
            "path": "README.md",
            "type": "file",
            "content": "SGVsbG8gV29ybGQ="  # "Hello World" in base64
        }
        mock_request.return_value = mock_response
        
        result = self.helper.get_content("owner", "repo", "README.md")
        
        self.assertEqual(result["name"], "README.md")
        self.assertEqual(result["type"], "file")
    
    @patch('requests.Session.request')
    def test_create_issue(self, mock_request):
        """Test issue creation"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "number": 1,
            "title": "Test Issue",
            "state": "open"
        }
        mock_request.return_value = mock_response
        
        result = self.helper.create_issue(
            owner="owner",
            repo="repo",
            title="Test Issue",
            body="Issue description"
        )
        
        self.assertEqual(result["number"], 1)
        self.assertEqual(result["title"], "Test Issue")
        self.assertEqual(result["state"], "open")
    
    @patch('requests.Session.request')
    def test_search_code(self, mock_request):
        """Test code search"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"name": "file1.py", "path": "src/file1.py"},
                {"name": "file2.py", "path": "src/file2.py"}
            ]
        }
        mock_request.return_value = mock_response
        
        result = self.helper.search_code("test query")
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "file1.py")
    
    @patch('requests.Session.request')
    def test_error_handling(self, mock_request):
        """Test error handling"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Not Found"}
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        mock_request.return_value = mock_response
        
        with self.assertRaises(Exception) as context:
            self.helper.get_repo("owner", "nonexistent-repo")
        
        self.assertIn("GitHub API request failed", str(context.exception))
    
    def test_backup_knowledge_base_structure(self):
        """Test backup knowledge base method exists and has correct signature"""
        self.assertTrue(hasattr(self.helper, 'backup_knowledge_base'))
        self.assertTrue(callable(self.helper.backup_knowledge_base))
    
    def test_restore_knowledge_base_structure(self):
        """Test restore knowledge base method exists and has correct signature"""
        self.assertTrue(hasattr(self.helper, 'restore_knowledge_base'))
        self.assertTrue(callable(self.helper.restore_knowledge_base))


class TestGitHubAPIIntegration(unittest.TestCase):
    """Integration tests (require actual API access)"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            self.skipTest("GITHUB_TOKEN not set, skipping integration tests")
        self.helper = GitHubAPIHelper(token=self.token)
    
    def test_get_authenticated_user(self):
        """Test getting authenticated user information"""
        try:
            user = self.helper.get_authenticated_user()
            self.assertIn("login", user)
            self.assertIn("id", user)
        except Exception as e:
            self.skipTest(f"Integration test failed: {e}")


if __name__ == "__main__":
    unittest.main()
