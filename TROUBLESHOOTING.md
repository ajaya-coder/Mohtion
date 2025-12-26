# Mohtion Troubleshooting Guide

This guide covers common issues encountered when setting up and running Mohtion, based on real MVP testing experience.

## GitHub App Authentication Issues

### Error: "401 Unauthorized" when calling GitHub API

**Symptom**: Getting 401 errors when trying to access GitHub API, even though credentials are correct.

**Possible causes**:

#### 1. JWT expiration time too far in future

**Error message**: `"'Expiration time' claim ('exp') is too far in the future"`

**Cause**: The JWT token lifetime (from `iat` to `exp`) exceeds GitHub's maximum allowed time.

**Solution**: This was fixed in `mohtion/integrations/github_app.py` by reducing the JWT expiration:
```python
# Before (caused issues)
payload = {
    "iat": now - 60,  # 660 second total lifetime
    "exp": now + 600,
}

# After (working)
payload = {
    "iat": now,  # 540 second total lifetime
    "exp": now + 540,  # 9 minutes
}
```

#### 2. Private key format issues

**Symptom**: `"Could not parse the provided public key"`

**Cause**: The private key in `.env` is not properly base64 encoded or spans multiple lines.

**Solution**:
1. Use `encode_key.py` to properly encode your private key:
   ```bash
   python encode_key.py path/to/your-key.pem
   ```
2. Copy the ENTIRE base64 string onto ONE line in `.env`
3. Ensure no spaces before or after the `=` sign
4. Verify with `python debug_credentials.py`

**Example of INCORRECT `.env` format**:
```env
GITHUB_PRIVATE_KEY_BASE64=
 LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFb2dJQkFB...
```

**Example of CORRECT `.env` format**:
```env
GITHUB_PRIVATE_KEY_BASE64=LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFb2dJQkFB...
```

#### 3. App not installed on repository

**Symptom**: 401 error when trying to clone a specific repository

**Cause**: GitHub App is not installed on the repository you're trying to access.

**Solution**:
1. Go to your GitHub App settings
2. Click "Install App"
3. Add the repository you want to test
4. Click "Save"

#### 4. Insufficient permissions

**Cause**: GitHub App doesn't have the required permissions.

**Required permissions**:
- **Contents**: Read & write
- **Metadata**: Read-only
- **Pull requests**: Read & write

**Solution**:
1. Go to your GitHub App settings
2. Click "Permissions & events"
3. Update the permissions
4. Save changes
5. Accept the new permissions in your installation

## Anthropic API Issues

### Error: "401 - invalid x-api-key"

**Cause**: Invalid, expired, or incorrectly formatted API key.

**Solution**:
1. Go to https://console.anthropic.com/settings/keys
2. Generate a new API key
3. Update `ANTHROPIC_API_KEY` in `.env`
4. Ensure the key starts with `sk-ant-api03-`
5. Restart any running processes to reload the `.env` file

### Error: "Your credit balance is too low"

**Cause**: No credits in Anthropic account.

**Solution**:
1. Go to https://console.anthropic.com/settings/billing
2. Add credits (minimum $5 recommended for testing)
3. Wait a few minutes for credits to be applied
4. Try again

## Test Verification Issues

### Tests fail / No PR created

**Symptom**: Agent completes refactoring but doesn't create a PR.

**Expected behavior**: This is CORRECT! Mohtion will not create a PR if tests fail.

**Common causes**:

#### 1. Repository has no tests

**How to identify**: Check logs for `"No test command detected"` or pytest exit code 1 with no test output.

**Solution**:
- Add a test suite to your repository
- Or test on a different repository that has tests
- Mohtion is designed to only create PRs when tests pass

#### 2. Tests are actually failing

**How to identify**: Check the test output in logs

**Solution**:
- The self-healing mechanism should attempt to fix (max 2 retries)
- If tests still fail after self-healing, the refactoring is abandoned (by design)
- This is a safety feature - it prevents broken code from being merged

#### 3. Test command not found

**Symptom**: `"Could not detect test command"`

