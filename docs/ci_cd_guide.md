# CI/CD and Automation Guide

This guide explains the comprehensive CI/CD pipeline and automation tools integrated into Agent Zero.

## Overview

Agent Zero now includes a full suite of GitHub Actions workflows for continuous integration, deployment, security, and automation. This infrastructure ensures code quality, security, and reliability while automating repetitive tasks.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Developer Workflow                        │
│  Push → PR → Tests → Review → Merge → Deploy               │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────┴──────────────────────────────────────────────┐
│                  GitHub Actions Workflows                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   CI Tests   │  │   Security   │  │    Docker    │     │
│  │   - Python   │  │   - CodeQL   │  │   - Build    │     │
│  │   - Lint     │  │   - Snyk     │  │   - Push     │     │
│  │   - Format   │  │   - Bandit   │  │   - Scan     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Performance  │  │    Release   │  │     Docs     │     │
│  │ - Benchmarks │  │  - Changelog │  │  - Build     │     │
│  │ - Metrics    │  │  - PyPI      │  │  - Validate  │     │
│  │ - Load Test  │  │  - GitHub    │  │  - Deploy    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ Auto-Update  │  │ PR Automation│                        │
│  │ - Deps       │  │  - Labels    │                        │
│  │ - Actions    │  │  - Assign    │                        │
│  │ - Security   │  │  - Commands  │                        │
│  └──────────────┘  └──────────────┘                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Workflow Categories

### 1. Continuous Integration (CI)

**Workflow:** `ci.yml`

**Purpose:** Validate code quality and functionality on every change

**Triggers:**
- Push to main/master/develop
- Pull requests

**Jobs:**
- **Test**: Run tests across Python 3.10, 3.11, 3.12
- **Lint**: Code quality checks (Ruff, Black, isort)
- **Security**: Vulnerability scanning (Bandit, Safety)

**Benefits:**
- Early bug detection
- Consistent code style
- Security vulnerability identification
- Cross-version compatibility

### 2. Docker Build & Deploy

**Workflow:** `docker.yml`

**Purpose:** Build, test, and publish Docker images

**Triggers:**
- Push to main
- Version tags (v*)
- Pull requests
- Manual dispatch

**Jobs:**
- **Build**: Multi-platform Docker images (amd64, arm64)
- **Push**: Automatic push to Docker Hub on main
- **Test**: Container startup verification
- **Scan**: Vulnerability scanning with Trivy

**Features:**
- Semantic versioning
- Build caching
- Multi-architecture support
- Security scanning
- Automated publishing

### 3. Security Analysis

**Workflow:** `codeql.yml`

**Purpose:** Comprehensive security analysis

**Triggers:**
- Push to main/develop
- Pull requests
- Weekly schedule (Monday)

**Jobs:**
- **CodeQL**: Static analysis for Python and JavaScript
- **Dependency Review**: Check for vulnerable dependencies
- **Snyk**: Additional security scanning

**Benefits:**
- Early vulnerability detection
- Dependency security monitoring
- Automated security reports
- SARIF integration

### 4. Release Management

**Workflow:** `release.yml`

**Purpose:** Automate release process

**Triggers:**
- Version tags (v*)
- Manual dispatch

**Jobs:**
- **Create Release**: GitHub release with changelog
- **Publish PyPI**: Upload to Python Package Index

**Features:**
- Automatic changelog generation
- Semantic release notes
- PyPI publishing
- Version tagging

### 5. Documentation

**Workflow:** `docs.yml`

**Purpose:** Maintain documentation quality

**Triggers:**
- Changes to docs/ or .md files
- Manual dispatch

**Jobs:**
- **Validate**: Check Markdown links
- **Lint**: Markdown formatting
- **Build**: Generate MkDocs site
- **Spell Check**: Catch typos

**Benefits:**
- Broken link detection
- Consistent formatting
- Automated site generation
- Spelling verification

### 6. Performance Testing

**Workflow:** `performance.yml`

**Purpose:** Monitor performance and code quality

**Triggers:**
- Push to main
- Pull requests
- Weekly schedule
- Manual dispatch

**Jobs:**
- **Performance**: Benchmarks and profiling
- **Metrics**: Code complexity analysis
- **Load Test**: Stress testing (scheduled/manual)

**Metrics:**
- Execution time
- Memory usage
- Cyclomatic complexity
- Maintainability index

### 7. Auto-Update

**Workflow:** `auto-update.yml`

**Purpose:** Keep dependencies and actions current

**Triggers:**
- Weekly schedule (Monday)
- Manual dispatch

**Jobs:**
- **Update Dependencies**: Python packages
- **Update Actions**: GitHub Actions versions
- **Security Updates**: Vulnerability patches

**Features:**
- Automatic PR creation
- Security issue tracking
- Dependency updates
- Action version updates

### 8. PR Automation

**Workflow:** `pr-automation.yml`

**Purpose:** Streamline PR workflow

**Triggers:**
- Pull request events
- PR reviews
- Issue comments

**Jobs:**
- **Auto-label**: Based on file changes
- **Size label**: XS, S, M, L, XL
- **Title check**: Semantic PR titles
- **Auto-assign**: Reviewer assignment
- **Stale detection**: Mark inactive PRs
- **Conflict check**: Rebase detection
- **Command bot**: /rerun, /format commands

## Setup Instructions

### 1. Initial Setup

