# 🌿 EcoPackAI - Sustainable Packaging Recommendation System

An AI-powered web application that helps businesses choose eco-friendly packaging materials. The system uses machine learning to predict costs and CO₂ emissions, providing smart recommendations based on product requirements.

---

## 📋 Project Overview

This project demonstrates a complete end-to-end machine learning pipeline - from data collection to deployment. The system analyzes packaging materials and recommends the best options based on sustainability, cost, and performance factors.

---

## 🔧 Project Workflow

### Step 1: Data Collection & Loading
**Files:** `data_processor.py`, `load_data.py`

- Loaded 100+ packaging materials dataset from CSV files
- Data includes material properties: strength, weight capacity, biodegradability, recyclability, cost, and CO₂ emissions
- Stored in `data/` folder with multiple dataset variations

### Step 2: Data Processing & Feature Engineering
**Files:** `ml_dataset_preparation.py`, `dataset_preparation/`

- Cleaned raw data and handled missing values
- Created derived features: cost efficiency index, CO₂ impact score, material suitability score
- Normalized features for ML model training
- Split data into training (80%) and testing (20%) sets
- Saved processed datasets in `dataset_preparation/` folder

### Step 3: Machine Learning Model Training
**Files:** `train_models.py`, `cost_model.pkl`, `co2_model.pkl`

- **Cost Prediction Model:** Random Forest Regressor - predicts material cost per kg
- **CO₂ Emission Model:** XGBoost Regressor - predicts carbon footprint
- Trained on 14 engineered features
- Saved trained models as `.pkl` files for production use
- Model metrics stored in `model_metrics.csv`

### Step 4: Backend API Development
**Files:** `backend/app.py`, `backend/ml_engine.py`, `backend/database.py`

- Built Flask REST API with multiple endpoints
- `/api/recommendations` - Returns AI-powered material suggestions
- `/api/analytics` - Provides dashboard data and statistics
- `/api/health` - API health check endpoint
- Integrated ML models for real-time predictions
- API key authentication for security

### Step 5: Frontend Development
**Files:** `frontend/index.html`, `frontend/app.js`, `frontend/style.css`

- Created responsive single-page application
- Product input form with validation
- Results display with material cards and comparison table
- Interactive dashboard with Plotly.js charts
- Export functionality (PDF/Excel reports)

### Step 6: Deployment
**Files:** `Dockerfile`, `requirements.txt`

- Containerized application with Docker
- Deployed on Hugging Face Spaces
- Configured for production environment

---

## 🖥️ Website Features & Output

### 1. New Request Page
- **Input Form:** Enter product details (name, category, weight, volume, fragility, temperature, humidity, shelf life, quantity)
- **Priority Selection:** Choose between Cost, Sustainability, or Balanced optimization
- **Submit:** Get instant AI recommendations

### 2. Results Page
- **Top 3 Material Cards:** Shows best matches with suitability scores
- **Detailed Comparison Table:** Side-by-side comparison of all recommended materials
- **Metrics Display:**
  - Cost per kg (USD)
  - CO₂ emission (kg)
  - Strength (MPa)
  - Recyclability (%)
  - Suitability score (%)

### 3. Dashboard Analytics
- **CO₂ Reduction:** Shows environmental impact savings vs traditional packaging
- **Cost Savings:** Displays money saved using AI recommendations
- **Total Requests:** Count of recommendations made
- **Top Material:** Most recommended material type
- **Charts:**
  - Environmental Impact Comparison (Bar chart)
  - Cost Efficiency Analysis (Bar chart)
  - Material Selection Distribution (Pie/Donut chart)
  - Performance Trends (Line chart)
  - Sustainability Metrics (Bar chart with recyclability scores)

### 4. Export Options
- **PDF Report:** Comprehensive analytics report with all metrics and charts
- **Excel Export:** Raw data export for further analysis

---

## 🛠️ Technology Stack

| Category | Technologies |
|----------|-------------|
| **Backend** | Python, Flask, Flask-CORS |
| **ML/AI** | scikit-learn, XGBoost, pandas, numpy, joblib |
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap |
| **Visualization** | Plotly.js, Chart.js |
| **Export** | jsPDF, SheetJS (XLSX) |
| **Deployment** | Docker, Hugging Face Spaces |

---

## 🚀 How to Run Locally

```bash
# Clone the repository
git clone <repository-url>

# Install dependencies
pip install -r requirements.txt

# Run the backend
cd backend
python app.py

# Open browser at http://localhost:7860
```

---

## 🔗 Live Demo

**Hugging Face Spaces:** [https://huggingface.co/spaces/vasudevan31/Package-Recommendation-System](https://huggingface.co/spaces/vasudevan31/Package-Recommendation-System)

---

## 📊 Sample Results

When you submit a product request, the system returns:

| Material | Cost/kg | CO₂ (kg) | Strength | Recyclability | Score |
|----------|---------|----------|----------|---------------|-------|
| Bamboo Fiber Pack | $52.80 | 0.65 | 55 MPa | 90% | 89% |
| Recycled Paper Board | $45.50 | 0.85 | 45 MPa | 85% | 85% |
| Bioplastic Container | $78.20 | 1.20 | 50 MPa | 70% | 80% |

---