# TODO

## Phase 1: Project Foundation ✓ COMPLETE

- [x] Create `pyproject.toml` with dependencies and project metadata
- [x] Set up directory structure (`mohtion/`, `tests/`)
- [x] Configure development tools (ruff, mypy, pytest)
- [x] Create `mohtion/__init__.py` with version info
- [x] Set up Docker and docker-compose for local development

## Phase 2: Core Models & Config ✓ COMPLETE

- [x] `models/target.py` - TechDebtTarget dataclass (file, line range, debt type, severity)
- [x] `models/bounty.py` - BountyResult dataclass (target, branch, PR url, status)
- [x] `models/repo_config.py` - RepoConfig (parsed from .mohtion.yaml)
- [ ] `models/installation.py` - GitHub App installation data (deferred)

## Phase 3: GitHub App Integration ✓ COMPLETE

- [x] Register GitHub App (manually, document the process)
- [x] `integrations/github_app.py` - App authentication, JWT generation
- [x] `integrations/github_api.py` - Clone repo, create branch, push, open PR
- [x] Webhook signature verification

## Phase 4: Web Service ✓ COMPLETE

- [x] `web/app.py` - FastAPI application setup
- [x] `web/routes/webhooks.py` - Handle installation, push, and scheduled events
- [ ] `web/routes/api.py` - REST API for status/config (stretch goal)
- [x] Health check endpoint

## Phase 5: Background Worker ✓ COMPLETE

- [x] `worker/__main__.py` - Worker entry point
- [x] `worker/tasks.py` - Define scan_repo task
- [ ] `worker/scheduler.py` - Periodic scan scheduling per repo (stretch goal)
- [x] Job queue setup (Redis + ARQ)

## Phase 6: LLM Integration ✓ COMPLETE

- [x] `llm/client.py` - Claude API wrapper
- [x] Prompt templates for code analysis
- [x] Prompt templates for refactoring
- [x] Prompt templates for error analysis (self-healing)

## Phase 7: Analyzers (Debt Detection) 🔄 IN PROGRESS

- [x] `analyzers/base.py` - Abstract Analyzer base class
- [x] `analyzers/complexity.py` - Cyclomatic complexity analyzer
- [ ] `analyzers/type_checker.py` - Missing type hints (Python)
- [ ] `analyzers/duplicate.py` - Duplicate code detection
- [ ] `analyzers/deprecation.py` - Deprecated patterns (stretch goal)

## Phase 8: Agent Core ✓ COMPLETE

- [x] `agent/scanner.py` - Orchestrate analyzers, rank targets by priority
- [x] `agent/refactor.py` - LLM-driven code transformation
- [x] `agent/verifier.py` - Run tests in container, capture logs, self-heal
- [x] `agent/orchestrator.py` - Main loop: scan → refactor → verify → PR

## Phase 9: Containerized Test Execution

- [ ] Dockerfile for running target repo tests in isolation
- [ ] Sandboxed execution environment
- [ ] Capture stdout/stderr for self-healing analysis

## Phase 10: Database & Persistence

- [ ] Database schema (installations, repos, bounties, scan history)
- [ ] SQLAlchemy models or raw SQL
- [ ] Migrations setup (Alembic)

## Phase 11: Testing

- [ ] Unit tests for analyzers
- [ ] Unit tests for agent components
- [ ] Integration tests for GitHub API operations (mocked)
- [ ] End-to-end test with sample repo

## Phase 12: Deployment & DevOps

- [ ] Production Dockerfile
- [ ] docker-compose.yml for full stack (web, worker, redis, postgres)
- [ ] Deployment guide (Railway, Fly.io, or AWS)
- [ ] Environment variable documentation

## Phase 13: Polish & Documentation

- [ ] Finalize README with real usage
- [ ] GitHub App installation instructions
- [ ] Self-hosting guide

---

## Current Priority

**Phase 11 (MVP Testing)** - Test the full agent loop end-to-end before expanding features.

## Phase 11: MVP Testing & Validation ✅ COMPLETE

- [x] Create `.env` file with GitHub App credentials
- [x] Fix GitHub App private key base64 encoding
- [x] Fix GitHub JWT timing issue (exp too far in future)
- [x] Verify web service health endpoint
- [x] Test webhook signature verification
- [x] Manual test: Run full agent loop on sample repository
- [x] Monitor full agent loop execution (scan → refactor → verify → self-heal)
- [x] Debug and fix runtime issues (JWT, credentials, Windows permissions)
- [x] Document testing process

### MVP Test Results
- ✅ Full agent loop executed successfully
- ✅ Scanner found 3 tech debt targets
- ✅ LLM refactoring worked (3 API calls)
- ✅ Self-healing attempted (2 retries)
- ✅ Safety mechanism validated (no PR when tests fail)
- ⚠️ PR creation blocked by missing tests in test repo

## Phase 12: Production Readiness 🔄 IN PROGRESS

- [x] Test on repository with actual test suite
- [x] Verify PR creation end-to-end
- [x] Fix verifier to use `python -m pytest` instead of `pytest`
- [x] Add automatic dependency installation from requirements.txt
- [ ] Set up PostgreSQL database for persistence
- [ ] Add database migrations (Alembic)
- [ ] Enable Docker deployment (fix virtualization requirement)
- [ ] Deploy to cloud (Railway, Fly.io, or AWS)
- [ ] Set up webhook automation for continuous monitoring
- [ ] Add monitoring and logging infrastructure

### Phase 12 Test Results ✅
- ✅ Created test repository (test-for-mohtion) with passing tests
- ✅ Full agent loop executed successfully
- ✅ Dependencies auto-installed from requirements.txt
- ✅ Scanner found 5 tech debt targets
- ✅ LLM refactoring reduced complexity from 13 to lower
- ✅ Tests passed after refactoring
- ✅ **FIRST PR CREATED**: https://github.com/JulianCruzet/test-for-mohtion/pull/1
- ✅ All MVP components validated and working in production scenario
