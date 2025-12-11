import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sklearn.model_selection import train_test_split
import statsmodels.api as sm

import streamlit as st
import pandas as pd
import numpy as np


with tab_overview:
    st.subheader("Overview")

    # ===== ROW 1 (3 charts) =====
    col1, col2, col3 = st.columns(3)

    # 1) Stock value by Category (colored by category)
    with col1:
        st.markdown("**Stock Value by Category**")
        if len(df_f) > 0:
            by_cat = (
                df_f.groupby("category", as_index=False)["stock_value"]
                .sum()
            )
            fig1 = px.bar(
                by_cat,
                x="category",
                y="stock_value",
                color="category",
                color_discrete_sequence=COLOR_PALETTE,
                labels={"stock_value": "Stock value", "category": "Category"},
            )
            fig1 = style_fig(fig1, height=320)
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No data for current filters.")

    # 2) Demand vs Days of Cover (scatter bubble)
    with col2:
        st.markdown("**Demand vs Days of Cover**")
        if len(df_f) > 0:
            fig2 = px.scatter(
                df_f,
                x="avg_daily_sales",
                y="days_of_cover",
                color="risk_flag",
                color_discrete_map=RISK_COLOR_MAP,
                size="stock_value",
                hover_data=["sku_id", "category", "supplier"],
                labels={
                    "avg_daily_sales": "Avg daily sales (units)",
                    "days_of_cover": "Days of cover",
                    "risk_flag": "Risk status",
                },
            )
            fig2 = style_fig(fig2, height=320)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No data for current filters.")

    # 3) Stock Value by Supplier (donut)
    with col3:
        st.markdown("**Stock Value by Supplier (Donut)**")
        if len(df_f) > 0:
            by_sup = (
                df_f.groupby("supplier", as_index=False)["stock_value"]
                .sum()
            )
            fig3 = px.pie(
                by_sup,
                names="supplier",
                values="stock_value",
                hole=0.55,
                color="supplier",
                color_discrete_sequence=COLOR_PALETTE,
            )
            fig3.update_traces(textinfo="percent+label")
            fig3 = style_fig(fig3, height=320)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No data for current filters.")

    st.markdown("---")

    # ===== ROW 2 (3 charts) =====
    col4, col5, col6 = st.columns(3)

    # 4) Inventory Risk Distribution (bar)
    with col4:
        st.markdown("**Inventory Risk Distribution**")
        if len(df_f) > 0:
            risk_counts = (
                df_f.groupby("risk_flag", as_index=False)["sku_id"]
                .count()
                .rename(columns={"sku_id": "count"})
            )
            fig4 = px.bar(
                risk_counts,
                x="risk_flag",
                y="count",
                color="risk_flag",
                color_discrete_map=RISK_COLOR_MAP,
                labels={
                    "risk_flag": "Risk status",
                    "count": "Number of SKUs",
                },
            )
            fig4 = style_fig(fig4, height=320)
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No data for current filters.")

    # 5) Number of SKUs by Category (LINE)
    with col5:
        st.markdown("**Number of SKUs by Category (Line)**")
        if len(df_f) > 0:
            by_cat_count = (
                df_f.groupby("category", as_index=False)["sku_id"]
                .count()
                .rename(columns={"sku_id": "count"})
            )
            fig5 = px.line(
                by_cat_count,
                x="category",
                y="count",
                markers=True,
                color_discrete_sequence=[PRIMARY_COLOR],
                labels={
                    "category": "Category",
                    "count": "Number of SKUs",
                },
            )
            fig5 = style_fig(fig5, height=320)
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.info("No data for current filters.")

    # 6) Recommended order quantity by category (bar)
    with col6:
        st.markdown("**Recommended Order Qty by Category**")
        if len(df_f) > 0:
            by_cat_order = (
                df_f.groupby("category", as_index=False)["recommended_order_qty"]
                .sum()
            )
            fig6 = px.bar(
                by_cat_order,
                x="category",
                y="recommended_order_qty",
                color="category",
                color_discrete_sequence=COLOR_PALETTE,
                labels={
                    "recommended_order_qty": "Recommended qty (units)",
                    "category": "Category",
                },
            )
            fig6 = style_fig(fig6, height=320)
            st.plotly_chart(fig6, use_container_width=True)
        else:
            st.info("No data for current filters.")

