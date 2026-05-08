<div align="center">

# Marketing Analytics Ai MCP

**MCP server for marketing analytics ai mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-marketing-analytics-ai-mcp)](https://pypi.org/project/meok-marketing-analytics-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Marketing Analytics Ai MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `campaign_roi` | Calculate comprehensive campaign ROI including ROAS, CPA, CPC, CPM, |
| `ab_test_analyze` | Analyze A/B test results with statistical significance testing. |
| `funnel_optimizer` | Analyze a conversion funnel and identify the biggest leak point with |
| `attribution_model` | Apply an attribution model to marketing touchpoints. Distributes conversion |
| `ad_copy_generator` | Generate ad copy variants tailored to a specific platform with proper |

## Installation

```bash
pip install meok-marketing-analytics-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "marketing-analytics-ai-mcp": {
      "command": "python",
      "args": ["-m", "meok_marketing_analytics_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 5 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
