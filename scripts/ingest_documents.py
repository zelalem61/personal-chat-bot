#!/usr/bin/env python
"""
Document Ingestion Script - Load Portfolio into ChromaDB

LEARNING NOTES:
---------------
This script loads your portfolio document into ChromaDB for RAG retrieval.
Run this after:
1. Starting ChromaDB (docker-compose up -d)
2. Filling in your portfolio.md file

WHAT IT DOES:
1. Reads portfolio.md from the data directory
2. Chunks the content into smaller pieces
3. Generates embeddings using OpenAI
4. Stores chunks + embeddings in ChromaDB

USAGE:
    python scripts/ingest_documents.py

    # Clear existing data and re-ingest
    python scripts/ingest_documents.py --clear

    # Specify a different file
    python scripts/ingest_documents.py --file path/to/document.md
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from portfolio_bot.core.vectorstore import VectorStore
from portfolio_bot.logs.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


async def load_markdown_file(file_path: Path) -> list[dict]:
    """
    Load a markdown file and prepare it for ingestion.

    Args:
        file_path: Path to the markdown file.

    Returns:
        List of document dicts with 'content' and 'metadata'.

    LEARNING NOTE: You might want to preprocess the markdown:
    - Remove frontmatter
    - Split by sections (## headers)
    - Extract metadata from headers
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = file_path.read_text(encoding="utf-8")

    if not content.strip():
        logger.warning(f"File is empty: {file_path}")
        return []

    # Simple approach: treat entire file as one document
    # The VectorStore will chunk it automatically
    documents = [
        {
            "content": content,
            "metadata": {
                "source": file_path.name,
                "file_path": str(file_path),
            },
        }
    ]

    # Advanced: Split by markdown sections
    # This can improve retrieval by keeping related content together
    sections = split_by_sections(content, file_path.name)
    if len(sections) > 1:
        logger.info(f"Found {len(sections)} sections in {file_path.name}")
        documents = sections

    return documents


def split_by_sections(content: str, source: str) -> list[dict]:
    """
    Split markdown content by ## headers.

    Args:
        content: Markdown content.
        source: Source file name for metadata.

    Returns:
        List of document dicts, one per section.

    LEARNING NOTE: Splitting by sections can improve RAG quality because:
    1. Each chunk is about one topic
    2. Headers provide context about the content
    3. Smaller, focused chunks are easier to match
    """
    sections = []
    current_section = ""
    current_header = "Introduction"

    for line in content.split("\n"):
        if line.startswith("## "):
            # Save previous section
            if current_section.strip():
                sections.append({
                    "content": f"# {current_header}\n\n{current_section.strip()}",
                    "metadata": {
                        "source": source,
                        "section": current_header,
                    },
                })
            # Start new section
            current_header = line[3:].strip()
            current_section = ""
        else:
            current_section += line + "\n"

    # Don't forget the last section
    if current_section.strip():
        sections.append({
            "content": f"# {current_header}\n\n{current_section.strip()}",
            "metadata": {
                "source": source,
                "section": current_header,
            },
        })

    return sections


async def ingest_documents(file_path: Path, clear: bool = False) -> None:
    """
    Ingest documents into ChromaDB.

    Args:
        file_path: Path to the markdown file to ingest.
        clear: Whether to clear existing data first.
    """
    logger.info(f"Starting document ingestion from {file_path}")

    # Initialize vector store
    vs = VectorStore()
    await vs.initialize()

    # Clear if requested
    if clear:
        logger.info("Clearing existing documents...")
        await vs.clear()

    # Load documents
    documents = await load_markdown_file(file_path)

    if not documents:
        logger.warning("No documents to ingest. Is your portfolio.md empty?")
        print("\n⚠️  No documents to ingest!")
        print("Please fill in your portfolio.md file first.")
        print(f"Location: {file_path}")
        return

    # Ingest
    logger.info(f"Ingesting {len(documents)} document(s)...")
    count = await vs.add_documents(documents)

    logger.info(f"Successfully ingested {count} chunks")
    print(f"\n✅ Successfully ingested {count} chunks into ChromaDB!")
    print(f"   Total documents in store: {vs.get_document_count()}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Ingest portfolio documents into ChromaDB for RAG retrieval."
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=project_root / "portfolio_bot" / "data" / "portfolio.md",
        help="Path to the markdown file to ingest",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing documents before ingesting",
    )

    args = parser.parse_args()

    print("=" * 50)
    print("Portfolio Bot - Document Ingestion")
    print("=" * 50)
    print(f"File: {args.file}")
    print(f"Clear existing: {args.clear}")
    print()

    try:
        asyncio.run(ingest_documents(args.file, args.clear))
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except ConnectionError as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure ChromaDB is running:")
        print("  docker-compose up -d")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.exception("Ingestion failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
