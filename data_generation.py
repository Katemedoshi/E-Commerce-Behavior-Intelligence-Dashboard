"""
Data Generation Module for E-Commerce Dataset
Generates realistic synthetic e-commerce transaction data
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

# Initialize Faker
fake = Faker()

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)


def generate_customers(n_customers=1000):
    """Generate customer data"""
    customers = []
    
    for i in range(n_customers):
        customer = {
            'customer_id': f'CUST_{i+1:05d}',
            'customer_name': fake.name(),
            'email': fake.email(),
            'country': random.choice(['USA', 'UK', 'Canada', 'Germany', 'France', 'Australia', 'Japan', 'India']),
            'registration_date': fake.date_between(start_date='-2 years', end_date='today'),
            'age': random.randint(18, 70),
            'gender': random.choice(['Male', 'Female']),
        }
        customers.append(customer)
    
    return pd.DataFrame(customers)


def generate_products(n_products=200):
    """Generate product catalog"""
    
    categories = {
        'Electronics': ['Laptop', 'Smartphone', 'Headphones', 'Tablet', 'Smartwatch', 'Camera'],
        'Clothing': ['T-Shirt', 'Jeans', 'Jacket', 'Dress', 'Shoes', 'Sweater'],
        'Home & Garden': ['Furniture', 'Decor', 'Kitchen', 'Bedding', 'Lighting', 'Storage'],
        'Sports': ['Fitness Equipment', 'Outdoor Gear', 'Sportswear', 'Bicycle', 'Yoga Mat', 'Dumbbells'],
        'Books': ['Fiction', 'Non-Fiction', 'Educational', 'Comics', 'Magazine', 'Textbook'],
        'Beauty': ['Skincare', 'Makeup', 'Fragrance', 'Hair Care', 'Personal Care', 'Tools']
    }
    
    products = []
    
    for i in range(n_products):
        category = random.choice(list(categories.keys()))
        subcategory = random.choice(categories[category])
        
        # Price based on category
        price_ranges = {
            'Electronics': (50, 2000),
            'Clothing': (10, 200),
            'Home & Garden': (20, 500),
            'Sports': (15, 800),
            'Books': (5, 100),
            'Beauty': (10, 150)
        }
        
        price_range = price_ranges[category]
        base_price = round(random.uniform(price_range[0], price_range[1]), 2)
        
        product = {
            'product_id': f'PROD_{i+1:05d}',
            'product_name': f'{fake.word().title()} {subcategory}',
            'category': category,
            'subcategory': subcategory,
            'price': base_price,
            'cost': round(base_price * random.uniform(0.4, 0.7), 2),
            'stock_quantity': random.randint(0, 500)
        }
        products.append(product)
    
    return pd.DataFrame(products)


def generate_transactions(customers_df, products_df, n_transactions=10000):
    """Generate transaction data"""
    
    transactions = []
    
    # Generate dates over the last 2 years
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    for i in range(n_transactions):
        # Random customer
        customer = customers_df.sample(1).iloc[0]
        
        # Random date (more transactions in recent months)
        days_ago = int(np.random.exponential(scale=200))
        days_ago = min(days_ago, 730)  # Cap at 2 years
        transaction_date = end_date - timedelta(days=days_ago)
        
        # Random number of items (1-5)
        n_items = random.choices([1, 2, 3, 4, 5], weights=[50, 30, 15, 4, 1])[0]
        
        # Select products
        selected_products = products_df.sample(n_items)
        
        for _, product in selected_products.iterrows():
            quantity = random.choices([1, 2, 3, 4, 5], weights=[70, 20, 7, 2, 1])[0]
            
            # Apply discount occasionally
            discount = random.choice([0, 0, 0, 0, 0.1, 0.15, 0.2, 0.25])  # 62.5% no discount
            unit_price = product['price'] * (1 - discount)
            
            transaction = {
                'transaction_id': f'TXN_{i+1:08d}_{random.randint(1000, 9999)}',
                'customer_id': customer['customer_id'],
                'product_id': product['product_id'],
                'transaction_date': transaction_date.strftime('%Y-%m-%d'),
                'quantity': quantity,
                'unit_price': round(unit_price, 2),
                'discount': discount,
                'total_amount': round(unit_price * quantity, 2),
                'payment_method': random.choice(['Credit Card', 'Debit Card', 'PayPal', 'Bank Transfer', 'Cash']),
                'shipping_method': random.choice(['Standard', 'Express', 'Next Day']),
            }
            transactions.append(transaction)
    
    return pd.DataFrame(transactions)


def add_data_quality_issues(df, missing_rate=0.05, outlier_rate=0.02):
    """Introduce realistic data quality issues for cleaning demonstration"""
    
    df = df.copy()
    
    # Add missing values
    n_rows = len(df)
    
    # Missing customer_id (rare)
    missing_customer = random.sample(range(n_rows), int(n_rows * 0.001))
    df.loc[missing_customer, 'customer_id'] = np.nan
    
    # Missing payment_method (occasional)
    missing_payment = random.sample(range(n_rows), int(n_rows * missing_rate))
    df.loc[missing_payment, 'payment_method'] = np.nan
    
    # Missing shipping_method (occasional)
    missing_shipping = random.sample(range(n_rows), int(n_rows * missing_rate * 0.5))
    df.loc[missing_shipping, 'shipping_method'] = np.nan
    
    # Add outliers in quantity (data entry errors)
    outlier_rows = random.sample(range(n_rows), int(n_rows * outlier_rate))
    df.loc[outlier_rows, 'quantity'] = df.loc[outlier_rows, 'quantity'] * random.choice([10, 50, 100])
    
    # Add outliers in unit_price (pricing errors)
    outlier_price = random.sample(range(n_rows), int(n_rows * outlier_rate * 0.5))
    df.loc[outlier_price, 'unit_price'] = df.loc[outlier_price, 'unit_price'] * random.choice([10, 100])
    
    # Add some negative quantities (returns/cancellations mixed in)
    negative_rows = random.sample(range(n_rows), int(n_rows * 0.01))
    df.loc[negative_rows, 'quantity'] = -df.loc[negative_rows, 'quantity']
    
    # Add duplicate rows (system errors)
    n_duplicates = int(n_rows * 0.005)
    duplicates = df.sample(n_duplicates)
    df = pd.concat([df, duplicates], ignore_index=True)
    
    return df


def main():
    """Generate complete e-commerce dataset"""
    
    print("Generating e-commerce dataset...")
    
    # Generate datasets
    print("Creating customers...")
    customers_df = generate_customers(n_customers=1000)
    
    print("Creating products...")
    products_df = generate_products(n_products=200)
    
    print("Creating transactions...")
    transactions_df = generate_transactions(customers_df, products_df, n_transactions=15000)
    
    # Add data quality issues
    print("Adding data quality issues for cleaning demonstration...")
    transactions_df = add_data_quality_issues(transactions_df)
    
    # Save to CSV
    print("Saving to CSV files...")
    customers_df.to_csv('data/customers.csv', index=False)
    products_df.to_csv('data/products.csv', index=False)
    transactions_df.to_csv('data/transactions.csv', index=False)
    
    # Create a combined dataset
    print("Creating combined dataset...")
    combined_df = transactions_df.merge(
        customers_df[['customer_id', 'customer_name', 'country', 'age', 'gender']], 
        on='customer_id', 
        how='left'
    ).merge(
        products_df[['product_id', 'product_name', 'category', 'subcategory', 'cost']], 
        on='product_id', 
        how='left'
    )
    
    # Calculate profit
    combined_df['profit'] = (combined_df['unit_price'] - combined_df['cost']) * combined_df['quantity']
    
    combined_df.to_csv('data/ecommerce_data.csv', index=False)
    
    print("\nDataset generation complete!")
    print(f"Customers: {len(customers_df):,}")
    print(f"Products: {len(products_df):,}")
    print(f"Transactions: {len(transactions_df):,}")
    print(f"Date range: {transactions_df['transaction_date'].min()} to {transactions_df['transaction_date'].max()}")
    
    # Print data quality summary
    print("\nData Quality Issues Introduced:")
    print(f"Missing customer_id: {transactions_df['customer_id'].isna().sum()}")
    print(f"Missing payment_method: {transactions_df['payment_method'].isna().sum()}")
    print(f"Missing shipping_method: {transactions_df['shipping_method'].isna().sum()}")
    print(f"Duplicate rows: {transactions_df.duplicated().sum()}")
    
    return customers_df, products_df, transactions_df, combined_df


if __name__ == "__main__":
    import os
    os.makedirs('data', exist_ok=True)
    main()
