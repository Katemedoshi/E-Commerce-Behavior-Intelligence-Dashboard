# E-Commerce Analytics Dashboard

A comprehensive data analysis project for e-commerce businesses featuring customer segmentation (RFM analysis), SQL analytics, interactive visualizations, and business recommendations.

## 🚀 Features

- **📊 Data Generation**: Synthetic e-commerce dataset with realistic transactions
- **🧹 Data Cleaning**: Automated pipeline for handling missing values, outliers, and quality issues
- **👥 RFM Analysis**: Customer segmentation using Recency, Frequency, and Monetary analysis
- **🗄️ SQL Analytics**: 12+ SQL queries for revenue, customer, and product insights
- **📈 Visualizations**: 10+ charts using Matplotlib and Seaborn
- **🖥️ Streamlit Dashboard**: Interactive web dashboard with Plotly charts
- **💡 Business Recommendations**: Data-driven actionable insights

## 📁 Project Structure

```
ecommerce-analytics/
├── data/                          # Data files
│   ├── customers.csv              # Customer master data
│   ├── products.csv               # Product catalog
│   ├── transactions.csv           # Raw transactions
│   ├── ecommerce_data.csv         # Combined dataset
│   ├── cleaned_ecommerce_data.csv # Cleaned dataset
│   ├── rfm_analysis.csv           # RFM analysis results
│   ├── segment_summary.csv        # Customer segments
│   └── sql_results/               # SQL query outputs
├── visualizations/                # Generated charts
├── app.py                         # Streamlit dashboard
├── data_generation.py             # Dataset creation
├── data_cleaning.py               # Cleaning pipeline
├── rfm_analysis.py                # RFM segmentation
├── sql_analytics.py               # SQL queries
├── visualizations.py              # Chart generation
├── run_pipeline.py                # Main execution script
├── requirements.txt               # Python dependencies
├── BUSINESS_RECOMMENDATIONS.md    # Business insights
└── README.md                      # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. **Clone or download the project**
```bash
cd ecommerce-analytics
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

## 🎯 Usage

### Option 1: Run Complete Pipeline

Execute all steps at once:
```bash
python run_pipeline.py
```

### Option 2: Step-by-Step Execution

Run individual components:

```bash
# 1. Generate synthetic data
python data_generation.py

# 2. Clean the data
python data_cleaning.py

# 3. Perform RFM analysis
python rfm_analysis.py

# 4. Run SQL analytics
python sql_analytics.py

# 5. Create visualizations
python visualizations.py

# 6. Launch dashboard
streamlit run app.py
```

### Option 3: Direct Dashboard Launch

If data already exists:
```bash
streamlit run app.py
```

## 📊 Dashboard Features

The Streamlit dashboard includes:

### 📈 Overview Tab
- KPI metrics (Revenue, Profit, Orders, Customers, AOV)
- Monthly revenue and profit trends
- Category revenue breakdown
- Geographic performance

### 👥 Customers Tab
- RFM distribution charts (Recency, Frequency, Monetary)
- Customer segment treemap
- Segment-specific recommendations
- Top customers analysis

### 🛍️ Products Tab
- Top 15 products by revenue
- Category performance scatter plot
- Price tier analysis
- Product profitability insights

### ⚙️ Operations Tab
- Payment method distribution
- Shipping method performance
- Sales by day of week
- Discount impact analysis

### 💡 Recommendations Tab
- Priority business actions
- Segment-specific strategies
- Implementation roadmap
- Success metrics tracking

## 🗄️ SQL Queries Included

### Revenue Analysis
1. **Monthly Revenue** - Monthly trends with growth rates
2. **Quarterly Revenue** - Quarter-over-quarter comparison
3. **Revenue by Category** - Category performance with margins

### Customer Analytics
4. **Top Customers** - Highest value customers
5. **Cohort Analysis** - Customer retention by acquisition month
6. **Geographic Analysis** - Performance by country

### Product Analytics
7. **Product Performance** - Top products by revenue
8. **Category Performance** - Category & subcategory insights
9. **Inventory Alerts** - Low-stock, high-demand products

