# Marketing Analytics AI MCP Server
**By MEOK AI Labs** | [meok.ai](https://meok.ai)

Marketing analytics toolkit: campaign ROI, A/B test analysis, funnel optimization, attribution modeling, and ad copy generation.

## Tools

| Tool | Description |
|------|-------------|
| `campaign_roi` | Calculate ROI, ROAS, CPA, CPC, CPM with performance assessment |
| `ab_test_analyze` | Statistical significance testing for A/B experiments |
| `funnel_optimizer` | Identify biggest funnel leak with optimization recommendations |
| `attribution_model` | Multi-touch attribution (first, last, linear, time decay, U/W-shaped) |
| `ad_copy_generator` | Platform-specific ad copy with character limits and best practices |

## Installation

```bash
pip install mcp
```

## Usage

### Run the server

```bash
python server.py
```

### Claude Desktop config

```json
{
  "mcpServers": {
    "marketing-analytics": {
      "command": "python",
      "args": ["/path/to/marketing-analytics-ai-mcp/server.py"]
    }
  }
}
```

## Pricing

| Tier | Limit | Price |
|------|-------|-------|
| Free | 30 calls/day | $0 |
| Pro | Unlimited + premium features | $9/mo |
| Enterprise | Custom + SLA + support | Contact us |

## License

MIT