**Solution**: Specify the test command in `.mohtion.yaml`:
```yaml
test_command: "pytest"  # or "npm test", "go test", etc.
```

## Environment and Configuration Issues

### Settings not updating after changing `.env`

**Symptom**: Changes to `.env` file don't take effect.

**Cause**: Python caches the settings using `@lru_cache`.

**Solution**:
```python
# Clear the cache
python -c "from mohtion.config import get_settings; get_settings.cache_clear()"
```

Or restart the Python process/web server.

### Windows Permission Errors

**Symptom**: `PermissionError: [WinError 5] Access is denied` when cleaning up temp directories.

**Cause**: Windows locks files in `.git` directory.

**Impact**: This is a known issue but doesn't affect functionality. The temp directory just won't be deleted.

**Workaround**: Ignore the error or manually delete temp directories later.

## Docker Issues

### "Virtualization support not detected"

**Symptom**: Docker Desktop fails to start on Windows.

**Cause**: Virtualization (Intel VT-x or AMD-V) is not enabled in BIOS.

**Solution**:
1. Restart computer and enter BIOS (usually F2, F10, or Del during boot)
2. Find "Virtualization Technology" or "VT-x" setting
3. Enable it
4. Save and restart
5. Start Docker Desktop

**Alternative**: Run Mohtion locally without Docker for testing (see MVP_QUICKSTART.md).

## Testing and Validation

### "No tech debt targets found"

**Cause**: Code is too clean or threshold is too high.

**Solutions**:

#### Lower the complexity threshold

Edit your test script or `.env`:
```python
# In test script
config = RepoConfig(
    thresholds=Thresholds(
        cyclomatic_complexity=5,  # Lower threshold
    )
)
```

Or in `.env`:
```env
DEFAULT_COMPLEXITY_THRESHOLD=5
```

#### Test on different code

- Try a repository with known complex functions
- Look for functions with lots of nested if statements
- Functions with high branching logic

### Web service won't start

**Symptom**: `uvicorn` command fails or port is already in use.

**Solutions**:

#### Port already in use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

#### Module not found
```bash
# Reinstall dependencies
pip install -e ".[dev]"
```

## Debugging Tips

### Check if credentials are loading correctly

```bash
python debug_credentials.py
```

Expected output:
```
[OK] GITHUB_APP_ID loaded: 12345678
[OK] GITHUB_WEBHOOK_SECRET loaded: whsec_...
[OK] ANTHROPIC_API_KEY loaded: sk-ant-...
[OK] Private key decoded successfully
```

### Test GitHub App installation

```bash
python get_installation_id.py
```

Should show your installation ID and account.

### Check scanner output

```bash
python test_mvp_low_threshold.py
```

Shows what tech debt targets were found without attempting refactoring.

### View full agent loop execution

```bash
python test_full_loop.py
```

Run the complete Plan-Act-Verify loop with detailed logging.

## Getting Help

### Enable debug logging

In `.env`:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

### Check log files

Review console output for detailed error messages and stack traces.

### Common log messages explained

- `"No tech debt targets found"` - Code is clean or threshold too high
- `"Tests failed with code 1"` - Tests didn't pass (expected if no tests exist)
- `"Self-healing attempt X"` - Agent is retrying after test failure (working correctly)
- `"Correctly aborted PR creation"` - Safety mechanism working (no PR when tests fail)

### Still stuck?

1. Check `LOGBOOK.md` for known issues
2. Review `MVP_QUICKSTART.md` for setup steps
3. Verify all environment variables in `.env`
4. Make sure you have credits in both GitHub App and Anthropic accounts
5. Test individual components (credentials, JWT, scanner) separately

## Known Limitations (MVP)

- Windows temp directory cleanup fails (harmless)
- Only Python code analysis (JavaScript/TypeScript coming soon)
- Only complexity analyzer (more analyzers planned)
- No webhook automation yet (manual trigger only)
- No database persistence (memory only)
- Requires local Python execution (cloud deployment planned)

These are expected limitations of the MVP and will be addressed in future phases.