### Operational Analytics
10. **Payment Methods** - Transaction distribution
11. **Shipping Performance** - Revenue by shipping method
12. **Daily Patterns** - Sales by day of week

## 📈 RFM Segmentation

Customers are segmented into 11 groups:

| Segment | RFM Criteria | Strategy |
|---------|--------------|----------|
| Champions | R≥4, F≥4, M≥4 | VIP programs, referrals |
| Loyal Customers | F≥4, M≥4 | Upsell, loyalty rewards |
| Potential Loyalists | R≥4, (F≥3 or M≥3) | Onboarding, membership |
| New Customers | R≥4, F≤2 | Welcome offers, education |
| Promising | R≥3, F≥2, M≥2 | Targeted incentives |
| Need Attention | R≥3, F≥3, M≥3 | Limited-time offers |
| About to Sleep | R≤2, (F≥3 or M≥3) | Win-back campaigns |
| At Risk | R≤2, F≥4, M≥4 | Aggressive win-back |
| Cannot Lose Them | R≤2, F≥4, M≥4 | Personal outreach |
| Hibernating | R≤2, F≤2, M≥3 | Reactivation emails |
| Lost | Low R, F, M | Exit surveys |

## 🎨 Visualizations

The project generates the following charts:

1. Monthly Revenue Trend (bar + line combo)
2. Revenue by Category (horizontal bar)
3. RFM Distribution (histograms)
4. Customer Segments (treemap + bar)
5. Customer Geography (map-style bar)
6. Top Customers (ranked bar)
7. Product Performance (heatmap)
8. Category Matrix (heatmap)
9. Payment Methods (pie chart)
10. Sales by Day (bar chart)
11. Discount Impact (dual bar charts)

All charts are saved to the `visualizations/` folder.

## 🔧 Data Cleaning Pipeline

The automated cleaning pipeline handles:
- ✅ Missing values (imputation/removal)
- ✅ Duplicate records
- ✅ Outlier detection (IQR and Z-score methods)
- ✅ Negative quantities (returns flagging)
- ✅ Data type validation
- ✅ Derived features creation

## 💡 Business Recommendations

Key insights from the analysis include:

### Customer Retention
- Focus win-back campaigns on "At Risk" segment
- Implement VIP program for "Champions"
- Create structured onboarding for "New Customers"

### Revenue Growth
- Optimize pricing strategy by price tier
- Expand successful product categories
- Improve discount effectiveness

### Operational Efficiency
- Monitor payment method distribution
- Optimize shipping costs
- Reduce return rates

See `BUSINESS_RECOMMENDATIONS.md` for complete details.

## 📦 Dependencies

```
pandas==2.1.4
numpy==1.26.3
matplotlib==3.8.2
seaborn==0.13.1
streamlit==1.29.0
plotly==5.18.0
scikit-learn==1.3.2
faker==22.0.0
```

## 📊 Sample Data

The generated dataset includes:
- **1,000** unique customers
- **200** unique products across 6 categories
- **15,000+** transactions
- **2 years** of historical data
- Realistic data quality issues for demonstration

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Production Deployment
For production deployment on Streamlit Cloud:
1. Push to GitHub
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy directly from repository

## 📝 License

This project is open source and available for educational and commercial use.

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Additional SQL queries
- Machine learning predictions
- Real-time data integration
- Enhanced visualizations
- Multi-language support

## 🎓 Learning Resources

This project demonstrates:
- Data cleaning and preprocessing
- Customer segmentation techniques
- SQL analytics for business intelligence
- Data visualization best practices
- Interactive dashboard development
- Business recommendation frameworks

## 📞 Support

For issues or questions:
1. Check the logs in `pipeline.log`
2. Verify all dependencies are installed
3. Ensure data files are generated in `data/` folder
4. Review error messages for specific issues

## 🏆 Success Metrics

Track these KPIs to measure impact:
- Customer retention rate (target: +10-15%)
- Average order value (target: +5-10%)
- Segment migration (At Risk → Loyal)
- Inventory turnover (target: +15%)
- Real-time dashboard adoption

---

**Built with ❤️ using Python, Pandas, SQL, and Streamlit**
