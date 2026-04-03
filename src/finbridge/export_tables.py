import argparse

import pandas as pd
import tabula
import os

def extract_and_merge_tables(pdf_path, pages="all"):
    """Extract tables from PDF and merge consecutive tables with the same headers."""
    # extract prefix from the PDF path
    pdf_prefix = os.path.splitext(pdf_path)[0]

    # Extract all tables from the PDF
    tables = tabula.read_pdf(pdf_path, pages=pages, multiple_tables=True)

    # Initialize variables for merging tables
    merged_tables = []
    current_merged_table = None
    current_headers = None

    for i, table in enumerate(tables):
        # Clean up the table - drop empty rows and columns
        table = table.dropna(how='all').dropna(axis=1, how='all')

        if table.empty:
            continue

        # Get the headers of the current table
        headers = list(table.columns)

        # If we have a current merged table and the headers match
        if current_merged_table is not None and headers == current_headers:
            # Append the data (excluding headers) to the current merged table
            current_merged_table = pd.concat([current_merged_table, table], ignore_index=True)
        else:
            # If we have a previous merged table, add it to the list
            if current_merged_table is not None:
                merged_tables.append(current_merged_table)

            # Start a new merged table
            current_merged_table = table
            current_headers = headers

    # Add the last merged table if it exists
    if current_merged_table is not None:
        merged_tables.append(current_merged_table)

    # Save the merged tables to CSV files
    for i, table in enumerate(merged_tables, 1):
        output_path = f"{pdf_prefix}_table{i}.csv"
        table.to_csv(output_path, index=False)
        print(f"Saved merged table {i} to {output_path}")

    return merged_tables


def main():
    parser = argparse.ArgumentParser(description="Extract tables from PDF files")
    parser.add_argument("pdf_path", help="Path to the PDF file")

    args = parser.parse_args()

    extract_and_merge_tables(args.pdf_path)


if __name__ == "__main__":
    main()
