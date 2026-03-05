#!/usr/bin/env python3
"""
FastAPI backend for data analytics dashboard.

This module provides REST API endpoints for accessing
cleaned and analyzed data from the data processing pipeline.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
from pathlib import Path
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Data Analytics API",
    description="API for accessing customer and order analytics data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Define paths
BASE_PATH = Path(__file__).parent.parent
DATA_PATH = BASE_PATH / 'data' / 'processed'


def load_csv_data(filename: str) -> pd.DataFrame:
    """
    Load CSV data with error handling.
    
    Args:
        filename: Name of the CSV file
        
    Returns:
        pandas DataFrame
        
    Raises:
        HTTPException: If file not found or error loading
    """
    try:
        file_path = DATA_PATH / filename
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            raise HTTPException(status_code=404, detail=f"Data file {filename} not found")
        
        df = pd.read_csv(file_path)
        logger.info(f"Successfully loaded {filename}: {len(df)} rows")
        return df
    except pd.errors.EmptyDataError:
        logger.error(f"File is empty: {filename}")
        raise HTTPException(status_code=404, detail=f"Data file {filename} is empty")
    except Exception as e:
        logger.error(f"Error loading {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")


def dataframe_to_response(df: pd.DataFrame) -> JSONResponse:
    """
    Convert DataFrame to JSON response.
    
    Args:
        df: pandas DataFrame
        
    Returns:
        JSONResponse with data
    """
    # Convert DataFrame to dict with records orientation
    data = df.to_dict(orient="records")
    return JSONResponse(content=data)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {"status": "ok"}


@app.get("/api/revenue")
async def get_monthly_revenue():
    """
    Get monthly revenue trend data.
    
    Returns:
        Monthly revenue data with month, total_revenue, and order_count
    """
    try:
        df = load_csv_data("monthly_revenue.csv")
        return dataframe_to_response(df)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_monthly_revenue: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/top-customers")
async def get_top_customers():
    """
    Get top customers by total spend.
    
    Returns:
        Top customers data with customer details and churn status
    """
    try:
        df = load_csv_data("top_customers.csv")
        return dataframe_to_response(df)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_top_customers: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/categories")
async def get_category_performance():
    """
    Get category performance metrics.
    
    Returns:
        Category performance data with revenue and order metrics
    """
    try:
        df = load_csv_data("category_performance.csv")
        return dataframe_to_response(df)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_category_performance: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/regions")
async def get_regional_analysis():
    """
    Get regional analysis data.
    
    Returns:
        Regional analysis data with customer and order metrics
    """
    try:
        df = load_csv_data("regional_analysis.csv")
        return dataframe_to_response(df)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_regional_analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/summary")
async def get_data_summary():
    """
    Get summary statistics of all data.
    
    Returns:
        Summary statistics including total customers, orders, revenue, etc.
    """
    try:
        # Load all data files
        customers_df = load_csv_data("customers_clean.csv")
        orders_df = load_csv_data("orders_clean.csv")
        monthly_revenue_df = load_csv_data("monthly_revenue.csv")
        top_customers_df = load_csv_data("top_customers.csv")
        category_df = load_csv_data("category_performance.csv")
        region_df = load_csv_data("regional_analysis.csv")
        
        # Calculate summary statistics
        summary = {
            "total_customers": len(customers_df),
            "total_orders": len(orders_df),
            "completed_orders": len(orders_df[orders_df['status'] == 'completed']),
            "total_revenue": float(monthly_revenue_df['total_revenue'].sum()),
            "avg_order_value": float(monthly_revenue_df['total_revenue'].sum() / 
                                  len(orders_df[orders_df['status'] == 'completed'])),
            "top_customer_revenue": float(top_customers_df['total_spend'].max()) if len(top_customers_df) > 0 else 0,
            "categories_count": len(category_df),
            "regions_count": len(region_df),
            "date_range": {
                "start_date": monthly_revenue_df['month'].min() if len(monthly_revenue_df) > 0 else None,
                "end_date": monthly_revenue_df['month'].max() if len(monthly_revenue_df) > 0 else None
            }
        }
        
        return JSONResponse(content=summary)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_data_summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 error handler."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 error handler."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
