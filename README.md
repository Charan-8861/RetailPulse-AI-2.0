# 📊 RetailPulse AI 2.0

## Deep Learning-Powered Retail Analytics and Demand Forecasting

RetailPulse AI 2.0 is an end-to-end retail analytics, demand forecasting, and business intelligence application built using **Python, Streamlit, TensorFlow, Keras, and Scikit-learn**.

The application enables users to upload different retail datasets, configure important business fields, analyze retail performance, transform transactional data into time-series data, train an **LSTM deep learning model**, compare it against baseline forecasting methods, generate future forecasts, and obtain data-driven business insights.

RetailPulse AI 2.0 extends the original **RetailPulse AI: Smart Retail Analytics** project by introducing deep learning, predictive intelligence, automated model evaluation, and an interactive deployed application.

---

## 🌐 Live Application

🚀 **RetailPulse AI 2.0 is deployed on Streamlit Community Cloud.**

**Live Demo:**  
https://retailpulse-ai-2.streamlit.app/

**GitHub Repository:**  
https://github.com/Charan-8861/RetailPulse-AI-2.0

---

## 🎯 Project Objective

The objective of RetailPulse AI 2.0 is to develop a reusable retail intelligence platform capable of working with different retail datasets rather than being restricted to a single predefined dataset.

The application combines:

- Flexible retail dataset upload
- Automatic column detection
- Manual column configuration
- Data preprocessing and validation
- Retail business analytics
- Deep learning-based forecasting
- Baseline forecasting comparison
- Model performance evaluation
- Future sales/demand forecasting
- Business insights
- Downloadable forecasting results
- User authentication
- Cloud deployment

---

# ✨ Key Features

## 🔐 User Authentication

RetailPulse AI 2.0 includes a user authentication system with:

- User registration
- Secure password hashing
- User login
- Session-based authentication
- Logout functionality

SQLite is used for lightweight user-account storage.

---

## 📁 Flexible Dataset Upload

Users can upload retail datasets in:

- CSV
- Excel (`.xlsx`)

The application is designed to support different retail datasets through configurable column mapping.

---

## 🧠 Automatic Column Detection

RetailPulse AI attempts to automatically identify important retail fields such as:

- Date
- Sales / Revenue
- Quantity / Demand
- Product
- Category
- Region
- Customer

Users can manually verify or modify the detected mappings before configuring the dataset.

---

## 📊 Retail Analytics Dashboard

The interactive dashboard provides retail KPIs and visual analysis including:

- Total Sales
- Total Quantity
- Number of Customers
- Number of Products
- Monthly Sales Trend
- Sales by Category
- Sales by Region
- Top Products by Sales

The dashboard automatically adapts according to the columns available in the uploaded dataset.

---

## 📈 Retail Analytics

The Analytics module provides deeper exploration of the configured retail dataset.

Depending on the available columns, users can analyze:

- Sales trends
- Product performance
- Category performance
- Regional performance
- Quantity and demand patterns
- Customer activity

---

## 🤖 LSTM Demand Forecasting

The core predictive component of RetailPulse AI 2.0 uses a **Long Short-Term Memory (LSTM)** neural network.

The forecasting pipeline supports:

- Weekly forecasting
- Monthly forecasting
- Configurable lookback periods
- Configurable training epochs
- Configurable forecast horizon
- MinMax feature scaling
- Chronological train/test splitting
- Sequence generation
- Stacked LSTM architecture
- Dropout regularization
- Early stopping
- Learning-rate reduction
- Recursive future forecasting

Users can forecast either sales or quantity depending on the configured dataset.

---

## 🧪 Forecasting Model Comparison

RetailPulse AI 2.0 does not assume that deep learning will always outperform simpler forecasting techniques.

The application compares:

1. **LSTM**
2. **Naive Forecast**
3. **Seasonal Naive Forecast**

Models are evaluated using:

- MAE — Mean Absolute Error
- RMSE — Root Mean Squared Error
- MAPE — Mean Absolute Percentage Error
- R² — Coefficient of Determination

