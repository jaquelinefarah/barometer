import streamlit as st
import datetime
from itables.streamlit import interactive_table


def render_custody(df_custody):
    st.header("Custody")

    # === Define available date range ===
    min_date = df_custody["date"].min().date()
    max_date = df_custody["date"].max().date()

    # === Session state initialization ===
    if "custody_start" not in st.session_state:
        st.session_state.custody_start = min_date
    if "custody_end" not in st.session_state:
        st.session_state.custody_end = max_date

    # === Two separate date pickers ===
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start date",
            value=st.session_state.custody_start,
            min_value=min_date,
            max_value=max_date,
            format="YYYY/MM/DD"
        )
    with col2:
        end_date = st.date_input(
            "End date",
            value=st.session_state.custody_end,
            min_value=min_date,
            max_value=max_date,
            format="YYYY/MM/DD"
        )

    st.caption("👉 Select start and end dates, then click *Apply period* to update custody data.")

    # === Apply button updates session state ===
    if st.button("Apply period"):
        if start_date > end_date:
            st.error("⚠️ End date must be after start date")
        else:
            st.session_state.custody_start = start_date
            st.session_state.custody_end = end_date
            st.success(f"📅 Period applied: {start_date} → {end_date}")

    # Always use session_state values for filtering
    start_date = st.session_state.custody_start
    end_date = st.session_state.custody_end

    # === Filter custody by selected period ===
    custody_period = df_custody[
        (df_custody["date"].dt.date >= start_date) &
        (df_custody["date"].dt.date <= end_date)
    ].copy()

    if not custody_period.empty:
        # === Consolidate custody by broker for the whole period ===
        custody_summary = (
            custody_period.groupby("broker").agg(
                start_balance=("start_balance", "first"),
                end_balance=("end_balance", "last")
            ).reset_index()
        )
        custody_summary["total_change"] = custody_summary["end_balance"] - custody_summary["start_balance"]
        custody_summary["variation_pct"] = (
            custody_summary["total_change"] / custody_summary["start_balance"]
        ) * 100

        # === Quick summary ===
        num_brokers = custody_summary["broker"].nunique()
        avg_var = custody_summary["variation_pct"].mean()
        top_gain = custody_summary.loc[custody_summary["variation_pct"].idxmax()]
        top_loss = custody_summary.loc[custody_summary["variation_pct"].idxmin()]

        st.markdown(f"""
        **Summary ({start_date} → {end_date}):**  
        - 📊 Brokers: **{num_brokers}**  
        - 📈 Avg. Variation: **{avg_var:.2f}%**  
        - 🟢 Top Gain: **{top_gain['broker']}** ({top_gain['variation_pct']:.2f}%)  
        - 🔴 Top Loss: **{top_loss['broker']}** ({top_loss['variation_pct']:.2f}%)
        """)

        # === Broker selectbox with "All brokers" option ===
        options = ["All brokers"] + custody_summary["broker"].unique().tolist()
        selected_broker = st.selectbox("Select broker:", options, index=0)

        if selected_broker == "All brokers":
            custody_filtered = custody_summary.copy()
        else:
            custody_filtered = custody_summary[custody_summary["broker"] == selected_broker]

        # === Format numbers for display ===
        if not custody_filtered.empty:
            custody_filtered["start_balance"] = custody_filtered["start_balance"].map("{:,.0f}".format)
            custody_filtered["end_balance"] = custody_filtered["end_balance"].map("{:,.0f}".format)
            custody_filtered["total_change"] = custody_filtered["total_change"].map("{:,.0f}".format)
            custody_filtered["variation_pct"] = custody_filtered["variation_pct"].map("{:.2f}%".format)

        # === CSS reforçado para o rodapé já no primeiro render ===
        st.markdown(
            """
            <style>
            div.dataTables_wrapper .row:last-child {
                display: flex !important;
                justify-content: space-between !important;
                align-items: center !important;
                white-space: nowrap !important;
                width: 100% !important;
                min-width: 100% !important;
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
            custody_filtered,
            classes="display nowrap",
            paging=True,
            pageLength=20,
            lengthMenu=[10, 20, 50, 100],
            scrollX=True,
            scrollY="600px",
            scrollCollapse=True,
            style="width:100%",
            dom="<'row'<'col-sm-12'tr>>"
                + "<'row d-flex justify-content-between align-items-center'<'col-sm-6'i><'col-sm-6'p>>"
        )

    else:
        st.warning("⚠️ No data available for the selected period.")

