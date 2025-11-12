# GitHub MCP Server Setup Guide with Personal Access Token

This guide will walk you through setting up the GitHub MCP Server to access your private repositories using a Personal Access Token (PAT) with Claude Desktop.

## Prerequisites

Before starting, ensure you have:
- **Claude Desktop** (latest version) installed
- **Docker** installed and running
- A **GitHub account** with access to the repositories you want to work with

## Step 1: Create a Personal Access Token (PAT)

### 1.1 Generate Your PAT

1. Go to [GitHub Personal Access Tokens](https://github.com/settings/personal-access-tokens/new)
2. Click **"Generate new token (classic)"**
3. Fill in the required information:
   - **Note**: "Claude Desktop MCP Access"
   - **Expiration**: Choose your preferred duration
   - **Owner**: Select your GitHub account

### 1.2 Configure PAT Scopes

Select the following scopes to allow access to your private repositories:

✅ **Required Scopes:**
- `repo` - Full control of private repositories
- `read:org` - Read org and team membership
- `read:packages` - Read GitHub Packages

### 1.3 Generate and Save Your Token

1. Click **"Generate token"** at the bottom
2. **IMPORTANT**: Copy the token immediately - GitHub will only show it once
3. Store it securely (you'll need it for the configuration)

## Step 2: Configure Claude Desktop

### 2.1 Locate Your Configuration File

Your `claude_desktop_config.json` file is located at:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 2.2 Add GitHub MCP Server Configuration

Add the following JSON configuration to your `claude_desktop_config.json` file. **Replace `YOUR_GITHUB_PAT_HERE` with your actual PAT**:

```json
{
  "mcp": {
    "inputs": [
      {
        "type": "promptString",
        "id": "github_token",
        "description": "GitHub Personal Access Token",
        "password": true
      }
    ],
    "servers": {
      "github": {
        "command": "docker",
        "args": [
          "run",
          "-i",
          "--rm",
          "-e",
          "GITHUB_PERSONAL_ACCESS_TOKEN",
          "ghcr.io/github/github-mcp-server"
        ],
        "env": {
          "GITHUB_PERSONAL_ACCESS_TOKEN": "${input:github_token}"
        }
      }
    }
  }
}
```

### 2.3 Alternative: Complete Configuration File

If your `claude_desktop_config.json` file is empty or you want to start fresh, here's a complete example:

```json
{
  "mcp": {
    "inputs": [
      {
        "type": "promptString",
        "id": "github_token",
        "description": "GitHub Personal Access Token",
        "password": true
      }
    ],
    "servers": {
      "github": {
        "command": "docker",
        "args": [
          "run",
          "-i",
          "--rm",
          "-e",
          "GITHUB_PERSONAL_ACCESS_TOKEN",
          "ghcr.io/github/github-mcp-server"
        ],
        "env": {
          "GITHUB_PERSONAL_ACCESS_TOKEN": "${input:github_token}"
        }
      }
    }
  }
}
```

## Step 3: Test the Connection

### 3.1 Restart Claude Desktop

1. **Close Claude Desktop completely**
2. **Restart the application**
3. Claude will prompt you for your GitHub PAT when it starts

### 3.2 Verify GitHub Access

Try asking Claude to help with a repository task, for example:

```
"Can you list the private repositories I have access to on GitHub?"
```

Or:

```
"What are the recent pull requests in my private repository [repository-name]?"
```

## Step 4: Troubleshooting

### 4.1 PAT Issues

**Problem**: Authentication fails
**Solution**: 
- Verify your PAT has the correct scopes (`repo`, `read:org`, `read:packages`)
- Ensure the PAT hasn't expired
- Check that you're using the correct PAT (tokens are only shown once)

### 4.2 Docker Issues

**Problem**: Server not starting
**Solution**:
- Ensure Docker Desktop is running
- Try pulling the image manually:
  ```bash
  docker pull ghcr.io/github/github-mcp-server
  ```
- If authentication issues occur:
  ```bash
  docker logout ghcr.io
  ```

### 4.3 Configuration Issues

**Problem**: GitHub tools not appearing in Claude
**Solution**:
- Verify JSON syntax in your config file
- Check the config file location is correct
- Review Claude Desktop logs:
  - **macOS**: `~/Library/Logs/Claude/`
  - **Windows**: `%APPDATA%\Claude\logs\`

### 4.4 Compatibility Issues

**Note**: Some users report compatibility issues between Claude Desktop and Docker-based MCP servers. If you experience problems:
- Verify you're using the latest version of Claude Desktop
- Check Docker Desktop is up to date
- Consider trying alternative MCP hosts like VS Code if issues persist

## Security Best Practices

### PAT Security
- **Never commit PATs** to version control
- **Use environment variables** when possible
- **Rotate PATs regularly** (every 90 days recommended)
- **Use separate tokens** for different projects/purposes
- **Set appropriate file permissions** on config files (chmod 600)

### Configuration File Security
```bash
# Secure your config file
chmod 600 ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

## Available GitHub MCP Tools

Once connected, you can use Claude to help with:

- **Repository Management**: List, create, delete repositories
- **Issue Management**: Create, update, close, and search issues
- **Pull Request Operations**: Create, review, merge pull requests
- **Code Analysis**: Search code, analyze repositories
- **Workflow Automation**: Trigger GitHub Actions, manage CI/CD
- **Team Collaboration**: Manage organizations, teams, and permissions

## Next Steps

After successful setup, you can:

1. **Explore available tools** by asking Claude to show GitHub-related capabilities
2. **Configure security modes** if needed:
   - **Read-only mode**: Add `--read-only` flag for safety
   - **Lockdown mode**: Add `--lockdown-mode` flag for restricted access
3. **Customize tool access** using toolsets configuration for specific functionality

## Support and Resources

- **GitHub MCP Server Repository**: https://github.com/github/github-mcp-server
- **Documentation**: https://github.com/github/github-mcp-server/tree/main/docs
- **GitHub Docs - Personal Access Tokens**: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
- **Docker Installation**: https://www.docker.com/

---

**Ready to connect your AI assistant to your GitHub repositories!** 🎉