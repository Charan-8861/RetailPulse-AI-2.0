# 📊 RetailPulse AI 2.0

## Deep Learning-Powered Retail Analytics and Demand Forecasting

RetailPulse AI 2.0 is an intelligent retail analytics and forecasting application developed using Python, Streamlit, Machine Learning, and Deep Learning.

The application allows users to upload retail datasets, automatically identify important retail fields, explore business performance, convert transactional data into time-series data, train an LSTM forecasting model, compare it with baseline forecasting methods, and generate future demand or sales forecasts.

RetailPulse AI 2.0 extends the original **RetailPulse AI: Smart Retail Analytics** project by introducing Deep Learning-based predictive intelligence.

---

## 🎯 Project Objective

The objective of RetailPulse AI 2.0 is to build a reusable retail forecasting application capable of working with different retail datasets rather than being restricted to a single predefined dataset.

The system provides:

- Automated retail dataset configuration
- Retail business analytics
- Time-series preparation
- LSTM-based forecasting
- Baseline forecasting comparison
- Model performance evaluation
- Future sales/demand forecasting
- Downloadable forecast results

---

## ✨ Key Features

### 📁 Flexible Dataset Upload

Users can upload retail datasets in:

- CSV
- Excel (`.xlsx`)

The application is designed to support different retail datasets through configurable column mapping.

### 🧠 Automatic Column Detection

RetailPulse AI attempts to automatically detect:

- Date
- Sales / Revenue
- Quantity / Demand
- Product
- Category
- Region
- Customer

Users can manually correct the detected columns before continuing.

### 📊 Retail Analytics Dashboard

The application generates business analytics including:

- Total Sales
- Total Quantity
- Number of Customers
- Number of Products
- Monthly Sales Trend
- Sales by Category
- Sales by Region
- Top Products by Sales

### 🤖 LSTM Demand Forecasting

The Deep Learning forecasting pipeline includes:

- Weekly or Monthly forecasting
- Configurable lookback periods
- Configurable training epochs
- Configurable forecast horizon
- MinMax scaling
- Chronological train/test split
- Stacked LSTM architecture
- Dropout regularization
- Early Stopping
- Learning-rate reduction

### 🧪 Forecasting Model Comparison

The application compares:

1. LSTM
2. Naive Forecast
3. Seasonal Naive Forecast

Models are evaluated using:

- MAE
- RMSE
- MAPE
- R2

The application automatically identifies the best-performing model based on MAPE.

### 🔮 Future Forecasting

RetailPulse AI generates future sales or demand forecasts and provides:

- Forecast dates
- Forecast values
- Historical + future forecast visualization
- Forecast trend interpretation
- Downloadable CSV results

---

## 🧠 Deep Learning Architecture

The current LSTM network consists of:

```text
Input Time-Series Sequence
        ↓
LSTM Layer - 32 Units
        ↓
Dropout - 20%
        ↓
LSTM Layer - 16 Units
        ↓
Dropout - 20%
        ↓
Dense Layer - 8 Units (ReLU)
        ↓
Dense Output Layer
        ↓
Forecast
```

The model uses:

```text
Optimizer : Adam
Loss      : Mean Squared Error
```

Training also uses:

- EarlyStopping
- ReduceLROnPlateau

---

## 🔄 Application Workflow

```text
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
Train / Test Split
        ↓
Data Scaling
        ↓
LSTM Training
        ↓
Baseline Forecasting
        ↓
Model Evaluation
        ↓
Best Model Identification
        ↓
Future Forecast
        ↓
Business Insight
        ↓
Download Forecast
```

---

## 📈 Model Evaluation

A sample weekly forecasting experiment produced the following results:

| Model | MAE | RMSE | MAPE | R2 |
|---|---:|---:|---:|---:|
| Naive Forecast | 15,154.12 | 20,085.85 | 17.68% | 0.446 |
| LSTM | 20,591.01 | 26,591.51 | 21.82% | 0.028 |
| Seasonal Naive | 22,879.39 | 27,781.07 | 24.32% | -0.075 |

### Result

For this experiment, the **Naive Forecast** achieved the lowest MAPE and was therefore identified as the best-performing forecasting method.

The LSTM achieved a MAPE of approximately **21.82%**.

This comparison demonstrates the importance of benchmarking Deep Learning models against simpler forecasting methods instead of assuming that a more complex model will always provide better predictions.

> Model results may vary between training runs because neural-network training involves random initialization and optimization.

---

## 🛠️ Technologies Used

### Programming

- Python

### Application Development

- Streamlit

### Data Processing

- Pandas
- NumPy

### Machine Learning

- Scikit-learn

### Deep Learning

- TensorFlow
- Keras
- LSTM

### Data Formats

- CSV
- Microsoft Excel

---

## 📂 Project Structure

```text
RetailPulse-AI-2.0/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   └── processed/
│
├── models/
│   └── lstm_model.keras
│
├── outputs/
│   ├── forecasts/
│   │   └── latest_forecast.csv
│   │
│   └── metrics/
│       └── model_comparison.csv
│
└── utils/
    ├── __init__.py
    ├── column_detection.py
    ├── data_utils.py
    ├── preprocessing.py
    ├── forecasting.py
    └── evaluation.py
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <YOUR-REPOSITORY-URL>
```

### 2. Navigate to the project

```bash
cd RetailPulse-AI-2.0
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

If Streamlit is installed in an Anaconda environment on Windows, the application can also be started using:

```powershell
C:\Users\DELL\anaconda3\python.exe -m streamlit run app.py
```

---

## 📦 Requirements

The main dependencies are:

```text
streamlit
pandas
numpy
scikit-learn
tensorflow
openpyxl
```

---

## 📊 Supported Retail Data

The application is designed to work with retail datasets containing a date field and at least one forecasting target.

Minimum recommended structure:

```text
Date + Sales
```

or:

```text
Date + Quantity
```

Additional fields such as the following enable more analytics:

```text
Product
Category
Region
Customer
```

Because users manually confirm column mappings, the dataset does not need to use exactly the same column names as the original development dataset.

---

## ⚠️ Forecasting Considerations

Forecasting performance depends on:

- Amount of historical data
- Data quality
- Seasonality
- Forecast frequency
- Lookback period
- Dataset volatility
- LSTM training configuration

A Deep Learning model is not automatically superior to simpler forecasting approaches.

RetailPulse AI therefore evaluates LSTM against baseline models before presenting model-performance conclusions.

---

## 🚀 Future Enhancements

Possible future extensions include:

- GRU forecasting
- Bidirectional LSTM
- Multivariate forecasting
- Product-level forecasting
- Category-level forecasting
- Hyperparameter optimization
- Automatic frequency recommendation
- Additional forecasting algorithms
- Cloud deployment
- Database integration
- Explainable AI components

---

## 💼 Business Applications

RetailPulse AI can support retail decision-making in areas such as:

- Demand forecasting
- Sales planning
- Inventory planning
- Product performance analysis
- Regional performance analysis
- Seasonal demand analysis
- Business trend identification

---

## 📌 Project Evolution

### RetailPulse AI – Capstone 1

Focused on:

- Excel
- SQL
- Python EDA
- Machine Learning
- Power BI
- Business Intelligence

### RetailPulse AI 2.0 – Capstone 2

Extends the project with:

- Deep Learning
- LSTM
- Time-Series Forecasting
- Automated Model Comparison
- Predictive Intelligence
- Interactive Streamlit Application

---

## 👨‍💻 Author

**Charan R**

Data Analytics | Machine Learning | Deep Learning