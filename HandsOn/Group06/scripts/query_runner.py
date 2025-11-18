"""
SPARQL Query Runner for Madrid Bus Network RDF Data

This version loads the RDF graph using rdflib and executes each query
contained in the SPARQL files under `rdf/`. By default it works with the
small sample datasets so we can iterate quickly, but the `--rdf` flag can
point to any other file (TTL/NT/etc.).

Usage examples:
    python3 query_runner.py
    python3 query_runner.py --links
    python3 query_runner.py --rdf path/to/data.ttl --sparql path/to/queries.sparql
"""

import argparse
import time
from pathlib import Path

from rdflib import Graph


def run_query(graph, query_dict, query_num):
    """Execute a SPARQL query using rdflib.Graph.query."""
    comment = query_dict["comment"] or "SPARQL query"
    query = query_dict["query"]

    print(f"\n{'=' * 70}")
    print(f"QUERY {query_num}: {comment}")
    print(f"{'=' * 70}")

    start = time.time()

    try:
        results = graph.query(query)
    except Exception as exc:
        print(f"✗ Query failed: {exc}")
        return

    rows = list(results)
    elapsed = time.time() - start
    print(f"✓ Completed in {elapsed:.2f}s · {len(rows):,} result(s)")

    if not rows:
        return

    preview = rows[: min(5, len(rows))]
    for idx, row in enumerate(preview, 1):
        formatted = ", ".join(str(value) for value in row)
        print(f"  {idx}. {formatted}")


def parse_queries(sparql_file):
    """Parse SPARQL file and extract queries"""
    queries = []
    prefixes = []
    current_query = []
    current_comment = []
    in_prefix_section = True

    with open(sparql_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()

            if not line:
                continue

            # Collect PREFIX declarations
            if line.startswith("PREFIX"):
                if in_prefix_section:
                    prefixes.append(line)
                continue

            # End of prefix section
            if in_prefix_section and line.startswith("#") and "=" in line:
                in_prefix_section = False

            if in_prefix_section:
                continue

            # Query separator
            if line.startswith("#") and "=" in line:
                if current_query:
                    query_text = "\n".join(prefixes + current_query)
                    comment_text = " ".join(current_comment)
                    queries.append({"comment": comment_text, "query": query_text})
                    current_query = []
                    current_comment = []
                continue

            # Comment lines
            if line.startswith("#"):
                comment_line = line.lstrip("#").strip()
                if comment_line:
                    current_comment.append(comment_line)
                continue

            # Query content
            if line:
                current_query.append(line)

        # Save last query
        if current_query:
            query_text = "\n".join(prefixes + current_query)
            comment_text = " ".join(current_comment)
            queries.append({"comment": comment_text, "query": query_text})

    return queries


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description="Validate Madrid Bus Network RDF data using SPARQL queries"
    )
    parser.add_argument(
        "--links",
        action="store_true",
        help="Use RDF dataset with Wikidata links and corresponding queries",
    )
    parser.add_argument(
        "--rdf",
        type=Path,
        help="Path to the RDF file to query (overrides defaults)",
    )
    parser.add_argument(
        "--sparql",
        type=Path,
        help="Path to the SPARQL file to execute (overrides defaults)",
    )
    args = parser.parse_args()

    base_dir = Path(__file__).parent.parent
    rdf_dir = base_dir / "rdf"

    default_rdf = rdf_dir / "madrid-bus-data-sample-500.ttl"
    default_sparql = rdf_dir / "queries.sparql"
    if args.links:
        default_rdf = rdf_dir / "madrid-bus-data-with-links-sample-500.ttl"
        default_sparql = rdf_dir / "queries-with-links.sparql"

    rdf_file = args.rdf if args.rdf else default_rdf
    sparql_file = args.sparql if args.sparql else default_sparql

    if not rdf_file.exists():
        raise FileNotFoundError(f"RDF file not found: {rdf_file}")
    if not sparql_file.exists():
        raise FileNotFoundError(f"SPARQL file not found: {sparql_file}")

    print("\n" + "=" * 70)
    print("RDF Data Validator - Madrid Bus Network")
    print(f"Mode: {'WITH Wikidata Links' if args.links else 'Base Dataset'}")
    print("=" * 70)

    print(f"\nLoading RDF graph from {rdf_file} ...")
    graph = Graph()
    suffix = rdf_file.suffix.lower()
    rdf_format = None
    if suffix in {".ttl", ".turtle"}:
        rdf_format = "turtle"
    elif suffix in {".nt", ".ntriples"}:
        rdf_format = "nt"
    elif suffix in {".rdf", ".xml"}:
        rdf_format = "xml"
    graph.parse(rdf_file, format=rdf_format)
    print(f"✓ Graph loaded with {len(graph):,} triple(s)")

    queries = parse_queries(sparql_file)
    print(f"\nExecuting {len(queries)} query(ies) from {sparql_file.name}")

    for idx, query_dict in enumerate(queries, 1):
        run_query(graph, query_dict, idx)

    print(f"\n{'=' * 70}")
    print("Completed all queries.")
    print("=" * 70)


if __name__ == "__main__":
    main()
