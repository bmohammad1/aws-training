"""
JSON to Parquet Converter
Converts any nested JSON file to Parquet format using pandas and pyarrow.
Supports command-line configuration for input file, output directory, and compression.
"""

import json
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
import logging
import argparse
import sys
from typing import Dict, Any, List
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def flatten_json(nested_json: Dict[str, Any], separator: str = '_') -> Dict[str, Any]:
    """
    Flatten a nested JSON object into a single-level dictionary.
    
    Args:
        nested_json: The nested JSON object to flatten
        separator: String to use for separating nested keys
    
    Returns:
        Flattened dictionary
    """
    def _flatten(obj: Any, parent_key: str = '') -> Dict[str, Any]:
        items = []
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_key = f"{parent_key}{separator}{key}" if parent_key else key
                items.extend(_flatten(value, new_key).items())
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_key = f"{parent_key}{separator}{i}" if parent_key else str(i)
                items.extend(_flatten(item, new_key).items())
        else:
            return {parent_key: obj}
        
        return dict(items)
    
    return _flatten(nested_json)


def normalize_items_to_dataframe(order_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Extract and normalize the items array into a separate DataFrame.
    
    Args:
        order_data: The order JSON data
    
    Returns:
        DataFrame containing normalized items data
    """
    items = order_data.get('order', {}).get('items', [])
    normalized_items = []
    
    for item in items:
        flattened_item = flatten_json(item)
        # Add order-level information to each item
        flattened_item['order_id'] = order_data.get('order', {}).get('orderId')
        flattened_item['order_date'] = order_data.get('order', {}).get('orderDate')
        normalized_items.append(flattened_item)
    
    return pd.DataFrame(normalized_items)


def create_order_summary_dataframe(order_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Create a DataFrame for the main order summary (excluding items array).
    
    Args:
        order_data: The order JSON data
    
    Returns:
        DataFrame containing order summary data
    """
    # Create a copy of order data without the items array
    order_summary = order_data.copy()
    if 'order' in order_summary and 'items' in order_summary['order']:
        # Keep just the count of items instead of the full array
        order_summary['order']['items_count'] = len(order_summary['order']['items'])
        del order_summary['order']['items']
    
    flattened_order = flatten_json(order_summary)
    return pd.DataFrame([flattened_order])


def convert_json_to_parquet(
    json_file_path: str,
    output_dir: str = None,
    compression: str = 'snappy'
) -> Dict[str, str]:
    """
    Convert JSON file to Parquet format with proper schema optimization.
    
    Args:
        json_file_path: Path to the input JSON file
        output_dir: Directory to save Parquet files (defaults to same directory as JSON)
        compression: Compression algorithm to use ('snappy', 'gzip', 'brotli', 'lz4')
    
    Returns:
        Dictionary with paths to created Parquet files
    """
    try:
        # Load JSON data
        logger.info(f"Loading JSON file: {json_file_path}")
        with open(json_file_path, 'r', encoding='utf-8') as f:
            order_data = json.load(f)
        
        # Set output directory
        if output_dir is None:
            output_dir = Path(json_file_path).parent
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        created_files = {}
        
        # 1. Create order summary Parquet file
        logger.info("Creating order summary DataFrame...")
        order_df = create_order_summary_dataframe(order_data)
        
        # Optimize data types
        for col in order_df.columns:
            if order_df[col].dtype == 'object':
                try:
                    # Try to convert to datetime if it looks like a timestamp
                    if any(keyword in col.lower() for keyword in ['date', 'time', 'timestamp']):
                        if order_df[col].notna().any():
                            order_df[col] = pd.to_datetime(order_df[col], errors='ignore')
                    # Try to convert to numeric if possible
                    elif order_df[col].notna().any():
                        numeric_converted = pd.to_numeric(order_df[col], errors='ignore')
                        if not numeric_converted.equals(order_df[col]):
                            order_df[col] = numeric_converted
                except Exception:
                    pass  # Keep as string if conversion fails
        
        order_parquet_path = output_dir / 'order_summary.parquet'
        logger.info(f"Saving order summary to: {order_parquet_path}")
        order_df.to_parquet(order_parquet_path, compression=compression, index=False)
        created_files['order_summary'] = str(order_parquet_path)
        
        # 2. Create items Parquet file
        logger.info("Creating items DataFrame...")
        items_df = normalize_items_to_dataframe(order_data)
        
        if not items_df.empty:
            # Optimize data types for items
            for col in items_df.columns:
                if items_df[col].dtype == 'object':
                    try:
                        # Convert timestamps
                        if any(keyword in col.lower() for keyword in ['date', 'time', 'timestamp']):
                            if items_df[col].notna().any():
                                items_df[col] = pd.to_datetime(items_df[col], errors='ignore')
                        # Convert numeric columns
                        elif items_df[col].notna().any():
                            numeric_converted = pd.to_numeric(items_df[col], errors='ignore')
                            if not numeric_converted.equals(items_df[col]):
                                items_df[col] = numeric_converted
                    except Exception:
                        pass
            
            items_parquet_path = output_dir / 'order_items.parquet'
            logger.info(f"Saving items to: {items_parquet_path}")
            items_df.to_parquet(items_parquet_path, compression=compression, index=False)
            created_files['order_items'] = str(items_parquet_path)
        
        # 3. Create a single flattened Parquet file (alternative approach)
        logger.info("Creating flattened single-file version...")
        flattened_data = flatten_json(order_data)
        flattened_df = pd.DataFrame([flattened_data])
        
        # Optimize data types for flattened version
        for col in flattened_df.columns:
            if flattened_df[col].dtype == 'object':
                try:
                    if any(keyword in col.lower() for keyword in ['date', 'time', 'timestamp']):
                        if flattened_df[col].notna().any():
                            flattened_df[col] = pd.to_datetime(flattened_df[col], errors='ignore')
                    elif flattened_df[col].notna().any():
                        numeric_converted = pd.to_numeric(flattened_df[col], errors='ignore')
                        if not numeric_converted.equals(flattened_df[col]):
                            flattened_df[col] = numeric_converted
                except Exception:
                    pass
        
        flattened_parquet_path = output_dir / 'order_flattened.parquet'
        logger.info(f"Saving flattened version to: {flattened_parquet_path}")
        flattened_df.to_parquet(flattened_parquet_path, compression=compression, index=False)
        created_files['order_flattened'] = str(flattened_parquet_path)
        
        logger.info("Conversion completed successfully!")
        return created_files
        
    except FileNotFoundError:
        logger.error(f"JSON file not found: {json_file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {e}")
        raise
    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        raise


def get_parquet_info(parquet_file_path: str) -> None:
    """
    Display information about the created Parquet file.
    
    Args:
        parquet_file_path: Path to the Parquet file
    """
    try:
        # Read parquet file metadata
        parquet_file = pq.ParquetFile(parquet_file_path)
        
        print(f"\n=== Parquet File Info: {Path(parquet_file_path).name} ===")
        print(f"Schema:")
        print(parquet_file.schema)
        print(f"\nMetadata:")
        print(f"  - Number of rows: {parquet_file.metadata.num_rows}")
        print(f"  - Number of columns: {parquet_file.metadata.num_columns}")
        print(f"  - File size: {Path(parquet_file_path).stat().st_size:,} bytes")
        
        # Read and display sample data
        df = pd.read_parquet(parquet_file_path)
        print(f"\nSample data (first 3 rows):")
        print(df.head(3).to_string())
        print(f"\nData types:")
        print(df.dtypes.to_string())
        
    except Exception as e:
        logger.error(f"Error reading Parquet file info: {e}")


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert nested JSON files to Parquet format with schema optimization.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python json_to_parquet.py order-summary.json
  python json_to_parquet.py data.json --output my_output_dir
  python json_to_parquet.py large_file.json --compression gzip
  python json_to_parquet.py nested_data.json --output parquet_files --compression brotli
        """
    )
    
    parser.add_argument(
        'json_file',
        help='Path to the JSON file to convert'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='parquet_output',
        help='Output directory for Parquet files (default: parquet_output)'
    )
    
    parser.add_argument(
        '-c', '--compression',
        choices=['snappy', 'gzip', 'brotli', 'lz4'],
        default='snappy',
        help='Compression algorithm to use (default: snappy)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--no-info',
        action='store_true',
        help='Skip displaying file information after conversion'
    )
    
    return parser.parse_args()


def main():
    """Main execution function."""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Configure logging level based on verbose flag
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.getLogger().setLevel(log_level)
    
    json_file_path = args.json_file
    output_directory = args.output
    compression = args.compression
    
    # Validate JSON file path
    json_path = Path(json_file_path)
    if not json_path.exists():
        logger.error(f"JSON file not found: {json_file_path}")
        sys.exit(1)
    
    if not json_path.is_file():
        logger.error(f"Path is not a file: {json_file_path}")
        sys.exit(1)
    
    if json_path.suffix.lower() != '.json':
        logger.warning(f"File doesn't have .json extension: {json_file_path}")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    try:
        # Convert JSON to Parquet
        logger.info(f"Converting {json_file_path} to Parquet format...")
        logger.info(f"Output directory: {output_directory}")
        logger.info(f"Compression: {compression}")
        
        created_files = convert_json_to_parquet(
            json_file_path=json_file_path,
            output_dir=output_directory,
            compression=compression
        )
        
        print("\n" + "="*60)
        print("CONVERSION SUMMARY")
        print("="*60)
        print(f"📄 Source file: {json_file_path}")
        print(f"📁 Output directory: {output_directory}")
        print(f"🗜️  Compression: {compression}")
        
        for file_type, file_path in created_files.items():
            print(f"\n✅ {file_type.replace('_', ' ').title()}: {file_path}")
            if not args.no_info:
                get_parquet_info(file_path)
        
        print(f"\n🎉 Successfully converted JSON to Parquet format!")
        print(f"� Generated {len(created_files)} Parquet file(s)")
        
    except KeyboardInterrupt:
        logger.info("Conversion interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()