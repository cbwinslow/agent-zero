### Recommendations 20250709_042844
- Add pytest.ini to simplify running tests and ensure 'python' package is found.
- Ignore python/api/backup_test.py during collection to avoid import errors.
- Added helper tests for dotenv and file utilities as a starting point for full coverage.
- Provided a deployment script for Hetzner servers using Nginx at cloudcurio.cc/agent-zero.
- Ensure requirements.txt packages are installed before running tests.
