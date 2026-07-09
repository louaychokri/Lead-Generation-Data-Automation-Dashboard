import pandas as pd
import streamlit as st
from app.database.db import init_db, fetch_all_items, count_items, update_status
from app.exporters.csv_exporter import export_csv
from app.exporters.excel_exporter import export_excel


def run_dashboard():
    st.set_page_config(page_title="LeadFlow By Zarbouty", page_icon="🏢", layout="wide")
    init_db()

    st.title("LeadFlow")
    st.caption("API-first automation dashboard for web intelligence, jobs, repositories, and technical trends")

    items = fetch_all_items()
    if not items:
        st.warning("No data found yet. Run the launcher first.")
        st.code("python start_leadflow.py", language="powershell")
        return

    df = pd.DataFrame(items)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Items", count_items())
    with col2:
        st.metric("Average Score", round(df["score"].fillna(0).mean(), 2))
    with col3:
        st.metric("Sources", df["source"].nunique())
    with col4:
        st.metric("Methods", df["collection_method"].nunique())

    st.divider()
    st.subheader("Filters")
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        selected_source = st.selectbox("Source", ["All"] + sorted(df["source"].dropna().unique().tolist()))
    with f2:
        selected_status = st.selectbox("Status", ["All"] + sorted(df["status"].dropna().unique().tolist()))
    with f3:
        selected_method = st.selectbox("Collection Method", ["All"] + sorted(df["collection_method"].dropna().unique().tolist()))
    with f4:
        min_score = st.slider("Minimum Score", 0, 100, 0)

    filtered = df.copy()
    if selected_source != "All":
        filtered = filtered[filtered["source"] == selected_source]
    if selected_status != "All":
        filtered = filtered[filtered["status"] == selected_status]
    if selected_method != "All":
        filtered = filtered[filtered["collection_method"] == selected_method]
    filtered = filtered[filtered["score"].fillna(0) >= min_score]

    search_text = st.text_input("Search inside results", "")
    if search_text:
        mask = filtered.astype(str).apply(lambda row: row.str.contains(search_text, case=False, na=False).any(), axis=1)
        filtered = filtered[mask]

    st.divider()
    st.subheader("Export Filtered Results")
    e1, e2 = st.columns(2)
    with e1:
        if st.button("Export Excel"):
            st.success(f"Excel exported: {export_excel(filtered.to_dict('records'))}")
    with e2:
        if st.button("Export CSV"):
            st.success(f"CSV exported: {export_csv(filtered.to_dict('records'))}")

    st.divider()
    st.subheader("Results")
    columns = ["id", "title", "company", "source", "collection_method", "category", "location", "score", "status", "url", "description"]
    existing = [c for c in columns if c in filtered.columns]
    st.dataframe(filtered[existing], use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Update Item Status")
    if filtered.empty:
        st.info("No items match the selected filters.")
        return

    selected_id = st.selectbox("Select item ID", filtered["id"].tolist())
    new_status = st.selectbox("New status", ["New", "Contacted", "Replied", "Not Interested", "Converted"])
    if st.button("Update Status"):
        update_status(int(selected_id), new_status)
        st.success(f"Status updated for item ID {selected_id}")
        st.rerun()


if __name__ == "__main__":
    run_dashboard()
