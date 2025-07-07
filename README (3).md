
# 📦 Unified Export Dashboard (Streamlit App)

This Streamlit application allows pharmaceutical export managers to analyze export data with filters and visualizations.

---

## ✅ Features

### Tab 1: 📋 Dashboard
- Upload a CSV file with export data
- Filter by:
  - Product name (partial match)
  - Destination country
  - Exporter
  - Importer
  - Date range
- View:
  - Total Quantity
  - Total Revenue (USD)
  - Average Unit Rate
  - Filtered table
  - Download CSV of filtered data

### Tab 2: 📊 Visual Charts
- Bar chart of quantity by country
- Bar chart of quantity by exporter
- Pie chart of quantity distribution by country (Top 10)

---

## 🛠 Setup Instructions

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Run the app**
```bash
streamlit run app_with_tabs.py
```

---

## 🧾 CSV Format

Ensure your CSV includes the following columns:
- `DATE`
- `PRODUCT`
- `QUANTITY`
- `UNIT RATE`
- `TOTAL USD`
- `DESTINATION`
- `EXPORTER`
- `IMPORTER`

---

## 📌 Example Usage

1. Upload the export dataset CSV via the app.
2. Use sidebar to filter by product or region.
3. Analyze summary KPIs.
4. View charts to see export trends and contributions.
5. Export filtered data.

---