The application identifies the best-performing forecasting method based on **MAPE**.

---

## 🔮 Future Forecasting

After model training, RetailPulse AI can generate future sales or demand predictions.

Forecasting outputs include:

- Forecast dates
- Predicted values
- Historical vs future visualization
- Forecast percentage change
- Forecast trend interpretation
- Downloadable forecast CSV

---

## 💡 Business Insights

The Business Insights module converts analytical and forecasting results into decision-support information.

It helps users interpret:

- Business performance
- Retail trends
- Forecast direction
- Potential opportunities
- Areas requiring attention
- Forecast-based business recommendations

This connects the technical forecasting pipeline with practical retail decision-making.

---

## ⚙️ Dataset Information

The Dataset Info module provides information about the configured dataset including:

- Number of rows
- Number of columns
- Missing values
- Duplicate records
- Column data types
- Unique values
- Selected column mappings
- Dataset quality information
- Forecasting readiness

---

# 🧠 Deep Learning Architecture

The current LSTM network consists of:

```text
Input Time-Series Sequence
          ↓
     LSTM Layer
       32 Units
          ↓
    Dropout (20%)
          ↓
     LSTM Layer
       16 Units
          ↓
    Dropout (20%)
          ↓
      Dense Layer
       8 Units
        ReLU
          ↓
   Dense Output Layer
          ↓
       Forecast
```

### Model Configuration

```text
Optimizer : Adam
Loss      : Mean Squared Error
```

Training also uses:

- EarlyStopping
- ReduceLROnPlateau

These techniques help reduce unnecessary training and adjust the learning rate when validation performance stops improving.

---

# 🔄 Application Workflow

```text
User Registration / Login
            ↓
Upload Retail Dataset
            ↓
Dataset Validation
            ↓
Automatic Column Detection
            ↓
Manual Column Configuration
            ↓
Data Preprocessing
            ↓
Retail Analytics Dashboard
            ↓
Weekly / Monthly Aggregation
            ↓
Chronological Train/Test Split
            ↓
MinMax Scaling
            ↓
LSTM Sequence Generation
            ↓
LSTM Training
            ↓
Baseline Forecasting
            ↓
Model Evaluation
            ↓
Best Model Identification
            ↓
Future Forecast Generation
            ↓
Business Insights
            ↓
Download Forecast Results
```

---

# 📈 Model Evaluation

A sample weekly forecasting experiment produced:

| Model | MAE | RMSE | MAPE | R² |
|---|---:|---:|---:|---:|
| Naive Forecast | 15,154.12 | 20,085.85 | 17.68% | 0.446 |
| LSTM | 20,591.01 | 26,591.51 | 21.82% | 0.028 |
| Seasonal Naive | 22,879.39 | 27,781.07 | 24.32% | -0.075 |

### Result

For this experiment, the **Naive Forecast** achieved the lowest MAPE and was therefore identified as the best-performing forecasting method.

The LSTM achieved a MAPE of approximately **21.82%**.

This demonstrates an important forecasting principle: **a more complex deep learning model is not automatically superior to a simpler forecasting method**.

RetailPulse AI therefore benchmarks the LSTM against baseline forecasting approaches before drawing model-performance conclusions.

> Model results may vary between training runs because neural-network training involves random initialization and iterative optimization.

---

# 🛠️ Technologies Used

| Area | Technologies |
|---|---|
| Programming | Python |
| Application | Streamlit |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn |
| Deep Learning | TensorFlow, Keras, LSTM |
| Database | SQLite |
| Excel Support | OpenPyXL |
| Version Control | Git, GitHub |
| Deployment | Streamlit Community Cloud |
| Data Formats | CSV, XLSX |

---

# 📂 Project Structure

