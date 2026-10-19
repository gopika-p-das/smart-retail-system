# 🛒 Smart Retail Management System

An intelligent inventory management and demand forecasting web application designed for supermarket managers. Built with **Django**, **Scikit-Learn Machine Learning**, and modern **Bootstrap 5 UI**.

---

## 🚀 Key Features

- **📊 Manager Dashboard:** Real-time visibility into total stock, retail revenue, low-stock warnings, and demand forecasts.
- **📦 Products & Inventory Management:** Full CRUD operations for supermarket inventory, category classifications, and lead-time tracking.
- **📈 ML Demand Forecasting:** Predicts future customer purchase demand per product using trained regression pipelines.
- **🛡️ Inventory Optimization:** Automated recommendations (`REORDER`, `MAINTAIN`, `OVERSTOCKED`) based on predicted demand, current stock, and safety buffer thresholds.
- **🚚 Supplier Management:** Vendor tracking with delivery lead time and fulfillment status analysis.
- **📑 Reports & Analytics:** Comprehensive reports for sales volume, critical stock alerts, and restocking expenditure.

---

## 🛠️ Tech Stack

- **Backend:** Python 3, Django 5
- **Machine Learning:** Scikit-Learn, Pandas, NumPy, Joblib
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Bootstrap Icons
- **Database:** SQLite3

---

## 💻 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/gopika-p-das/smart-retail-system.git
   cd smart-retail-system
   ```

2. **Install required dependencies:**
   ```bash
   pip install django scikit-learn pandas numpy joblib
   ```

3. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Start the development server:**
   ```bash
   python manage.py runserver
   ```
   Open `http://127.0.0.1:8000/` in your browser.
