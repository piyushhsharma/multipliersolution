#!/usr/bin/env python3
"""
Data cleaning script for customer, order, and product datasets.

This script handles data quality issues including:
- Duplicate records
- Missing values
- Inconsistent formats
- Data validation
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_data(path: Path) -> pd.DataFrame:
    """
    Safely load CSV data with error handling.
    
    Args:
        path: Path to CSV file
        
    Returns:
        pandas DataFrame
        
    Raises:
        FileNotFoundError: If file doesn't exist
        EmptyDataError: If file is empty
    """
    try:
        df = pd.read_csv(path)
        logger.info(f"Successfully loaded {path.name}: {len(df)} rows")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        raise
    except pd.errors.EmptyDataError:
        logger.error(f"File is empty: {path}")
        raise
    except Exception as e:
        logger.error(f"Error loading {path}: {str(e)}")
        raise


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email string
        
    Returns:
        True if email is valid, False otherwise
    """
    if pd.isna(email) or not isinstance(email, str):
        return False
    
    email = str(email).strip()
    return ('@' in email and 
            '.' in email and 
            email.count('@') == 1 and
            not email.startswith('@') and
            not email.endswith('@') and
            not email.startswith('.') and
            not email.endswith('.'))


def parse_date(date_str, date_formats=None):
    """
    Parse date string using multiple formats.
    
    Args:
        date_str: Date string to parse
        date_formats: List of date formats to try
        
    Returns:
        Parsed date or NaT
    """
    if pd.isna(date_str):
        return pd.NaT
    
    if date_formats is None:
        date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m-%d-%Y']
    
    for fmt in date_formats:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except (ValueError, TypeError):
            continue
    
    # Try pandas default parsing as fallback
    try:
        return pd.to_datetime(date_str)
    except (ValueError, TypeError):
        return pd.NaT


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean customer data.
    
    Args:
        df: Raw customers DataFrame
        
    Returns:
        Cleaned customers DataFrame
    """
    logger.info("Cleaning customers data...")
    initial_count = len(df)
    
    # Make a copy to avoid SettingWithCopyWarning
    df_clean = df.copy()
    
    # Remove duplicates keeping most recent signup_date
    df_clean['signup_date'] = df_clean['signup_date'].apply(parse_date)
    df_clean = df_clean.sort_values('signup_date', na_position='last')
    df_clean = df_clean.drop_duplicates(subset=['customer_id'], keep='last')
    
    # Standardize emails to lowercase
    df_clean['email'] = df_clean['email'].astype(str).str.lower().str.strip()
    
    # Create email validation column
    df_clean['is_valid_email'] = df_clean['email'].apply(validate_email)
    
    # Strip whitespace from name and region
    df_clean['name'] = df_clean['name'].str.strip()
    df_clean['region'] = df_clean['region'].str.strip()
    
    # Fill missing region with "Unknown"
    df_clean['region'] = df_clean['region'].fillna('Unknown')
    
    # Parse signup_date to YYYY-MM-DD format
    df_clean['signup_date'] = df_clean['signup_date'].dt.strftime('%Y-%m-%d')
    
    # Convert back to datetime for consistency
    df_clean['signup_date'] = pd.to_datetime(df_clean['signup_date'], errors='coerce')
    
    duplicates_removed = initial_count - len(df_clean)
    logger.info(f"Customers cleaning complete: {duplicates_removed} duplicates removed")
    
    return df_clean


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean order data.
    
    Args:
        df: Raw orders DataFrame
        
    Returns:
        Cleaned orders DataFrame
    """
    logger.info("Cleaning orders data...")
    initial_count = len(df)
    
    # Make a copy to avoid SettingWithCopyWarning
    df_clean = df.copy()
    
    # Parse order_date with multiple formats
    df_clean['order_date'] = df_clean['order_date'].apply(parse_date)
    
    # Drop rows where both order_id AND customer_id are null
    df_clean = df_clean[~(df_clean['order_id'].isna() & df_clean['customer_id'].isna())]
    
    # Fill missing amount using median grouped by product
    product_medians = df_clean.groupby('product')['amount'].median()
    df_clean['amount'] = df_clean.apply(
        lambda row: row['amount'] if pd.notna(row['amount']) 
        else product_medians.get(row['product'], df_clean['amount'].median()),
        axis=1
    )
    
    # Normalize status column
    status_mapping = {
        'done': 'completed',
        'canceled': 'cancelled'
    }
    df_clean['status'] = df_clean['status'].str.lower().replace(status_mapping)
    
    # Ensure status values are in the allowed set
    allowed_statuses = ['completed', 'pending', 'cancelled', 'refunded']
    df_clean['status'] = df_clean['status'].apply(
        lambda x: x if x in allowed_statuses else 'pending'
    )
    
    # Add order_year_month column
    df_clean['order_year_month'] = df_clean['order_date'].dt.strftime('%Y-%m')
    
    rows_dropped = initial_count - len(df_clean)
    logger.info(f"Orders cleaning complete: {rows_dropped} rows dropped")
    
    return df_clean


def generate_cleaning_report(original_df: pd.DataFrame, cleaned_df: pd.DataFrame, 
                           dataset_name: str) -> None:
    """
    Generate and print cleaning report.
    
    Args:
        original_df: Original DataFrame
        cleaned_df: Cleaned DataFrame
        dataset_name: Name of the dataset
    """
    logger.info(f"\n=== {dataset_name.upper()} CLEANING REPORT ===")
    logger.info(f"Rows before cleaning: {len(original_df)}")
    logger.info(f"Rows after cleaning: {len(cleaned_df)}")
    logger.info(f"Rows removed: {len(original_df) - len(cleaned_df)}")
    
    logger.info("\nNull counts before cleaning:")
    logger.info(original_df.isnull().sum().to_string())
    
    logger.info("\nNull counts after cleaning:")
    logger.info(cleaned_df.isnull().sum().to_string())
    logger.info("=" * 50)


def main():
    """Main function to execute data cleaning process."""
    # Define paths
    base_path = Path(__file__).parent
    raw_data_path = base_path / 'data' / 'raw'
    processed_data_path = base_path / 'data' / 'processed'
    
    # Ensure processed directory exists
    processed_data_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load raw data
        logger.info("Loading raw data...")
        customers_raw = load_data(raw_data_path / 'customers.csv')
        orders_raw = load_data(raw_data_path / 'orders.csv')
        
        # Clean data
        customers_clean = clean_customers(customers_raw)
        orders_clean = clean_orders(orders_raw)
        
        # Generate cleaning reports
        generate_cleaning_report(customers_raw, customers_clean, 'customers')
        generate_cleaning_report(orders_raw, orders_clean, 'orders')
        
        # Save cleaned data
        logger.info("Saving cleaned data...")
        customers_clean.to_csv(processed_data_path / 'customers_clean.csv', index=False)
        orders_clean.to_csv(processed_data_path / 'orders_clean.csv', index=False)
        
        logger.info("Data cleaning completed successfully!")
        
    except Exception as e:
        logger.error(f"Data cleaning failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
