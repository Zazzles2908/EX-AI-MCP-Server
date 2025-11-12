# GitHub MCP Server Troubleshooting Guide

## Common Issues and Solutions

### 🔑 Authentication Issues

**Problem**: "Authentication failed" or "Invalid token" errors

**Solutions**:
1. **Verify PAT Scopes**: Ensure your PAT has these scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `read:org` (Read org and team membership) 
   - ✅ `read:packages` (Read GitHub Packages)

2. **Check PAT Expiration**: 
   - Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
   - Verify your token hasn't expired

3. **Test PAT Manually**:
   ```bash
   curl -H "Authorization: token YOUR_PAT" https://api.github.com/user
   ```
   If this returns your user info, the PAT is valid.

### 🐳 Docker Issues

**Problem**: "Command not found" or Docker container fails to start

**Solutions**:
1. **Check Docker Installation**:
   ```bash
   docker --version
   docker info
   ```

2. **Pull Image Manually**:
   ```bash
   docker pull ghcr.io/github/github-mcp-server
   ```

3. **Authentication Issues with ghcr.io**:
   ```bash
   docker logout ghcr.io
   docker pull ghcr.io/github/github-mcp-server
   ```

4. **Docker Desktop Status**:
   - Ensure Docker Desktop is running
   - Check system resources (memory/CPU)
   - Try restarting Docker Desktop

### 🔧 Configuration Issues

**Problem**: GitHub tools don't appear in Claude Desktop

**Solutions**:
1. **Verify Configuration File Path**:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Check JSON Syntax**:
   - Use a JSON validator to check syntax
   - Ensure proper quoting and brackets
   - Look for trailing commas

3. **Restart Claude Desktop**:
   - Close Claude Desktop completely
   - Wait a few seconds
   - Restart the application

### 📝 Log Files

**Where to find Claude Desktop logs**:

- **macOS**: `~/Library/Logs/Claude/`
- **Windows**: `%APPDATA%\Claude\logs\`
- **Linux**: `~/.local/share/Claude/logs/`

Look for:
- `claude_desktop.log`
- `mcp.log`
- `stderr.log`

### 🔍 Testing Your Setup

**Quick Verification Steps**:

1. **Ask Claude**:
   ```
   "Can you list my GitHub repositories?"
   ```

2. **Manual Docker Test**:
   ```bash
   docker run --rm \
     -e GITHUB_PERSONAL_ACCESS_TOKEN=YOUR_PAT \
     ghcr.io/github/github-mcp-server \
     --help
   ```

3. **API Test**:
   ```bash
   # Test PAT with GitHub API
   curl -H "Authorization: token YOUR_PAT" \
     https://api.github.com/user/repos \
     | head -20
   ```

### 🛡️ Security Considerations

**PAT Security**:
- Never commit PATs to version control
- Use environment variables when possible
- Rotate PATs every 90 days
- Set file permissions: `chmod 600 config.json`

**Config File Permissions**:
```bash
# Secure your config file
chmod 600 ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### 🆘 Getting Help

**If issues persist**:

1. **Check GitHub MCP Server Issues**: https://github.com/github/github-mcp-server/issues
2. **Review Documentation**: https://github.com/github/github-mcp-server/tree/main/docs
3. **Discord Community**: Join the MCP Discord for community support
4. **GitHub Support**: For PAT and API issues

### 🔄 Alternative Setup Options

**If Docker setup continues to fail**:

1. **Use Remote Server (with limitations)**:
   - Remote servers require OAuth through GitHub Apps
   - Not currently supported for Claude Desktop custom connectors
   - May work with VS Code or other MCP hosts

2. **Alternative MCP Hosts**:
   - **VS Code**: Better Docker support for MCP servers
   - **Cursor**: Good MCP integration
   - **Windsurf**: Supports MCP servers

3. **Native Installation**:
   - Build from source (requires Go development environment)
   - Run without Docker but requires manual dependency management

---

## Quick Reference

### PAT Creation Checklist
- [ ] Go to GitHub Settings > Developer settings > Personal access tokens
- [ ] Generate new token (classic)
- [ ] Add scopes: repo, read:org, read:packages
- [ ] Copy token immediately
- [ ] Store securely

### Configuration Checklist
- [ ] Locate correct config file path
- [ ] Add JSON configuration block
- [ ] Replace YOUR_PAT with actual token
- [ ] Verify JSON syntax
- [ ] Save file
- [ ] Restart Claude Desktop

### Testing Checklist
- [ ] Docker is running
- [ ] Docker image pulls successfully
- [ ] Configuration file exists and is valid
- [ ] PAT has correct scopes
- [ ] Claude Desktop restarted
- [ ] GitHub tools appear in Claude

---

**Remember**: The most common issue is either expired PATs or incorrect JSON configuration. Double-check both before diving into more complex troubleshooting! 🎯