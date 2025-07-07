import plotly.express as px
print("Plotly is working ✅")

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Export Dashboard", layout="wide")
st.title("📦 Unified Export Dashboard")

uploaded_file = st.file_uploader("Upload Combined CSV Export Data", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Clean columns and parse data
    df.columns = df.columns.str.strip()
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
    df['PRODUCT'] = df['PRODUCT'].astype(str).str.strip()
    df['QUANTITY'] = pd.to_numeric(df['QUANTITY'], errors='coerce')
    df['UNIT RATE'] = pd.to_numeric(df['UNIT RATE'], errors='coerce')
    df['TOTAL USD'] = pd.to_numeric(df['TOTAL USD'], errors='coerce')

    df = df.dropna(subset=['PRODUCT'])

    # --- Sidebar Filters ---
    st.sidebar.header("🔍 Filters")
    product_search = st.sidebar.text_input("Search Product Name (partial match)", "")
    filtered_df = df[df["PRODUCT"].str.contains(product_search, case=False, na=False)]

    countries = filtered_df["DESTINATION"].dropna().unique()
    selected_countries = st.sidebar.multiselect("Destination Country", countries, default=countries)

    exporters = filtered_df["EXPORTER"].dropna().unique()
    selected_exporters = st.sidebar.multiselect("Exporter", exporters, default=exporters)

    importers = filtered_df["IMPORTER"].dropna().unique()
    selected_importers = st.sidebar.multiselect("Importer", importers, default=importers)

    min_date = filtered_df["DATE"].min()
    max_date = filtered_df["DATE"].max()
    date_range = st.sidebar.date_input("Date Range", [min_date, max_date])

    filtered_df = filtered_df[
        filtered_df["DESTINATION"].isin(selected_countries) &
        filtered_df["EXPORTER"].isin(selected_exporters) &
        filtered_df["IMPORTER"].isin(selected_importers)
    ]

    if len(date_range) == 2:
        filtered_df = filtered_df[
            filtered_df["DATE"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))
        ]

    # --- Tabs ---
    tab1, tab2 = st.tabs(["📋 Dashboard", "📊 Visual Charts"])

    with tab1:
        st.subheader("📊 Key Metrics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Quantity", f"{filtered_df['QUANTITY'].sum():,.2f}")
        with col2:
            st.metric("Total Revenue (USD)", f"${filtered_df['TOTAL USD'].sum():,.2f}")
        with col3:
            st.metric("Avg. Unit Rate", f"${filtered_df['UNIT RATE'].mean():,.2f}")

        with st.expander("🔍 View Filtered Data"):
            st.dataframe(filtered_df)

        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Filtered Data", csv, "filtered_export_data.csv", "text/csv")

    with tab2:
        st.subheader("📊 Visual Charts")

        # Bar Chart: Quantity by Country
        country_qty = filtered_df.groupby("DESTINATION")["QUANTITY"].sum().reset_index().sort_values("QUANTITY", ascending=False)
        fig1 = px.bar(country_qty, x="DESTINATION", y="QUANTITY", title="📦 Total Quantity by Country")
        st.plotly_chart(fig1)

        # Bar Chart: Quantity by Exporter
        exporter_qty = filtered_df.groupby("EXPORTER")["QUANTITY"].sum().reset_index().sort_values("QUANTITY", ascending=False)
        fig2 = px.bar(exporter_qty, x="EXPORTER", y="QUANTITY", title="🏭 Total Quantity by Exporter")
        st.plotly_chart(fig2)

        # Pie Chart: Quantity Share by Exporter
        top_exporters = exporter_qty.nlargest(10, "QUANTITY")
        fig3 = px.pie(top_exporters, values="QUANTITY", names="EXPORTER", title="🥧 Top 10 Exporters by Quantity")
        st.plotly_chart(fig3)

else:
    st.info("Please upload the combined export CSV file to begin.")
