# GitHub Actions Workflows

This directory contains automated workflows for CI/CD, security, quality assurance, and project automation.

## 📋 Available Workflows

### Core CI/CD

#### **ci.yml** - Continuous Integration
Runs on: Pull requests and pushes to main/develop branches

**Features:**
- Tests across Python 3.10, 3.11, and 3.12
- Code linting with Ruff, Black, and isort
- Security scanning with Bandit and Safety
- Automatic test execution
- Security report artifacts

**Usage:** Automatic on PRs and commits

---

#### **docker.yml** - Docker Build & Push
Runs on: Push to main, tags, PRs, and manual trigger

**Features:**
- Multi-platform builds (amd64, arm64)
- Automatic push to Docker Hub on main branch
- Docker image vulnerability scanning with Trivy
- Build caching for faster builds
- Semantic versioning support

**Required Secrets:**
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`

**Usage:** Automatic on main branch commits and version tags

---

#### **codeql.yml** - Security Analysis
Runs on: Push, PRs, and weekly schedule (Monday midnight)

**Features:**
- CodeQL analysis for Python and JavaScript
- Dependency review on PRs
- Snyk security scanning
- SARIF report upload

**Optional Secrets:**
- `SNYK_TOKEN` (for enhanced Snyk features)

**Usage:** Automatic security scanning

---

### Release Management

#### **release.yml** - Release Automation
Runs on: Version tags (v*) and manual trigger

**Features:**
- Automated changelog generation
- GitHub release creation
- PyPI package publishing
- Semantic release notes

**Required Secrets:**
- `PYPI_TOKEN` (for PyPI publishing)

**Usage:**
```bash
# Create a new release
git tag v0.9.7
git push origin v0.9.7

# Or trigger manually from Actions tab
```

---

### Documentation

#### **docs.yml** - Documentation Management
Runs on: Changes to docs/ or .md files

**Features:**
- Markdown link validation
- Markdown linting
- MkDocs site building
- Spell checking
- Documentation artifact upload

**Usage:** Automatic on documentation changes

---

### Performance & Quality

#### **performance.yml** - Performance Testing
Runs on: Push, PRs, weekly schedule, and manual trigger

**Features:**
- Performance benchmarking
- Memory profiling
- Code complexity metrics (Radon, Lizard)
- Load testing with Locust
- PR comments with metrics

**Usage:** Automatic weekly, or trigger manually for load tests

---

### Automation

#### **auto-update.yml** - Dependency Management
Runs on: Weekly schedule (Monday) and manual trigger

**Features:**
- Automatic dependency updates
- GitHub Actions version updates
- Security vulnerability detection
- Auto-created PRs for updates
- Security issue creation

**Usage:** Runs automatically weekly

---

#### **pr-automation.yml** - PR Management
Runs on: PR events and comments

**Features:**
- Auto-labeling based on file changes
- PR size labeling (XS, S, M, L, XL)
- Semantic PR title checking
- Auto-reviewer assignment
- Stale PR detection
- Merge conflict checking
- PR command bot (/rerun, /format)

**Usage:** Automatic on PR activity

---

## 🚀 Getting Started

### Prerequisites

1. **Required Repository Secrets:**
   ```
   DOCKER_USERNAME      # Docker Hub username
   DOCKER_PASSWORD      # Docker Hub password or token
   PYPI_TOKEN          # PyPI API token (for releases)
   SNYK_TOKEN          # Snyk API token (optional)
   ```

2. **Enable GitHub Actions:**
   - Go to Settings → Actions → General
   - Allow all actions and reusable workflows
   - Enable workflow permissions (Read and write)

### Setting Up Secrets

1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each required secret

### Branch Protection

Recommended branch protection rules for `main`:

```yaml
- Require pull request before merging
- Require status checks to pass:
  - Test Python 3.11
  - Lint and Code Quality
  - Security Scan
- Require branches to be up to date
```

## 📊 Workflow Status Badges

Add these to your README.md:

```markdown
![CI](https://github.com/agent0ai/agent-zero/workflows/CI/badge.svg)
![Docker](https://github.com/agent0ai/agent-zero/workflows/Docker%20Build%20and%20Push/badge.svg)
![CodeQL](https://github.com/agent0ai/agent-zero/workflows/CodeQL/badge.svg)
```

## 🔧 Customization

### Modifying Workflows

1. **Change Python versions:**
   Edit matrix in `ci.yml`:
   ```yaml
   matrix:
     python-version: ["3.10", "3.11", "3.12"]
   ```

2. **Add new labels:**
   Edit `.github/labeler.yml`

3. **Customize Docker platforms:**
   Edit `docker.yml`:
   ```yaml
   platforms: linux/amd64,linux/arm64,linux/arm/v7
   ```

4. **Adjust schedule:**
   Edit cron expressions:
   ```yaml
   cron: '0 0 * * 1'  # Every Monday at midnight
   ```

### Creating Custom Workflows

1. Create new file in `.github/workflows/`
2. Follow the template:
   ```yaml
   name: My Custom Workflow
   
   on:
     push:
       branches: [ main ]
   
   jobs:
     my-job:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - name: Run my task
           run: echo "Hello World"
   ```

## 🐛 Troubleshooting

### Common Issues

**1. Workflow not triggering**
- Check branch filters in workflow file
- Verify Actions are enabled in repo settings
- Check workflow file syntax with yamllint

**2. Docker build failing**
- Verify Docker Hub credentials
- Check Dockerfile syntax
- Review build logs in Actions tab

**3. Tests failing**
- Check Python version compatibility
- Verify all dependencies are in requirements.txt
- Review test logs for specific errors

**4. Permission denied errors**
- Update workflow permissions in Settings → Actions
- Grant write permissions for specific workflows

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Docker Actions](https://docs.docker.com/build/ci/github-actions/)
- [CodeQL Documentation](https://codeql.github.com/docs/)

## 🤝 Contributing

When adding new workflows:

1. Test in a fork first
2. Document all required secrets
3. Add meaningful job and step names
4. Include error handling
5. Update this README
6. Add status badges if applicable

## 📝 Workflow Maintenance

### Weekly Tasks
- Review security scan results
- Check for workflow failures
- Update stale dependencies

### Monthly Tasks
- Review and update GitHub Actions versions
- Audit workflow efficiency
- Update documentation

### Quarterly Tasks
- Review all workflow configurations
- Optimize workflow execution times
- Update best practices

---

**Note:** All workflows are designed to be safe by default. They won't make destructive changes without explicit configuration or manual triggers.

For questions or issues with workflows, please open an issue or reach out to the maintainers.
