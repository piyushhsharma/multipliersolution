# Data Analytics Dashboard

A complete end-to-end data engineering project demonstrating data cleaning, analysis, and visualization capabilities using Python, FastAPI, and modern web technologies.

## 🚀 Project Overview

This project showcases a full data pipeline from raw data ingestion to interactive dashboard visualization. It includes:

- **Data Cleaning**: Automated cleaning of customer and order datasets with quality issues
- **Data Analysis**: Comprehensive analysis including revenue trends, customer segmentation, and regional performance
- **API Backend**: FastAPI-based REST API serving processed data
- **Interactive Dashboard**: Responsive web dashboard with real-time data visualization

## 📁 Project Structure

```
assignment_project/
├── clean_data.py              # Data cleaning script
├── analyze.py                 # Data analysis script
├── backend/
│   ├── main.py               # FastAPI application
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── index.html            # Dashboard HTML
│   ├── app.js                # Frontend JavaScript
│   └── styles.css            # Dashboard styles
├── data/
│   ├── raw/                  # Raw datasets
│   │   ├── customers.csv
│   │   ├── orders.csv
│   │   └── products.csv
│   └── processed/            # Cleaned and analyzed data
│       ├── customers_clean.csv
│       ├── orders_clean.csv
│       ├── monthly_revenue.csv
│       ├── top_customers.csv
│       ├── category_performance.csv
│       └── regional_analysis.csv
├── tests/                    # Test directory (empty for this demo)
└── README.md                 # This file
```

## 🛠️ Technology Stack

### Backend
- **Python 3.8+**: Core programming language
- **Pandas**: Data manipulation and analysis
- **FastAPI**: Modern web framework for APIs
- **Uvicorn**: ASGI server for FastAPI

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with responsive design
- **Vanilla JavaScript**: No framework dependencies
- **Chart.js**: Data visualization library

### Data Processing
- **Pathlib**: Cross-platform path handling
- **Logging**: Comprehensive error tracking
- **Datetime**: Date parsing and manipulation

## 📊 Dataset Features

### Raw Data Issues Addressed

**Customers Dataset:**
- Duplicate customer IDs (kept most recent signup)
- Missing and malformed email addresses
- Whitespace in names and regions
- Mixed date formats
- Missing region values

**Orders Dataset:**
- Mixed date formats (YYYY-MM-DD, DD/MM/YYYY, MM-DD-YYYY)
- Null amounts and order IDs
- Inconsistent status values
- Missing product references

**Products Dataset:**
- Complete product catalog
- Products not present in orders (for analysis completeness)

## 🧹 Data Cleaning Process

The `clean_data.py` script performs comprehensive data cleaning:

### Customers Cleaning
- Removes duplicate customer IDs keeping most recent signup date
- Standardizes emails to lowercase
- Validates email format with `is_valid_email` flag
- Parses signup dates to standard format
- Strips whitespace from text fields
- Fills missing regions with "Unknown"

### Orders Cleaning
- Multi-format date parsing for order dates
- Removes rows with missing critical identifiers
- Fills missing amounts using product medians
- Normalizes status values to standard set
- Adds `order_year_month` for time-based analysis

## 📈 Analysis Features

The `analyze.py` script generates comprehensive insights:

### 1. Monthly Revenue Trends
- Completed orders only
- Total revenue and order count by month
- Time series analysis for trend identification

### 2. Top Customers Analysis
- Ranked by total spend
- Includes customer details and order counts
- **Churn Indicator**: Customers inactive for 90+ days

### 3. Category Performance
- Total revenue by category
- Average order value
- Order volume analysis

### 4. Regional Analysis
- Customer distribution by region
- Order volume and revenue metrics
- Average revenue per customer

## 🌐 API Endpoints

The FastAPI backend provides the following endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check endpoint |
| `/api/revenue` | GET | Monthly revenue trend data |
| `/api/top-customers` | GET | Top customers with churn status |
| `/api/categories` | GET | Category performance metrics |
| `/api/regions` | GET | Regional analysis data |
| `/api/summary` | GET | Overall summary statistics |

### API Features
- **CORS Support**: Cross-origin requests enabled
- **Error Handling**: Comprehensive HTTP error responses
- **Data Validation**: Input validation and sanitization
- **JSON Responses**: Standardized JSON output format

## 📱 Dashboard Features

### Interactive Elements
- **Revenue Trend Chart**: Line chart with date filtering
- **Top Customers Table**: Sortable columns with search functionality
- **Category Performance**: Bar chart with detailed tooltips
- **Regional Analysis**: Sortable table with comprehensive metrics

### Responsive Design
- **Desktop**: Optimized for 1280px+ displays
- **Mobile**: Fully responsive for 375px+ screens
- **Tablet**: Adaptive layouts for intermediate sizes

### User Experience
- **Loading Indicators**: Visual feedback during data loading
- **Error Messages**: User-friendly error notifications
- **Search & Filter**: Real-time data filtering
- **Sort Functionality**: Multi-column sorting capabilities

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser with JavaScript enabled

