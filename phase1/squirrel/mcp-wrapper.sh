#!/usr/bin/env bash
# squirrel MCP wrapper — stdio bridge for Cursor
# Runs squirrel's observe module as a lightweight MCP server over stdio
exec python3 "$(dirname "$0")/mcp-stdio-bridge.py"
