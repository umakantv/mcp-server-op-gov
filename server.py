from mcp.server.fastmcp import FastMCP
from database import get_events_count, get_total_proposals, get_proposal_events, get_prompt_for_proposals_list

# Create an MCP server
mcp = FastMCP("OP Governance")

@mcp.tool()
def get_proposals_for_type(eventType: list[str]) -> str:
    """
    Get the list of proposals with IDs for a specific event types.
    
    :param eventType: The type of event to list
    :type eventType: str
    
    Event type can have the following values:
    - ProposalCreated
    - ProposalCanceled
    - ProposalQueued
    - VoteCast
    - VoteCastWithParams
    - ProposalExecuted
    - ProposalThresholdSet
    - ProposalTypeUpdated
    
    :return: The number of events of the specified type
    :rtype: int
    
    Example queries:
    - List some proposals that were created
    - What are the proposals that were executed?
    """
    return get_prompt_for_proposals_list(eventType)

@mcp.tool()
def get_number_of_events(eventType: list[str]) -> int:
    """
    Get the number of events for event type or for all events.
    
    :param eventType: The type of events to count
    :type eventType: str
    
    :return: The number of events of the specified type
    :rtype: int

    Event type can have the following values:
    - ProposalCreated
    - ProposalCanceled
    - ProposalQueued
    - VoteCast
    - VoteCastWithParams
    - ProposalExecuted
    - ProposalThresholdSet
    - ProposalTypeUpdated
    
    Example queries:
    - How many proposals were created?
    - How many proposals were executed?
    - How many voters cast voted? (Use ["VoteCast", "VoteCastWithParams"])

    """
    return get_events_count(eventType)

@mcp.tool()
def get_total_distinct_proposals() -> int:
    """
    Get the number of distinct proposals indexed
    
    :return: The number of distinct proposals indexed
    :rtype: int
    
    Example queries:
    - How many distinct proposals are indexed?
    - How many proposals are there in total?
    """
    return get_total_proposals()

@mcp.tool()
def get_propposal_details(proposalId: str) -> str:
    """
    Get the details for a proposal
    
    :return: text that describes a prompt for the LLM
    :rtype: str
    
    Example queries:
    - What are the details for proposal 0x1234?
    - What is the proposal 0x1234 about?
    - Explain the proposal 0x1234
    - Summary or timeline for the proposal 0x1234
    
    """
    return get_proposal_events(proposalId)


# Add a dynamic greeting resource
# @mcp.resource("greeting://{name}")
# def get_greeting(name: str) -> str:
#     """Get a personalized greeting"""
#     return f"Hello, {name}!"
