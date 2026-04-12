import os

# All paths relative to the directory containing config.py
_BASE = os.path.dirname(os.path.abspath(__file__))

# Load .env file (no python-dotenv dependency required)
_env_file = os.path.join(_BASE, ".env")
if os.path.exists(_env_file):
    with open(_env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                k, v = key.strip(), val.strip()
                if v:
                    os.environ[k] = v  # .env always takes precedence

CONFIG = {
    # LLM API
    "api_base": os.getenv("API_BASE", "https://openrouter.ai/api/v1"),
    "api_key": os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENROUTER_API_KEY", ""),
    "model": os.getenv("MODEL", "claude-sonnet-4-6-20250217"),
    "temperature": 0.2,
    "max_tokens": 4096,

    # Wiki knowledge base
    "wiki_dir": os.path.join(_BASE, "wiki"),
    "index_file": os.path.join(_BASE, "wiki", "INDEX.md"),
    "mastersheet_file": os.path.join(_BASE, "mastersheet", "clients.csv"),

    # External APIs
    "exa_api_key": os.getenv("EXA_API_KEY", ""),

    # Output and trace directories
    "output_dir": os.path.join(_BASE, "outputs"),
    "trace_dir": os.path.join(_BASE, "traces"),

    # Agent behavior limits
    "max_tool_calls_per_turn": 10,
    "max_wiki_article_tokens": 3000,
    "wiki_truncate_at": 2500,
    "max_index_chars": 4000,
    "max_history_messages": 10,

    # Rate limiting
    "rate_limit_chat": "30/minute",
    "rate_limit_feedback": "60/minute",
    "rate_limit_admin": "10/minute",

    # Input sanitization
    "max_query_length": 2000,
    "max_feedback_comment_length": 500,

    # Session persistence
    "session_dir": os.path.join(_BASE, "traces", "sessions"),
    "max_active_sessions": 50,
    "session_expire_hours": 24,

    # Benchmark judge model (different from agent model to reduce bias)
    "judge_model": os.getenv("JUDGE_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),

    # MCP Servers (optional integrations — see docs/mcp-setup.md)
    "mcp_servers": {
        "gmail": {
            "enabled": os.getenv("MCP_GMAIL_ENABLED", "false").lower() == "true",
            "transport": "stdio",
            "command": ["npx", "@anthropic/mcp-gmail"],
        },
        "supabase": {
            "enabled": os.getenv("MCP_SUPABASE_ENABLED", "false").lower() == "true",
            "transport": "stdio",
            "command": ["npx", "supabase-mcp-server"],
            "env": {
                "SUPABASE_URL": os.getenv("SUPABASE_URL", ""),
                "SUPABASE_KEY": os.getenv("SUPABASE_KEY", ""),
            },
        },
    },
}
