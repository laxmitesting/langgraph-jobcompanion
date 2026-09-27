from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from src.cover_letter.state import CoverLetterState
from src.cover_letter.nodes import extract_keywords_node, drafter_node, polisher_node
from src.cover_letter.edges import route_draft

# 1. Initialize the StateGraph with the specific schema
workflow = StateGraph(CoverLetterState)

# 2. Add the nodes to the graph 
workflow.add_node("extract_keywords_node", extract_keywords_node)
workflow.add_node("drafter_node", drafter_node)
workflow.add_node("polisher_node", polisher_node)

# 3. Define the standard flow edges
workflow.add_edge(START, "extract_keywords_node")
workflow.add_edge("extract_keywords_node", "drafter_node")

# 4. Define the conditional edge for the evaluation loop
# LangGraph evaluates route_draft, then uses the dictionary to map the result to the next node
workflow.add_conditional_edges(
    "drafter_node",
    route_draft,
    {
        "polisher_node": "polisher_node",  # If route_draft returns "polisher_node", go to polisher_node
        "drafter_node": "drafter_node"     # If route_draft returns "drafter_node", loop back to drafter_node
    }
)

# 5. Define the terminal edge
workflow.add_edge("polisher_node", END)

# 6. Initialize memory to persist state across sessions (Thread IDs)
memory = MemorySaver()

# 7. Compile the graph into an executable application
compiled_graph = workflow.compile(checkpointer=memory)