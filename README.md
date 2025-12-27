# Mohtion

**Autonomous Tech Debt Bounty Hunter**

Mohtion is a cloud-based AI agent that continuously monitors your GitHub repositories, identifies technical debt, and opens Pull Requests with verified fixes.

## 🎉 MVP Status: PRODUCTION VALIDATED

The Mohtion MVP has successfully created its first PR in production! All core components are working:

✅ GitHub App integration
✅ Code scanning & analysis
✅ LLM-powered refactoring
✅ Automatic dependency installation
✅ Test verification
✅ Self-healing on failures
✅ Safety mechanisms (no PR if tests fail)
✅ **PR creation via GitHub API**

**First production PR:** https://github.com/JulianCruzet/test-for-mohtion/pull/1

**Ready to test?** See [MVP_QUICKSTART.md](./MVP_QUICKSTART.md) for a step-by-step guide!

## How It Works

1. **Install** the Mohtion GitHub App on your repositories
2. **Configure** scanning preferences via `.mohtion.yaml` in your repo
3. **Relax** while Mohtion autonomously finds and fixes tech debt

```
┌─────────────────┐
│   GitHub Repo   │
└────────┬────────┘
         │ webhook / scheduled scan
         ▼
┌─────────────────┐
│  Mohtion Cloud  │  Clones repo, runs analysis,
│     Service     │  refactors code, runs tests
└────────┬────────┘
         │ tests pass
         ▼
┌─────────────────┐
│  Opens PR with  │
│  verified fix   │
└─────────────────┘
```

## Core Workflow

### 1. Reconnaissance (Scanning)

Mohtion detects tech debt using:
- **AST analysis** - Cyclomatic complexity, deep nesting, long functions
- **LLM vibe checks** - Semantic issues, code smells, unclear logic

**Targets:**
- Functions with high cyclomatic complexity
- Missing type hints (Python) or interfaces (TypeScript)
- Deprecated library calls or outdated syntax
- Duplicate logic across modules

### 2. Refactoring (Action)

- Creates branch: `mohtion/bounty-[unique-id]`
- Uses LLM to refactor identified code blocks
- Preserves external API and functional behavior

### 3. Verification (Safety)

- **Constraint:** Never opens a PR if tests fail
- Runs the project's test suite
- **Self-healing:** On failure, analyzes logs and retries (max 2 attempts)

### 4. Bounty Claim (PR)

Opens a Pull Request with:
- Specific debt identified
- Summary of refactoring strategy
- Confirmation of passing tests

## Configuration

Add `.mohtion.yaml` to your repository root:

```yaml
# Scanning settings
scan_interval: 24h
max_prs_per_day: 3

# Test command (auto-detected if not specified)
test_command: pytest

# Which analyzers to enable
analyzers:
  - complexity
  - type_hints
  - deprecations
  - duplicates

# Complexity thresholds
thresholds:
  cyclomatic_complexity: 10
  function_length: 50
  nesting_depth: 4
```

## Architecture

- **GitHub App** - Authenticates with repositories, receives webhooks
- **Background Worker** - Clones repos, runs Mohtion agent loop
- **Web Dashboard** - Configure settings, view bounty history (optional)

## Self-Hosting

For private infrastructure or air-gapped environments:

```bash
# Clone and configure
git clone https://github.com/your-username/mohtion.git
cd mohtion

# Set environment variables
export GITHUB_APP_ID=...
export GITHUB_PRIVATE_KEY=...
export ANTHROPIC_API_KEY=...

# Run with Docker
docker-compose up -d
```

## Project Documentation

- **[TODO.md](TODO.md)** - Development roadmap and task tracking
- **[LOGBOOK.md](LOGBOOK.md)** - Session-by-session development log

## License

MIT
