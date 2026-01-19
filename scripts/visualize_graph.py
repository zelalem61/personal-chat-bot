#!/usr/bin/env python
"""
Graph Visualization Script - Generate Diagram of Bot Architecture

LEARNING NOTES:
---------------
This script generates a visual diagram of the LangGraph structure.
Visualization helps you:
1. Understand the flow of your bot
2. Debug routing issues
3. Document your architecture
4. Explain the system to others

WHAT IT DOES:
1. Creates the compiled graph
2. Exports it as a Mermaid diagram
3. Renders to PNG image

USAGE:
    python scripts/visualize_graph.py

    # Specify output path
    python scripts/visualize_graph.py --output my_graph.png

REQUIREMENTS:
    pip install grandalf  # For graph layout
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def visualize(output_path: Path, show_mermaid: bool = False) -> None:
    """
    Generate graph visualization.

    Args:
        output_path: Where to save the PNG image.
        show_mermaid: Whether to also print the Mermaid syntax.
    """
    from portfolio_bot.core.graph import create_graph
    from portfolio_bot.logs.logger import setup_logging

    setup_logging()

    print("Creating graph...")
    graph = create_graph()

    # Get the underlying graph object
    graph_obj = graph.get_graph()

    # Print Mermaid syntax if requested
    if show_mermaid:
        print("\n=== Mermaid Diagram Syntax ===")
        print(graph_obj.draw_mermaid())
        print("=" * 40)
        print()

    # Generate PNG
    print(f"Generating visualization: {output_path}")
    try:
        png_data = graph_obj.draw_mermaid_png()
        output_path.write_bytes(png_data)
        print(f"✅ Saved to {output_path}")
    except Exception as e:
        print(f"❌ Failed to generate PNG: {e}")
        print("\nMake sure you have the required dependencies:")
        print("  pip install grandalf")
        print("\nAlternatively, copy the Mermaid syntax above and paste it into:")
        print("  https://mermaid.live")
        return

    # Also generate ASCII representation
    print("\n=== Graph Structure ===")
    print_ascii_graph()


def print_ascii_graph():
    """Print an ASCII representation of the graph."""
    graph_ascii = """
    ┌─────────┐
    │  START  │
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │ router  │ ◄── Classifies query: RAG, TOOL, or DIRECT
    └────┬────┘
         │
    ┌────┼────────────────┬───────────────────┐
    │    │                │                   │
    │    ▼                ▼                   ▼
    │ ┌──────────┐  ┌───────────┐    ┌────────────────┐
    │ │retriever │  │tool_agent │    │ response_agent │
    │ └────┬─────┘  └─────┬─────┘    └────────┬───────┘
    │      │              │                   │
    │      │              │                   │
    │      ▼              ▼                   │
    │ ┌────────────────────────────────────┐  │
    │ │          response_agent            │◄─┘
    │ └─────────────────┬──────────────────┘
    │                   │
    │                   ▼
    │              ┌────────┐
    └──────────────│  END   │
                   └────────┘

    Paths:
    • RAG:    router → retriever → response_agent → END
    • TOOL:   router → tool_agent → response_agent → END
    • DIRECT: router → response_agent → END
    """
    print(graph_ascii)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate a visual diagram of the LangGraph structure."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=project_root / "graph_structure.png",
        help="Output path for the PNG image",
    )
    parser.add_argument(
        "--mermaid",
        action="store_true",
        help="Also print the Mermaid diagram syntax",
    )

    args = parser.parse_args()

    print("=" * 50)
    print("Portfolio Bot - Graph Visualization")
    print("=" * 50)
    print()

    visualize(args.output, args.mermaid)


if __name__ == "__main__":
    main()
