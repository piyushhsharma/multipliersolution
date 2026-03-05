#!/usr/bin/env python3
"""
Data analysis script for cleaned customer and order datasets.

This script performs comprehensive analysis including:
- Monthly revenue trends
- Top customers analysis
- Category performance metrics
- Regional analysis
- Customer churn indicators
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
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
    """
    try:
        df = pd.read_csv(path)
        logger.info(f"Successfully loaded {path.name}: {len(df)} rows")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        raise
    except Exception as e:
        logger.error(f"Error loading {path}: {str(e)}")
        raise


def merge_datasets(customers_df: pd.DataFrame, orders_df: pd.DataFrame, 
                  products_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge customer, order, and product datasets.
    
    Args:
        customers_df: Clean customers DataFrame
        orders_df: Clean orders DataFrame
        products_df: Products DataFrame
        
    Returns:
        Merged DataFrame
    """
    logger.info("Merging datasets...")
    
    # Convert customer_id to same type for merging
    customers_df['customer_id'] = customers_df['customer_id'].astype(str)
    orders_df['customer_id'] = orders_df['customer_id'].astype(str)
    
    # Left join orders with customers
    orders_with_customers = pd.merge(
        orders_df, 
        customers_df, 
        on='customer_id', 
        how='left'
    )
    
    # Left join with products
    full_data = pd.merge(
        orders_with_customers,
        products_df,
        left_on='product',
        right_on='product_name',
        how='left'
    )
    
    # Report missing data
    missing_customers = full_data['name'].isna().sum()
    missing_products = full_data['category'].isna().sum()
    
    logger.info(f"Orders with missing customer info: {missing_customers}")
    logger.info(f"Orders with missing product info: {missing_products}")
    
    return full_data


def analyze_monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze monthly revenue trends for completed orders.
    
    Args:
        df: Merged DataFrame
        
    Returns:
        Monthly revenue DataFrame
    """
    logger.info("Analyzing monthly revenue trends...")
    
    # Filter completed orders only
    completed_orders = df[df['status'] == 'completed'].copy()
    
    # Group by month and calculate total revenue
    monthly_revenue = completed_orders.groupby('order_year_month').agg({
        'amount': ['sum', 'count']
    }).reset_index()
    
    # Flatten column names
    monthly_revenue.columns = ['month', 'total_revenue', 'order_count']
    
    # Sort by month
    monthly_revenue = monthly_revenue.sort_values('month')
    
    return monthly_revenue


def analyze_top_customers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze top customers by total spend.
    
    Args:
        df: Merged DataFrame
        
    Returns:
        Top customers DataFrame
    """
    logger.info("Analyzing top customers...")
    
    # Filter completed orders only
    completed_orders = df[df['status'] == 'completed'].copy()
    
    # Group by customer
    customer_analysis = completed_orders.groupby(['customer_id', 'name', 'region']).agg({
        'amount': 'sum',
        'order_id': 'count'
    }).reset_index()
    
    customer_analysis.columns = ['customer_id', 'name', 'region', 'total_spend', 'order_count']
    
    # Sort by total spend and get top 10
    top_customers = customer_analysis.sort_values('total_spend', ascending=False).head(10)
    
    return top_customers


def analyze_category_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze category performance metrics.
    
    Args:
        df: Merged DataFrame
        
    Returns:
        Category performance DataFrame
    """
    logger.info("Analyzing category performance...")
    
    # Filter completed orders only
    completed_orders = df[df['status'] == 'completed'].copy()
    
    # Group by category
    category_analysis = completed_orders.groupby('category').agg({
        'amount': ['sum', 'mean', 'count']
    }).reset_index()
    
    # Flatten column names
    category_analysis.columns = ['category', 'total_revenue', 'avg_order_value', 'order_count']
    
    # Sort by total revenue
    category_analysis = category_analysis.sort_values('total_revenue', ascending=False)
    
    return category_analysis


def analyze_regional_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze regional performance metrics.
    
    Args:
        df: Merged DataFrame
        
    Returns:
        Regional analysis DataFrame
    """
    logger.info("Analyzing regional performance...")
    
    # Filter completed orders only
    completed_orders = df[df['status'] == 'completed'].copy()
    
    # Customer analysis by region
    customer_regions = df[['customer_id', 'region']].drop_duplicates()
    customers_by_region = customer_regions.groupby('region')['customer_id'].count().reset_index()
    customers_by_region.columns = ['region', 'customer_count']
    
    # Order analysis by region
    orders_by_region = completed_orders.groupby('region').agg({
        'order_id': 'count',
        'amount': 'sum'
    }).reset_index()
    orders_by_region.columns = ['region', 'order_count', 'total_revenue']
    
    # Merge customer and order data
    regional_analysis = pd.merge(customers_by_region, orders_by_region, on='region', how='outer')
    
    # Calculate average revenue per customer
    regional_analysis['avg_revenue_per_customer'] = (
        regional_analysis['total_revenue'] / regional_analysis['customer_count']
    ).round(2)
    
    # Fill NaN values
    regional_analysis = regional_analysis.fillna(0)
    
    # Sort by total revenue
    regional_analysis = regional_analysis.sort_values('total_revenue', ascending=False)
    
    return regional_analysis


def add_churn_indicators(df: pd.DataFrame, top_customers_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add churn indicators to top customers.
    
    Args:
        df: Merged DataFrame
        top_customers_df: Top customers DataFrame
        
    Returns:
        Top customers DataFrame with churn indicators
    """
    logger.info("Adding churn indicators...")
    
    # Get current date (use latest order date as reference)
    latest_date = df['order_date'].max()
    cutoff_date = latest_date - timedelta(days=90)
    
    # Filter completed orders
    completed_orders = df[df['status'] == 'completed'].copy()
    
    # Find latest order date for each customer
    latest_orders = completed_orders.groupby('customer_id')['order_date'].max().reset_index()
    latest_orders.columns = ['customer_id', 'latest_order_date']
    
    # Add churn indicator
    latest_orders['churned'] = latest_orders['latest_order_date'] < cutoff_date
    
    # Merge with top customers
    top_customers_with_churn = pd.merge(
        top_customers_df,
        latest_orders[['customer_id', 'churned']],
        on='customer_id',
        how='left'
    )
    
    # Fill missing churn status (customers with no completed orders)
    top_customers_with_churn['churned'] = top_customers_with_churn['churned'].fillna(True)
    
    return top_customers_with_churn


def save_analysis_results(monthly_revenue: pd.DataFrame, top_customers: pd.DataFrame,
                          category_performance: pd.DataFrame, regional_analysis: pd.DataFrame,
                          output_path: Path) -> None:
    """
    Save analysis results to CSV files.
    
    Args:
        monthly_revenue: Monthly revenue DataFrame
        top_customers: Top customers DataFrame
        category_performance: Category performance DataFrame
        regional_analysis: Regional analysis DataFrame
        output_path: Output directory path
    """
    logger.info("Saving analysis results...")
    
    monthly_revenue.to_csv(output_path / 'monthly_revenue.csv', index=False)
    top_customers.to_csv(output_path / 'top_customers.csv', index=False)
    category_performance.to_csv(output_path / 'category_performance.csv', index=False)
    regional_analysis.to_csv(output_path / 'regional_analysis.csv', index=False)
    
    logger.info("All analysis results saved successfully!")


def main():
    """Main function to execute data analysis process."""
    # Define paths
    base_path = Path(__file__).parent
    processed_data_path = base_path / 'data' / 'processed'
    raw_data_path = base_path / 'data' / 'raw'
    
    try:
        # Load data
        logger.info("Loading data for analysis...")
        customers_df = load_data(processed_data_path / 'customers_clean.csv')
        orders_df = load_data(processed_data_path / 'orders_clean.csv')
        products_df = load_data(raw_data_path / 'products.csv')
        
        # Convert date columns
        orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
        customers_df['signup_date'] = pd.to_datetime(customers_df['signup_date'])
        
        # Merge datasets
        full_data = merge_datasets(customers_df, orders_df, products_df)
        
        # Perform analyses
        monthly_revenue = analyze_monthly_revenue(full_data)
        top_customers = analyze_top_customers(full_data)
        category_performance = analyze_category_performance(full_data)
        regional_analysis = analyze_regional_performance(full_data)
        
        # Add churn indicators
        top_customers = add_churn_indicators(full_data, top_customers)
        
        # Save results
        save_analysis_results(
            monthly_revenue, top_customers, 
            category_performance, regional_analysis,
            processed_data_path
        )
        
        # Print summary
        logger.info("\n=== ANALYSIS SUMMARY ===")
        logger.info(f"Total customers analyzed: {len(customers_df)}")
        logger.info(f"Total orders analyzed: {len(orders_df)}")
        logger.info(f"Completed orders: {len(full_data[full_data['status'] == 'completed'])}")
        logger.info(f"Monthly revenue periods: {len(monthly_revenue)}")
        logger.info(f"Categories analyzed: {len(category_performance)}")
        logger.info(f"Regions analyzed: {len(regional_analysis)}")
        logger.info("=" * 50)
        
        logger.info("Data analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Data analysis failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
