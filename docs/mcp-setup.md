# MCP Integration Setup

The CS Agent supports optional [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server integrations. MCP servers run as subprocesses and expose their tools to the agent via JSON-RPC over stdio.

## Prerequisites
- Node.js 18+ and npx (for running MCP servers)
- MCP server packages are downloaded automatically via npx on first run

## Gmail Integration

### Setup
1. Add to your `.env`:
   ```
   MCP_GMAIL_ENABLED=true
   ```
2. On first run, the Gmail MCP server will prompt for OAuth authentication in your browser.
3. Start the agent with `--serve` or in REPL mode — the Gmail MCP server starts automatically.

### Available Tools
When enabled, the Gmail MCP server provides tools for:
- Searching emails
- Reading email content
- Creating drafts
- Sending emails
- Managing labels

### Use Cases
- Automated deadline reminder emails to clients
- Reading incoming client emails for context
- Drafting response emails based on wiki SOPs

## Supabase Integration

### Setup
1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Add to your `.env`:
   ```
   MCP_SUPABASE_ENABLED=true
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_supabase_anon_key
   ```
3. Start the agent — the Supabase MCP server connects automatically.

### Available Tools
When enabled, the Supabase MCP server provides tools for:
- Querying database tables
- Inserting/updating records
- Running SQL queries
- Managing database schema

### Use Cases
- Replace CSV mastersheet with a Supabase table for real-time multi-user access
- Store session data and trace logs in a database
- Build dashboards with live data queries

## Architecture
```
Agent (agent.py)
  |
  |-- execute_tool("wiki_read", args)  --> Local tool (direct function call)
  |-- execute_tool("gmail_send", args) --> MCP fallback
        |
        +-- _call_mcp_tool("gmail", "gmail_send", args)
              |
              +-- JSON-RPC over stdio --> Gmail MCP Server (subprocess)
```

MCP servers are started as child processes when the agent launches (if enabled). The agent sends JSON-RPC requests over stdin/stdout. If a tool name is not found in the local tool registry, the agent falls back to checking running MCP servers.

## Troubleshooting
- **"command not found: npx"** — Install Node.js 18+
- **MCP server fails to start** — Check stderr output in the agent logs
- **Tool calls return errors** — Verify your API keys and permissions in `.env`
- **Gmail OAuth fails** — Ensure your browser can open for the OAuth flow
