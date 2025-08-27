import streamlit as st
import datetime
from itables.streamlit import interactive_table


def render_buyers_sellers(df_bs):
    st.header("Buyers & Sellers")

    # === Define available date range ===
    min_date = df_bs["date"].min().date()
    max_date = df_bs["date"].max().date()

    # === Session state initialization ===
    if "bs_start" not in st.session_state:
        st.session_state.bs_start = min_date
    if "bs_end" not in st.session_state:
        st.session_state.bs_end = max_date

    # === Two separate date pickers ===
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start date",
            value=st.session_state.bs_start,
            min_value=min_date,
            max_value=max_date,
            format="YYYY/MM/DD"
        )
    with col2:
        end_date = st.date_input(
            "End date",
            value=st.session_state.bs_end,
            min_value=min_date,
            max_value=max_date,
            format="YYYY/MM/DD"
        )

    st.caption("👉 Select start and end dates, then click *Apply period* to update Buyers & Sellers data.")

    # === Apply button updates session state ===
    if st.button("Apply Buyers & Sellers period"):
        if start_date > end_date:
            st.error("⚠️ End date must be after start date")
        else:
            st.session_state.bs_start = start_date
            st.session_state.bs_end = end_date
            st.success(f"📅 Period applied: {start_date} → {end_date}")

    # Always use session_state values for filtering
    start_date = st.session_state.bs_start
    end_date = st.session_state.bs_end

    # === Filter by selected period ===
    bs_period = df_bs[
        (df_bs["date"].dt.date >= start_date) &
        (df_bs["date"].dt.date <= end_date)
    ].copy()

    if not bs_period.empty:
        # === Consolidate by broker ===
        bs_summary = (
            bs_period.groupby("broker").agg(
                start_balance=("start_balance", "first"),
                end_balance=("end_balance", "last")
            ).reset_index()
        )
        bs_summary["total_change"] = bs_summary["end_balance"] - bs_summary["start_balance"]
        bs_summary["variation_pct"] = (bs_summary["total_change"] / bs_summary["start_balance"]) * 100
        bs_summary["Category"] = bs_summary["total_change"].apply(
            lambda x: "Buyer" if x > 0 else ("Seller" if x < 0 else "Neutral")
        )

        # === Quick summary ===
        num_brokers = bs_summary["broker"].nunique()
        avg_var = bs_summary["variation_pct"].mean()
        top_buyer = bs_summary.loc[bs_summary["total_change"].idxmax()]
        top_seller = bs_summary.loc[bs_summary["total_change"].idxmin()]

        st.markdown(f"""
        **Summary ({start_date} → {end_date}):**  
        - 📊 Brokers: **{num_brokers}**  
        - 📈 Avg. Variation: **{avg_var:.2f}%**  
        - 🟢 Top Buyer: **{top_buyer['broker']}** ({top_buyer['total_change']:,})  
        - 🔴 Top Seller: **{top_seller['broker']}** ({top_seller['total_change']:,})
        """)

        # === Broker selectbox with "All brokers" option ===
        options = ["All brokers"] + bs_summary["broker"].unique().tolist()
        selected_broker = st.selectbox("Select broker (Buyers & Sellers):", options, index=0)

        if selected_broker == "All brokers":
            bs_filtered = bs_summary.copy()
        else:
            bs_filtered = bs_summary[bs_summary["broker"] == selected_broker]

        # === Format numbers ===
        if not bs_filtered.empty:
            bs_filtered["start_balance"] = bs_filtered["start_balance"].map("{:,.0f}".format)
            bs_filtered["end_balance"] = bs_filtered["end_balance"].map("{:,.0f}".format)
            bs_filtered["total_change"] = bs_filtered["total_change"].map("{:,.0f}".format)
            bs_filtered["variation_pct"] = bs_filtered["variation_pct"].map("{:.2f}%".format)

        # === CSS fix for footer ===
        st.markdown(
            """
            <style>
            div.dataTables_wrapper .row:last-child {
                display: flex !important;
                justify-content: space-between !important;
                align-items: center !important;
                white-space: nowrap !important;
                margin-top: 6px !important;
                font-size: 11px !important;
                padding: 2px 6px !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # === Show interactive table ===
        interactive_table(
            bs_filtered,
            classes="display nowrap",
            paging=True,
            pageLength=20,
            scrollX=True,
            style="width:100%",
            dom="<'row'<'col-sm-12'tr>>"
                + "<'row d-flex justify-content-between align-items-center'<'col-sm-6'i><'col-sm-6'p>>"
        )

    else:
        st.warning("⚠️ No data available for Buyers & Sellers in the selected period.")