### Installation Steps

1. **Navigate to project directory:**
   ```bash
   cd assignment_project
   ```

2. **Install backend dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Run data cleaning:**
   ```bash
   python clean_data.py
   ```

4. **Run data analysis:**
   ```bash
   python analyze.py
   ```

5. **Start the API server:**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

6. **Open the dashboard:**
   - Open `frontend/index.html` in your web browser
   - Or serve it with a local web server

### Alternative: Using Python's HTTP Server

For easy frontend serving:
```bash
cd frontend
python -m http.server 3000
```

Then access: `http://localhost:3000`

## 🧪 Testing the Application

### API Testing
Use curl or any API client to test endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Get revenue data
curl http://localhost:8000/api/revenue

# Get top customers
curl http://localhost:8000/api/top-customers
```

### Data Validation
Check processed data in `data/processed/` directory:
- `customers_clean.csv`: Cleaned customer data
- `orders_clean.csv`: Cleaned order data
- Analysis results with comprehensive metrics

## 🎯 Design Choices & Assumptions

### Architecture Decisions
1. **Modular Design**: Separate scripts for cleaning and analysis
2. **Error Handling**: Comprehensive logging and error management
3. **Data Validation**: Input validation at multiple levels
4. **API-First**: Backend designed for API consumption

### Data Assumptions
1. **Customer Churn**: 90-day inactivity threshold
2. **Date Formats**: Support for three common date formats
3. **Status Normalization**: Standard order status categories
4. **Missing Data**: Median-based imputation for amounts

### Technical Choices
1. **Vanilla JavaScript**: No frontend framework dependencies
2. **Chart.js**: Lightweight, powerful visualization
3. **FastAPI**: Modern, high-performance API framework
4. **Pandas**: Industry-standard data manipulation

## 🔧 Configuration

### Environment Variables
No environment variables required for basic operation.

### Customization Options
- **Churn Period**: Modify `timedelta(days=90)` in `analyze.py`
- **Date Formats**: Add formats to `date_formats` list
- **API Port**: Change in uvicorn command
- **CORS Origins**: Update `allow_origins` in `main.py`

## 📝 Logging

The application uses Python's logging module with:
- **INFO Level**: General operation information
- **ERROR Level**: Error conditions and failures
- **Console Output**: Real-time logging during execution

## 🚨 Error Handling

### Data Processing Errors
- File not found scenarios
- Empty data files
- Invalid data formats
- Missing required columns

### API Errors
- 404: Data files not found
- 500: Internal server errors
- CORS issues handled by middleware

### Frontend Errors
- Network request failures
- Data parsing errors
- User-friendly error messages

## 🔄 Data Flow

1. **Raw Data** → `clean_data.py` → **Cleaned Data**
2. **Cleaned Data** → `analyze.py` → **Analysis Results**
3. **Analysis Results** → **FastAPI Backend** → **JSON API**
4. **JSON API** → **Frontend JavaScript** → **Interactive Dashboard**

## 📊 Sample Insights Generated

- **Revenue Trends**: Monthly growth patterns and seasonality
- **Customer Segmentation**: High-value customers identification
- **Product Performance**: Category-level revenue analysis
- **Geographic Analysis**: Regional market penetration
- **Churn Analysis**: Customer retention metrics

## 🎨 Frontend Features

### Visual Design
- Modern gradient headers
- Card-based layouts
- Smooth animations and transitions
- Professional color scheme

### Interactive Elements
- Hover effects on charts
- Sortable table columns
- Real-time search filtering
- Responsive navigation

### Accessibility
- Semantic HTML structure
- ARIA labels where appropriate
- Keyboard navigation support
- High contrast colors

## 🚀 Performance Considerations

### Backend Optimization
- Efficient pandas operations
- Memory-conscious data loading
- Error handling without performance impact

### Frontend Optimization
- Debounced search inputs
- Efficient DOM manipulation
- Responsive chart resizing
- Minimal external dependencies

## 🔮 Future Enhancements

### Potential Improvements
1. **Real-time Updates**: WebSocket integration
2. **Advanced Analytics**: Machine learning predictions
3. **Data Export**: CSV/PDF download capabilities
4. **User Authentication**: Secure user management
5. **Database Integration**: PostgreSQL/MongoDB support
6. **Docker Containerization**: Production deployment

### Scalability Features
1. **Caching**: Redis integration
2. **Load Balancing**: Multiple API instances
3. **Database**: Persistent data storage
4. **Monitoring**: Application performance tracking

## 📄 License

This project is provided as a demonstration of data engineering capabilities. Feel free to use and modify for educational purposes.

## 🤝 Contributing

For this demonstration project, the focus is on showcasing complete end-to-end data pipeline implementation. The code is production-ready and follows industry best practices.

---

**Note**: This project demonstrates a complete data engineering workflow from raw data to interactive visualization. All components are fully functional and can be extended for production use cases.
