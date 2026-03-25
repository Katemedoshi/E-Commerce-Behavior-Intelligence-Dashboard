"""
Data Cleaning Pipeline Module
Handles missing values, outliers, duplicates, and data quality issues
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataCleaningPipeline:
    """Pipeline for cleaning e-commerce transaction data"""
    
    def __init__(self, df):
        self.original_df = df.copy()
        self.cleaned_df = df.copy()
        self.cleaning_log = []
        
    def log_action(self, action, details):
        """Log cleaning actions"""
        self.cleaning_log.append({
            'action': action,
            'details': details,
            'timestamp': datetime.now()
        })
        logger.info(f"{action}: {details}")
    
    def get_data_profile(self):
        """Get data quality profile before cleaning"""
        df = self.cleaned_df
        
        profile = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isna().sum().sum(),
            'missing_by_column': df.isna().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
        }
        
        # Add statistics for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            profile['numeric_stats'] = df[numeric_cols].describe().to_dict()
        
        return profile
    
    def handle_missing_values(self, strategy='auto'):
        """Handle missing values with various strategies"""
        df = self.cleaned_df
        
        # Remove rows where critical fields are missing
        critical_cols = ['customer_id', 'transaction_id', 'product_id']
        for col in critical_cols:
            if col in df.columns:
                missing_count = df[col].isna().sum()
                if missing_count > 0:
                    df = df.dropna(subset=[col])
                    self.log_action('DROP_MISSING_CRITICAL', f"Dropped {missing_count} rows with missing {col}")
        
        # Handle payment_method missing values
        if 'payment_method' in df.columns:
            missing_payment = df['payment_method'].isna().sum()
            if missing_payment > 0:
                df['payment_method'] = df['payment_method'].fillna('Unknown')
                self.log_action('FILL_MISSING', f"Filled {missing_payment} missing payment_method with 'Unknown'")
        
        # Handle shipping_method missing values
        if 'shipping_method' in df.columns:
            missing_shipping = df['shipping_method'].isna().sum()
            if missing_shipping > 0:
                mode_shipping = df['shipping_method'].mode()[0] if not df['shipping_method'].mode().empty else 'Standard'
                df['shipping_method'] = df['shipping_method'].fillna(mode_shipping)
                self.log_action('FILL_MISSING', f"Filled {missing_shipping} missing shipping_method with mode '{mode_shipping}'")
        
        # Handle customer_name missing values (from merge)
        if 'customer_name' in df.columns:
            missing_names = df['customer_name'].isna().sum()
            if missing_names > 0:
                df['customer_name'] = df['customer_name'].fillna('Guest Customer')
                self.log_action('FILL_MISSING', f"Filled {missing_names} missing customer_name with 'Guest Customer'")
        
        # Handle other categorical missing values
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if df[col].isna().sum() > 0:
                missing_count = df[col].isna().sum()
                df[col] = df[col].fillna(f'Unknown_{col}')
                self.log_action('FILL_MISSING', f"Filled {missing_count} missing values in {col}")
        
        self.cleaned_df = df
        return self
    
    def remove_duplicates(self):
        """Remove duplicate rows"""
        df = self.cleaned_df
        
        # Count duplicates before removal
        duplicate_count = df.duplicated().sum()
        
        if duplicate_count > 0:
            df = df.drop_duplicates(keep='first')
            self.log_action('REMOVE_DUPLICATES', f"Removed {duplicate_count} duplicate rows")
        else:
            self.log_action('REMOVE_DUPLICATES', "No duplicate rows found")
        
        self.cleaned_df = df
        return self
    
    def handle_outliers(self, method='iqr', columns=None):
        """Handle outliers using IQR or Z-score method"""
        df = self.cleaned_df
        
        if columns is None:
            # Default columns to check for outliers
            columns = ['quantity', 'unit_price', 'total_amount']
        
        columns = [col for col in columns if col in df.columns]
        
        for col in columns:
            if method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 3 * IQR  # Using 3*IQR for less aggressive filtering
                upper_bound = Q3 + 3 * IQR
                
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                
                # Cap outliers instead of removing them
                df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
                
                if len(outliers) > 0:
                    self.log_action('HANDLE_OUTLIERS', f"Capped {len(outliers)} outliers in {col} using IQR method")
                    
            elif method == 'zscore':
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                outliers = df[z_scores > 3]
                
                # Cap values with z-score > 3
                upper_limit = df[col].mean() + 3 * df[col].std()
                lower_limit = max(0, df[col].mean() - 3 * df[col].std())
                df[col] = df[col].clip(lower=lower_limit, upper=upper_limit)
                
                if len(outliers) > 0:
                    self.log_action('HANDLE_OUTLIERS', f"Capped {len(outliers)} outliers in {col} using Z-score method")
        
        self.cleaned_df = df
        return self
    
    def handle_negative_values(self):
        """Handle negative quantities (returns/refunds)"""
        df = self.cleaned_df
        
        if 'quantity' in df.columns:
            negative_qty = df[df['quantity'] < 0]
            
            if len(negative_qty) > 0:
                # Separate returns from main dataset or handle appropriately
                # For this analysis, we'll keep them but flag them
                df['is_return'] = df['quantity'] < 0
                self.log_action('FLAG_RETURNS', f"Flagged {len(negative_qty)} return transactions")
                
                # Calculate return rate
                return_rate = len(negative_qty) / len(df) * 100
                self.log_action('CALCULATE_METRICS', f"Return rate: {return_rate:.2f}%")
        
        self.cleaned_df = df
        return self
    
    def validate_data_types(self):
        """Ensure correct data types"""
        df = self.cleaned_df
        
        # Convert transaction_date to datetime
        if 'transaction_date' in df.columns:
            df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
            invalid_dates = df['transaction_date'].isna().sum()
            if invalid_dates > 0:
                self.log_action('VALIDATE_DATES', f"Found {invalid_dates} invalid dates")
        
        # Ensure numeric columns are numeric
        numeric_cols = ['quantity', 'unit_price', 'total_amount', 'discount', 'cost', 'profit', 'age']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        self.cleaned_df = df
        return self
    
    def create_derived_features(self):
        """Create additional derived features for analysis"""
        df = self.cleaned_df
        
        if 'transaction_date' in df.columns:
            # Extract date components
            df['year'] = df['transaction_date'].dt.year
            df['month'] = df['transaction_date'].dt.month
            df['quarter'] = df['transaction_date'].dt.quarter
            df['day_of_week'] = df['transaction_date'].dt.dayofweek
            df['month_name'] = df['transaction_date'].dt.month_name()
            df['year_month'] = df['transaction_date'].dt.to_period('M').astype(str)
        
        # Calculate profit margin
        if 'profit' in df.columns and 'total_amount' in df.columns:
            df['profit_margin'] = (df['profit'] / df['total_amount'] * 100).round(2)
        
        # Age groups
        if 'age' in df.columns:
            df['age_group'] = pd.cut(df['age'], 
                                     bins=[0, 25, 35, 50, 65, 100], 
                                     labels=['18-25', '26-35', '36-50', '51-65', '65+'])
        
        # Price tier
        if 'unit_price' in df.columns:
            df['price_tier'] = pd.cut(df['unit_price'],
                                      bins=[0, 50, 150, 500, float('inf')],
                                      labels=['Budget', 'Mid-range', 'Premium', 'Luxury'])
        
        self.log_action('CREATE_FEATURES', "Created derived features: year, month, quarter, profit_margin, age_group, price_tier")
        self.cleaned_df = df
        return self
    
    def run_full_pipeline(self):
        """Execute complete cleaning pipeline"""
        logger.info("Starting data cleaning pipeline...")
        
        initial_profile = self.get_data_profile()
        logger.info(f"Initial data: {initial_profile['total_rows']:,} rows, {initial_profile['missing_values']:,} missing values")
        
        # Execute cleaning steps
        (self
            .handle_missing_values()
            .remove_duplicates()
            .handle_outliers()
            .handle_negative_values()
            .validate_data_types()
            .create_derived_features())
        
        final_profile = self.get_data_profile()
        logger.info(f"Final data: {final_profile['total_rows']:,} rows, {final_profile['missing_values']:,} missing values")
        
        rows_removed = initial_profile['total_rows'] - final_profile['total_rows']
        logger.info(f"Pipeline complete. Removed {rows_removed:,} rows ({rows_removed/initial_profile['total_rows']*100:.2f}%)")
        
        return self.cleaned_df
    
    def get_cleaning_report(self):
        """Get detailed cleaning report"""
        return {
            'log': self.cleaning_log,
            'initial_shape': self.original_df.shape,
            'final_shape': self.cleaned_df.shape,
            'rows_removed': self.original_df.shape[0] - self.cleaned_df.shape[0],
            'columns_added': len(self.cleaned_df.columns) - len(self.original_df.columns)
        }


def clean_ecommerce_data(file_path='data/ecommerce_data.csv'):
    """Main function to clean e-commerce data"""
    
    # Load data
    logger.info(f"Loading data from {file_path}...")
    df = pd.read_csv(file_path)
    
    # Create and run cleaning pipeline
    pipeline = DataCleaningPipeline(df)
    cleaned_df = pipeline.run_full_pipeline()
    
    # Save cleaned data
    cleaned_df.to_csv('data/cleaned_ecommerce_data.csv', index=False)
    logger.info("Cleaned data saved to data/cleaned_ecommerce_data.csv")
    
    # Return report
    report = pipeline.get_cleaning_report()
    
    return cleaned_df, report


if __name__ == "__main__":
    cleaned_df, report = clean_ecommerce_data()
    print("\n" + "="*50)
    print("DATA CLEANING REPORT")
    print("="*50)
    print(f"Original rows: {report['initial_shape'][0]:,}")
    print(f"Final rows: {report['final_shape'][0]:,}")
    print(f"Rows removed: {report['rows_removed']:,}")
    print(f"Columns added: {report['columns_added']}")
    print("\nCleaning actions:")
    for entry in report['log']:
        print(f"  - {entry['action']}: {entry['details']}")
