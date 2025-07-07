import streamlit as st
import pandas as pd
import zipfile
import io


st.set_page_config(page_title="Export Dashboard", layout="wide")
st.title("📦 Multi-Format Export Dashboard (ZIP Upload)")

uploaded_zip = st.file_uploader("Upload ZIP with Excel or CSV files", type="zip")

if uploaded_zip:
    combined_data = pd.DataFrame()

    with zipfile.ZipFile(uploaded_zip, 'r') as z:
        file_list = z.namelist()
        for file in file_list:
            try:
                with z.open(file) as f:
                    if file.endswith(".csv"):
                        df = pd.read_csv(f)
                    elif file.endswith(".xls"):
                        df = pd.read_excel(f, engine="xlrd")
                    elif file.endswith(".xlsx"):
                        df = pd.read_excel(f, engine="openpyxl")
                    else:
                        st.warning(f"⚠️ Unsupported file type: {file}")
                        continue

                    df["PRODUCT"] = file.split("/")[-1].split(".")[0]  # Use filename as product name
                    combined_data = pd.concat([combined_data, df], ignore_index=True)

            except Exception as e:
                st.warning(f"❌ Error reading {file}: {e}")

    if combined_data.empty:
        st.error("❌ No valid data extracted. Check file types or install required libraries.")
    else:
        df = combined_data.copy()
        df.columns = df.columns.str.strip()

        # Clean
        df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
        df['PRODUCT'] = df['PRODUCT'].astype(str).str.strip()
        df['QUANTITY'] = pd.to_numeric(df['QUANTITY'], errors='coerce')
        df['UNIT RATE'] = pd.to_numeric(df['UNIT RATE'], errors='coerce')
        df['TOTAL USD'] = pd.to_numeric(df['TOTAL USD'], errors='coerce')
        df = df.dropna(subset=['PRODUCT'])

        # Filters
        st.sidebar.header("🔍 Filters")
        product_search = st.sidebar.text_input("Search Product Name", "")
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

        # Tabs
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

            country_qty = filtered_df.groupby("DESTINATION")["QUANTITY"].sum().sort_values(ascending=True)
            st.write("### 📦 Total Quantity by Country")
            st.bar_chart(country_qty)

            exporter_qty = filtered_df.groupby("EXPORTER")["QUANTITY"].sum().sort_values(ascending=True)
            st.write("### 🏭 Total Quantity by Exporter")
            st.bar_chart(exporter_qty)

            product_qty = filtered_df.groupby("PRODUCT")["QUANTITY"].sum().sort_values(ascending=False)
            st.write("### 📦 Total Quantity by Product")
            st.bar_chart(product_qty)

            st.write("### 🔁 Product vs Exporter Quantity Table")
            prod_export_table = filtered_df.pivot_table(
                index="PRODUCT",
                columns="EXPORTER",
                values="QUANTITY",
                aggfunc="sum",
                fill_value=0
            )
            st.dataframe(prod_export_table)
else:
    st.info("📁 Please upload a ZIP file to begin.")