```text
RetailPulse-AI-2.0/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── app_pages/
│   ├── __init__.py
│   ├── analytics.py
│   ├── business_insights_page.py
│   ├── dashboard.py
│   ├── data_upload.py
│   ├── dataset_info.py
│   └── forecasting_page.py
│
├── assets/
│   ├── dashboard_bg.png
│   └── login_bg.png
│
├── data/
│   ├── raw/
│   └── processed/
│
├── database/
│   └── users.db
│
├── models/
│   └── lstm_model.keras
│
├── outputs/
│   ├── forecasts/
│   │   └── latest_forecast.csv
│   └── metrics/
│       └── model_comparison.csv
│
└── utils/
    ├── __init__.py
    ├── auth.py
    ├── business_insights.py
    ├── column_detection.py
    ├── data_utils.py
    ├── evaluation.py
    ├── forecasting.py
    ├── preprocessing.py
    └── ui_theme.py
```

> Runtime files such as the SQLite user database, trained model, and generated forecast outputs are excluded from Git using `.gitignore`.

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/Charan-8861/RetailPulse-AI-2.0.git
```

## 2. Navigate to the Project

```bash
cd RetailPulse-AI-2.0
```

## 3. Create a Virtual Environment (Recommended)

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
source .venv/bin/activate
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 5. Run the Application

```bash
streamlit run app.py
```

The application will normally become available at:

```text
http://localhost:8501
```

---

# 📦 Requirements

Core dependencies:

```text
streamlit
pandas
numpy
scikit-learn
tensorflow
openpyxl
```

---

# 📊 Supported Retail Data

RetailPulse AI 2.0 is designed to work with retail datasets containing a date field and at least one forecasting target.

Minimum recommended structure:

```text
Date + Sales
```

or:

```text
Date + Quantity
```

Additional fields enable richer analytics:

```text
Product
Category
Region
Customer
```

The dataset does **not** need to use these exact column names because RetailPulse AI provides automatic detection and manual column mapping.

---

# ⚠️ Forecasting Considerations

Forecasting performance can be affected by:

- Amount of historical data
- Data quality
- Missing observations
- Seasonality
- Forecast frequency
- Lookback period
- Forecast horizon
- Dataset volatility
- Neural-network initialization
- LSTM training configuration

A deep learning model is not automatically superior to simpler forecasting methods.

For this reason, RetailPulse AI evaluates the LSTM against baseline models before presenting model-performance conclusions.

---

# 💼 Business Applications

RetailPulse AI 2.0 can support retail decision-making in areas such as:

- Demand forecasting
- Sales planning
- Inventory planning
- Product performance analysis
- Regional performance analysis
- Seasonal demand analysis
- Business trend identification
- Data-driven decision support

---

# 🚀 Deployment

RetailPulse AI 2.0 is deployed using **Streamlit Community Cloud** and connected directly to the GitHub repository.

### Live Application

https://retailpulse-ai-2.streamlit.app/

Deployment environment:

```text
Platform : Streamlit Community Cloud
Python   : 3.12
Branch   : main
Entry    : app.py
```

---

# 🔮 Future Enhancements

Potential future extensions include:

- GRU forecasting
- Bidirectional LSTM
- Multivariate forecasting
- Product-level forecasting
- Category-level forecasting
- Region-level forecasting
- Hyperparameter optimization
- Automatic forecasting-frequency recommendation
- Additional time-series algorithms
- Persistent cloud database integration
- Explainable AI
- Advanced inventory recommendations
- Role-based authentication

---

# 📌 Project Evolution

## RetailPulse AI — Capstone 1

Focused on:

- Excel
- SQL
- Python EDA
- Machine Learning
- Power BI
- Business Intelligence

## RetailPulse AI 2.0 — Capstone 2

Extends the original project with:

- Deep Learning
- LSTM
- Time-Series Forecasting
- Automated Model Comparison
- Predictive Intelligence
- Business Insights
- User Authentication
- Interactive Streamlit Application
- Cloud Deployment

---

# 👨‍💻 Author

**Charan R**

Data Analytics | Machine Learning | Deep Learning

---

## ⭐ Project Links

**Live Application:**  
https://retailpulse-ai-2.streamlit.app/

**Source Code:**  
https://github.com/Charan-8861/RetailPulse-AI-2.0