from mcp.server.fastmcp import FastMCP
from database import get_events_count, get_total_proposals, get_proposal_events


proposalId = "0xc597c9419671680858a6429b588eb3dbf92305a3fe7e25bc375a0199a14b16ab"
summary = get_proposal_events(proposalId)

print(summary)