# ...existing code...

import os
from pymongo import MongoClient
from utils import epoch_to_date

proposal_summary_prompt = """Given the proposal data, prepare a summary using the following example

<example>

Summary for Proposal ID: 0xc597c9419671680858a6429b588eb3dbf92305a3fe7e25bc375a0199a14b16ab
Proposed By: 0xE4553b743E74dA3424Ac51f8C1E586fd43aE226F

# Developer Advisory Board Foundation Mission Team Elections

## Description:

This proposal is for the election of 2 roles in the Foundation Mission Team of the Developer Advisory Board, following the approval of the Developer Advisory Board Budget.
The election will use approval voting, allowing voters to select any number of nominees. Candidates can vote for themselves as long as they also vote for the remaining positions.
Candidates:

## Key Points:

* Proposal Created: January 10, 2025
* Vote Cast: January 10 - January 11, 2025 
* Total Voters: 3020
* Proposal Queued: January 31, 2025
* Proposal Executed: February 4, 2025
* Creation Date: January 10, 2025

Execution Date: February 4, 2025

</example>

<proposal>
{}
</proposal>
"""

proposal_list_prompt = """Given the list of proposals, group the proposals with their name using the following example:

<example>
Created Proposals:
* 0x4c50b4d0aa407589ff601b2df4d6652334198badcede5010dd31f5e7779f9291
* 0xa53409c73f413d2b1c6840b5969b75ce1b640d2c5d300b8ae301b2143001df80
* 0xede7ddcbdf8fd093f9d41f1fff775929e3ce293efd64fa32e7925ab9842c05a1

Executed Proposals:
* 0x44a55082d85292f19233aeee549886822828020221c7e30b55359e0e2eb17f82
* 0x6ce4bea69a6eb555c70b313b3070885e34d22e1cd97e72e52de43021ac885051
* 0xe8934eb513daf3d37e88d9e5e6c4d53f189363d1f42ccdb5ad61d0785890a5f7

</example>

<proposals>
{}
</proposals>
"""

def connect_to_mongodb(database_name: str):
    """
    Connect to the MongoDB database using the MONGODB_URI environment variable.

    :param database_name: Name of the database to connect to
    :return: Database object
    """
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = MongoClient(uri)
    db = client[database_name]
    return db

def get_events_count(eventTypes: list[str]):
    """
    Get the count of documents in the 'events' collection based on the event type.
    
    :return: Count of documents in the 'events' collection
    """
    db = connect_to_mongodb("indexer")
    events_collection = db["events"]
    if len(eventTypes) == 0:
      return events_collection.count_documents({})
    else:
      return events_collection.count_documents({"name": { "$in": eventTypes }})

def get_prompt_for_proposals_list(eventTypes: list[str]):
    
    db = connect_to_mongodb("indexer")
    events_collection = db["events"]
    # TODO: Could fetch 10 proposals ids in parallel for each type to have a good mix
    if len(eventTypes) != 0:
      events = list(events_collection.aggregate([
        { "$match": { "name": { "$in": eventTypes } } },
        { "$unwind": "$args" },
        { "$match": { "args.key": "proposalId" } },
        { "$project": { "proposalId": "$args.value._hex", "name": 1, "_id": 0 } },
        { "$limit": 100 },
        { "$sort": { "name": 1 } }
      ]))
      
      return proposal_list_prompt.format(events)
      
    else:
      return "No event types provided. Please specify at least one event type to filter proposals."


def get_total_proposals():
    db = connect_to_mongodb("indexer")
    events_collection = db["events"]
    query = {
      "name": "ProposalCreated",
      }
    return events_collection.count_documents(query)
  
def get_proposal_events(proposalId: str):
    """
    Get all events related to a specific proposalId.
    
    :param proposalId: The ID of the proposal to filter events by
    :return: List of events related to the specified proposalId
    """
    db = connect_to_mongodb("indexer")
    events_collection = db["events"]
    
    query = {
      "args": {
        "$elemMatch": {
          "key": "proposalId",
          "value._hex": proposalId
          }
        }
      }
    
    # Assuming proposalId is stored in the "args" field as a list item with the key: "proposalId"
    # Use `some` operator to match the proposalId in the args field
    
    events = list(events_collection.find(query).sort({ "blockNumber": 1, "logIndex": 1 }))
    
    # Group the events with type, and count the number of events for each type
    # with the first and last block number and log index
    # also add the first and last timestamp
    events_summary = {}
    creation_date = None
    execution_date = None
    event_types = []
    for event in events:
      event_type = event["name"]
      if event_type not in event_types:
        event_types.append(event_type)
      if event_type == "ProposalCreated":
        events_summary["proposed_by"] = event["args"][1]["value"]
        events_summary["description"] = event["args"][6]["value"]
        chunks = events_summary["description"].split("\n\n\n\n") 
        if len(chunks) >= 1:
          events_summary["title"] = chunks[0]
        
      if event_type not in events_summary:
          events_summary[event_type] = {
              "total_voters": 0,
              # "firstBlock": event["blockNumber"],
              # "lastBlock": event["blockNumber"],
              # "firstLogIndex": event["logIndex"],
              # "lastLogIndex": event["logIndex"],
              "firstTimestamp": event["timestamp"],
              "lastTimestamp": event["timestamp"]
          }
          if creation_date == None:
            creation_date = event["timestamp"]
          if execution_date == None:
            execution_date = event["timestamp"]
          creation_date = min(creation_date, event["timestamp"])
          execution_date = max(execution_date, event["timestamp"])
      
      events_summary[event_type]["total_voters"] += 1
      # events_summary[event_type]["lastBlock"] = max(events_summary[event_type]["lastBlock"], event["blockNumber"])
      # events_summary[event_type]["lastLogIndex"] = max(events_summary[event_type]["lastLogIndex"], event["logIndex"])
      events_summary[event_type]["lastTimestamp"] = max(events_summary[event_type]["lastTimestamp"], event["timestamp"])
    
    events_summary["creation_date"] = epoch_to_date(creation_date)
    events_summary["execution_date"] = epoch_to_date(execution_date)
    
    for event_type in event_types:
      events_summary[event_type]["firstTimestamp"] = epoch_to_date(events_summary[event_type]["firstTimestamp"])
      events_summary[event_type]["lastTimestamp"] = epoch_to_date(events_summary[event_type]["lastTimestamp"])
    
    print(events_summary)
    
    summary_propmpt = proposal_summary_prompt.format(events_summary)
    
    return summary_propmpt

# Example usage:
# db = connect_to_mongodb("my_database")
# events_count = get_events_count()
# print(f"Number of documents in 'events' collection: {events_count}")


