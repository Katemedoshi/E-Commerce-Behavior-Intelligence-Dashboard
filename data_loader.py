"""
Data Loader Module
Loads and transforms Online Retail.csv for the analytics pipeline
Maps columns: InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_online_retail_data(file_path='Online Retail.csv'):
    """
    Load and transform the Online Retail dataset
    
    Original columns: InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country
    """
    logger.info(f"Loading data from {file_path}...")
    
    # Load CSV
    df = pd.read_csv(file_path, encoding='latin-1')
    
    logger.info(f"Loaded {len(df):,} raw records")
    logger.info(f"Columns: {list(df.columns)}")
    
    # Map columns to standard format
    column_mapping = {
        'InvoiceNo': 'transaction_id',
        'StockCode': 'product_id',
        'Description': 'product_name',
        'Quantity': 'quantity',
        'InvoiceDate': 'transaction_date',
        'UnitPrice': 'unit_price',
        'CustomerID': 'customer_id',
        'Country': 'country'
    }
    
    df = df.rename(columns=column_mapping)
    
    # Convert data types
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    df['customer_id'] = df['customer_id'].astype(str)
    
    # Calculate total amount
    df['total_amount'] = df['quantity'] * df['unit_price']
    
    # Estimate cost (30% of price as typical retail margin)
    df['cost'] = df['unit_price'] * 0.6
    df['profit'] = (df['unit_price'] - df['cost']) * df['quantity']
    
    # Extract date components
    df['year'] = df['transaction_date'].dt.year
    df['month'] = df['transaction_date'].dt.month
    df['quarter'] = df['transaction_date'].dt.quarter
    df['day_of_week'] = df['transaction_date'].dt.dayofweek
    df['month_name'] = df['transaction_date'].dt.month_name()
    df['year_month'] = df['transaction_date'].dt.to_period('M').astype(str)
    
    # Add payment method (estimated - not in original data)
    df['payment_method'] = np.random.choice(
        ['Credit Card', 'Debit Card', 'PayPal', 'Bank Transfer'],
        size=len(df),
        p=[0.5, 0.2, 0.2, 0.1]
    )
    
    # Add shipping method (estimated)
    df['shipping_method'] = np.random.choice(
        ['Standard', 'Express', 'Next Day'],
        size=len(df),
        p=[0.7, 0.2, 0.1]
    )
    
    # Add discount column (0 for most, small discount for some)
    df['discount'] = np.where(
        np.random.random(len(df)) < 0.1,  # 10% of transactions have discount
        np.random.uniform(0.05, 0.2, len(df)),
        0
    )
    
    # Add customer_name (generate from customer_id)
    df['customer_name'] = df['customer_id'].apply(lambda x: f'Customer_{x}')
    
    # Add derived product category based on description keywords
    df['category'] = df['product_name'].apply(categorize_product)
    df['subcategory'] = df['category']  # Simplified - same as category
    
    # Calculate profit margin
    df['profit_margin'] = (df['profit'] / df['total_amount'] * 100).round(2)
    df['profit_margin'] = df['profit_margin'].fillna(0)
    
    # Add price tier
    df['price_tier'] = pd.cut(df['unit_price'],
                              bins=[0, 2, 5, 10, float('inf')],
                              labels=['Budget', 'Mid-range', 'Premium', 'Luxury'])
    
    logger.info(f"Transformed data shape: {df.shape}")
    logger.info(f"Date range: {df['transaction_date'].min()} to {df['transaction_date'].max()}")
    logger.info(f"Unique customers: {df['customer_id'].nunique():,}")
    logger.info(f"Unique products: {df['product_id'].nunique():,}")
    logger.info(f"Total revenue: ${df['total_amount'].sum():,.2f}")
    
    return df


def categorize_product(description):
    """Categorize products based on description keywords"""
    
    if pd.isna(description):
        return 'Other'
    
    description = str(description).upper()
    
    # Define category keywords
    categories = {
        'Kitchen': ['KNIFE', 'SPOON', 'FORK', 'PLATE', 'CUP', 'MUG', 'KITCHEN', 'CAKE', 'TEA', 'COFFEE', 'BOWL'],
        'Home Decor': ['HANGING', 'LANTERN', 'HEART', 'DECORATION', 'PICTURE', 'FRAME', 'CLOCK', 'MIRROR', 'CANDLE'],
        'Garden': ['GARDEN', 'FLOWER', 'PLANT', 'WATERING', 'SEED', 'POT', 'OUTDOOR'],
        'Gifts': ['GIFT', 'CHRISTMAS', 'BIRTHDAY', 'WRAP', 'CARD', 'PRESENT'],
        'Storage': ['BOX', 'BAG', 'BASKET', 'CONTAINER', 'JAR', 'TIN', 'STORAGE'],
        'Textiles': ['CUSHION', 'PILLOW', 'BLANKET', 'CURTAIN', 'TOWEL', 'FABRIC', 'CLOTH'],
        'Toys': ['TOY', 'DOLL', 'GAME', 'PUZZLE', 'PLAYHOUSE', 'BLOCK'],
        'Paper & Crafts': ['PAPER', 'CRAFT', 'PAINT', 'SKETCH', 'NOTEBOOK', 'JOURNAL'],
        'Lighting': ['LIGHT', 'LAMP', 'LANTERN', 'CANDLE'],
        'Seasonal': ['CHRISTMAS', 'EASTER', 'HALLOWEEN', 'VALENTINE', 'SEASONAL']
    }
    
    for category, keywords in categories.items():
        if any(keyword in description for keyword in keywords):
            return category
    
    return 'Other'


def save_processed_data(df, output_dir='data'):
    """Save processed data to CSV files"""
    import os
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save main dataset
    df.to_csv(f'{output_dir}/ecommerce_data.csv', index=False)
    logger.info(f"Saved processed data to {output_dir}/ecommerce_data.csv")
    
    # Save customers
    customers = df.groupby('customer_id').agg({
        'customer_name': 'first',
        'country': 'first',
        'transaction_date': 'min'
    }).reset_index()
    customers.columns = ['customer_id', 'customer_name', 'country', 'first_purchase_date']
    customers.to_csv(f'{output_dir}/customers.csv', index=False)
    
    # Save products
    products = df.groupby('product_id').agg({
        'product_name': 'first',
        'category': 'first',
        'unit_price': 'mean'
    }).reset_index()
    products.to_csv(f'{output_dir}/products.csv', index=False)
    
    # Save transactions
    df.to_csv(f'{output_dir}/transactions.csv', index=False)
    
    logger.info(f"Saved {len(customers):,} customers, {len(products):,} products")
    
    return df


def main():
    """Main function to load and process the retail data"""
    
    # Load and transform
    df = load_online_retail_data('Online Retail.csv')
    
    # Save processed files
    df = save_processed_data(df)
    
    # Print summary
    print("\n" + "="*70)
    print("DATA LOADING COMPLETE")
    print("="*70)
    print(f"Records: {len(df):,}")
    print(f"Customers: {df['customer_id'].nunique():,}")
    print(f"Products: {df['product_id'].nunique():,}")
    print(f"Date Range: {df['transaction_date'].min()} to {df['transaction_date'].max()}")
    print(f"Countries: {df['country'].nunique()}")
    print(f"Categories: {df['category'].nunique()}")
    print(f"Total Revenue: ${df['total_amount'].sum():,.2f}")
    print("="*70)
    
    return df


if __name__ == "__main__":
    main()