```bash
# Clone the repository
git clone https://github.com/agent0ai/agent-zero.git
cd agent-zero

# All workflows are already configured in .github/workflows/
ls .github/workflows/
```

### 2. Configure Secrets

Add these secrets in GitHub repository settings:

**Required:**
```
DOCKER_USERNAME      # For Docker Hub publishing
DOCKER_PASSWORD      # Docker Hub token
```

**Optional (for enhanced features):**
```
PYPI_TOKEN          # For PyPI publishing
SNYK_TOKEN          # For Snyk security scanning
```

**How to add secrets:**
1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add name and value
4. Click "Add secret"

### 3. Enable Workflows

Workflows are enabled by default. To verify:

1. Go to Actions tab in GitHub
2. Check that workflows are listed
3. Review any workflow runs

### 4. Configure Branch Protection

Recommended protection rules for `main` branch:

1. Go to Settings → Branches
2. Add rule for `main`
3. Enable:
   - Require pull request reviews
   - Require status checks (select CI jobs)
   - Require branches to be up to date
   - Include administrators

## Usage Examples

### Running Tests Locally

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio

# Run all tests
pytest tests/ -v

# Run specific test
python tests/test_mcp_discovery.py

# Run with coverage
pytest tests/ --cov=python --cov-report=html
```

### Building Docker Image Locally

```bash
# Build from run Dockerfile
docker build -t agent-zero:local -f docker/run/Dockerfile .

# Build from local Dockerfile
docker build -t agent-zero:dev -f DockerfileLocal .

# Run locally
docker run -p 50001:80 agent-zero:local
```

### Manual Release

```bash
# Create and push tag
git tag -a v0.9.7 -m "Release v0.9.7"
git push origin v0.9.7

# Workflows will automatically:
# 1. Create GitHub release
# 2. Generate changelog
# 3. Build Docker images
# 4. Publish to PyPI (if configured)
```

### Triggering Workflows Manually

1. Go to Actions tab
2. Select workflow
3. Click "Run workflow"
4. Choose branch
5. Fill in inputs (if any)
6. Click "Run workflow"

## Best Practices

### For Developers

1. **Before Creating PR:**
   - Run tests locally
   - Check code formatting
   - Review changes

2. **PR Title Format:**
   ```
   type(scope): description
   
   Examples:
   feat(mcp): add server discovery
   fix(ui): resolve button alignment
   docs(readme): update installation steps
   ```

3. **Commit Messages:**
   - Clear and descriptive
   - Reference issues when applicable
   - Use conventional commits

### For Reviewers

1. **Check CI Status:**
   - All tests passing
   - No security issues
   - Code coverage acceptable

2. **Review Changes:**
   - Code quality
   - Documentation updates
   - Test coverage

3. **Approve & Merge:**
   - Squash merge for clean history
   - Delete branch after merge

### For Maintainers

1. **Regular Maintenance:**
   - Review security scan results
   - Update dependencies weekly
   - Monitor workflow performance

2. **Release Process:**
   - Update changelog
   - Bump version
   - Create tag
   - Verify automated release

3. **Workflow Updates:**
   - Keep actions up to date
   - Optimize execution time
   - Add new checks as needed

## Monitoring and Metrics

### Workflow Status

Check workflow status in:
- Actions tab on GitHub
- PR checks
- Status badges in README

### Key Metrics

Monitor these metrics:
- **Test Pass Rate**: Should be 100%
- **Coverage**: Maintain >80%
- **Build Time**: Optimize if >10 minutes
- **Security Issues**: Address immediately

### Notifications

Configure notifications for:
- Failed workflows
- Security alerts
- Dependency updates
- Stale PRs

## Troubleshooting

### Common Issues

**1. Tests Failing**
```bash
# Check test output in Actions
# Run locally to debug
pytest tests/ -v -s

# Check Python version
python --version
```

**2. Docker Build Failing**
```bash
# Test build locally
docker build -t test -f docker/run/Dockerfile .

# Check Dockerfile syntax
docker build --dry-run -f docker/run/Dockerfile .
```

**3. Secrets Not Working**
- Verify secret names match exactly
- Check secret values have no extra spaces
- Ensure workflow has permissions

**4. Workflow Not Triggering**
- Check branch filters
- Verify file path patterns
- Review workflow syntax

### Getting Help

1. Check workflow logs in Actions tab
2. Review error messages
3. Consult workflow README
4. Open issue on GitHub
5. Ask in Discord community

## Advanced Features

### Custom Runners

For private repositories or special requirements:

1. Set up self-hosted runner
2. Update workflow to use custom runner:
   ```yaml
   jobs:
     my-job:
       runs-on: self-hosted
   ```

### Matrix Builds

Test across multiple configurations:

```yaml
strategy:
  matrix:
    python-version: [3.10, 3.11, 3.12]
    os: [ubuntu-latest, macos-latest, windows-latest]
```

### Conditional Execution

Run jobs based on conditions:

```yaml
jobs:
  deploy:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
```

### Caching

Speed up workflows with caching:

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Docker Actions](https://docs.docker.com/build/ci/github-actions/)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [Agent Zero Documentation](../docs/README.md)

## Contributing

To improve CI/CD:

1. Test changes in fork
2. Document new features
3. Update this guide
4. Submit PR with clear description

---

**Questions?** Open an issue or ask in our Discord community.

**Found a bug?** Report it on GitHub with workflow logs.

**Have suggestions?** We welcome contributions!
