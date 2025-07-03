import time
from langgraph.graph import StateGraph, END
from typing import Dict, Any, TypedDict, List
from typing_extensions import Annotated
import operator

from services.search_service import SearchService


search_service = SearchService()


# Define the state structure
class GraphState(TypedDict):
    messages: List[str]
    output_type: str
    text_search_results: List[str]
    image_search_results: List[str]
    final_answer: str


def router_node(state: GraphState) -> GraphState:
    """Router node that determines the next step based on output_type"""
    print(
        f"Router: Processing with output_type={state.get('output_type', 'unknown')}")
    return state


def text_search_node(state: GraphState) -> GraphState:
    """Text search node implementation"""
    messages = state.get("messages", [])
    if not messages:
        state["text_search_results"] = []
        return state

    query = messages[-1]
    print(f"Text Search: Processing query '{query}'")

    search_start = time.time()
    search_results = search_service.web_search(query)
    search_elapsed = time.time() - search_start
    print(f"Search service completed in {search_elapsed:.2f} seconds")
    # For now, return mock results
    state["text_search_results"] = search_results
    return state


def image_search_node(state: GraphState) -> GraphState:
    """Image search node implementation"""
    messages = state.get("messages", [])
    if not messages:
        state["image_search_results"] = []
        return state

    query = messages[-1]
    print(f"Image Search: Processing query '{query}'")

    # TODO: Implement actual image search logic here
    # For now, return mock results
    state["image_search_results"] = [
        f"Image result 1 for '{query}'", f"Image result 2 for '{query}'"]
    return state


def answer_node(state: GraphState) -> GraphState:
    """Answer node that generates final response"""
    text_results = state.get("text_search_results", [])
    image_results = state.get("image_search_results", [])

    # Generate answer based on available results
    if text_results:
        answer = f"Found {len(text_results)} text results: {', '.join(text_results[:2])}"
    elif image_results:
        answer = f"Found {len(image_results)} image results: {', '.join(image_results[:2])}"
    else:
        answer = "No results found, providing direct answer based on query"

    state["final_answer"] = answer
    print(f"Answer: {answer}")
    return state


def route_decision(state: GraphState) -> str:
    """Conditional routing function"""
    output_type = state.get("output_type", "")
    print(f"Routing decision: output_type='{output_type}'")

    if output_type == "text":
        return "text_search"
    elif output_type == "image":
        return "image_search"
    else:
        return "answer"


def create_graph() -> StateGraph:
    """Create and configure the LangGraph"""
    # Initialize the graph
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("text_search", text_search_node)
    workflow.add_node("image_search", image_search_node)
    workflow.add_node("answer", answer_node)

    # Set entry point
    workflow.set_entry_point("router")

    # Add conditional routing from router
    workflow.add_conditional_edges(
        "router",
        route_decision,
        {
            "text_search": "text_search",
            "image_search": "image_search",
            "answer": "answer"
        }
    )

    # Add edges from search nodes to answer
    workflow.add_edge("text_search", "answer")
    workflow.add_edge("image_search", "answer")

    # Add edge from answer to END
    workflow.add_edge("answer", END)

    # Compile the graph
    return workflow.compile()


def visualize_graph(graph, filename="langgraph_visualization.png"):
    """Visualize the graph using LangGraph's built-in visualization and save to PNG file"""
    try:
        # Generate the mermaid visualization
        mermaid_png = graph.get_graph().draw_mermaid_png()

        # Save to file
        with open(filename, 'wb') as f:
            f.write(mermaid_png)
        print(f"LangGraph visualization saved to {filename}")

    except Exception as e:
        print(f"Error creating LangGraph visualization: {e}")
        print("Make sure you have the required dependencies installed (e.g., pygraphviz, pillow)")


def test_graph(graph):
    """Test the graph with different scenarios"""
    test_cases = [
        {
            "messages": ["Find me some articles about AI"],
            "output_type": "text",
            "text_search_results": [],
            "image_search_results": [],
            "final_answer": ""
        },
        {
            "messages": ["Show me pictures of cats"],
            "output_type": "image",
            "text_search_results": [],
            "image_search_results": [],
            "final_answer": ""
        },
        {
            "messages": ["What is the weather today?"],
            "output_type": "",  # Default case
            "text_search_results": [],
            "image_search_results": [],
            "final_answer": ""
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n=== Test Case {i} ===")
        print(f"Input: {test_case}")

        try:
            result = graph.invoke(test_case)
            print(f"Output: {result}")
        except Exception as e:
            print(f"Error: {e}")


# Example usage
if __name__ == "__main__":
    # Create the graph
    print("Creating LangGraph...")
    graph = create_graph()

    print("Creating LangGraph built-in visualization...")
    visualize_graph(graph)

    # Test the graph
    print("Testing the graph...")
    test_graph(graph)

    print("\nGraph implementation completed successfully!")
