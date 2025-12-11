import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

PRIMARY_COLOR = "#006699"
ACCENT_COLOR = "#ff9933"
white_color = "#ffffff"

COLOR_PALETTE = [
    PRIMARY_COLOR,
    ACCENT_COLOR,
    "#004466",
    "#ffb366",
    "#3399cc",
]

RISK_COLOR_MAP = {
    "Healthy": COLOR_PALETTE[0],
    "Stock-out": COLOR_PALETTE[1],
    "Below ROP": COLOR_PALETTE[1],
    "Overstock": COLOR_PALETTE[2],
}


def style_fig(fig, height=320):
    """Apply common white background + black text to all charts."""
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="black"),
        xaxis=dict(
            title_font=dict(color="black"),
            tickfont=dict(color="black"),
        ),
        yaxis=dict(
            title_font=dict(color="black"),
            tickfont=dict(color="black"),
        ),
        legend=dict(
            title_font=dict(color="black"),
            font=dict(color="black"),
        ),
    )
    return fig


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Inventory Management BI System",
    layout="wide"
)
st.title("Inventory Management BI System")
# ================= DATA GENERATION =================
@st.cache_data
def load_base_inventory(n_items: int = 150) -> pd.DataFrame:
    rng = np.random.default_rng(42)

    categories = ["Home Cleaning", "Personal Care", "Paper", "Kitchen"]
    suppliers = ["Sano", "Unilever", "P&G", "Local Supplier A", "Local Supplier B"]

    records = []
    for i in range(n_items):
        sku_id = f"SKU-{1000 + i}"
        category = rng.choice(categories)
        supplier = rng.choice(suppliers)

        avg_daily_sales = float(rng.uniform(3, 80))  # units / day
        demand_std = avg_daily_sales * rng.uniform(0.2, 0.6)
        lead_time_days = int(rng.integers(3, 21))
        current_stock = int(rng.integers(0, int(avg_daily_sales * 45)))

        unit_cost = float(rng.uniform(5, 40))
        unit_price = unit_cost * rng.uniform(1.2, 1.9)

        annual_demand = avg_daily_sales * 365
        order_cost = rng.uniform(80, 250)  # per order
        holding_rate = rng.uniform(0.18, 0.32)  # 18–32% / year
        holding_cost = unit_cost * holding_rate

        stock_value = current_stock * unit_cost

        records.append({
            "sku_id": sku_id,
            "category": category,
            "supplier": supplier,
            "avg_daily_sales": round(avg_daily_sales, 2),
            "demand_std": round(demand_std, 2),
            "lead_time_days": lead_time_days,
            "current_stock": current_stock,
            "unit_cost": round(unit_cost, 2),
            "unit_price": round(unit_price, 2),
            "annual_demand": round(annual_demand, 0),
            "order_cost": round(order_cost, 2),
            "holding_cost": round(holding_cost, 2),
            "stock_value": round(stock_value, 2),
        })

    df = pd.DataFrame(records)

    df["days_of_cover"] = np.where(
        df["avg_daily_sales"] > 0,
        df["current_stock"] / df["avg_daily_sales"],
        np.nan
    )

    return df


def apply_policy(df_base: pd.DataFrame, z: float, holding_multiplier: float) -> pd.DataFrame:
    """Calculate EOQ, safety stock, ROP, risk flags under a given policy."""
    df = df_base.copy()

    df["holding_cost_adj"] = df["holding_cost"] * holding_multiplier

    annual_demand = df["avg_daily_sales"] * 365
    df["eoq"] = np.sqrt((2 * annual_demand * df["order_cost"]) / df["holding_cost_adj"])

    safety_stock = z * df["demand_std"] * np.sqrt(df["lead_time_days"])
    df["safety_stock"] = safety_stock.round().astype(int)

    rop = df["avg_daily_sales"] * df["lead_time_days"] + df["safety_stock"]
    df["rop"] = rop.round().astype(int)

    df["risk_flag"] = np.select(
        [
            df["current_stock"] <= 0,
            df["current_stock"] < df["rop"],
            df["days_of_cover"] > 7
        ],
        ["Stock-out", "Below ROP", "Overstock"],
        default="Healthy"
    )

    df["recommended_order_qty"] = np.where(
        df["current_stock"] < df["rop"],
        np.maximum(df["eoq"].round().astype(int), df["rop"] - df["current_stock"]),
        0
    )

    return df


base_df = load_base_inventory()


# ================= SIDEBAR FILTERS & MODEL PARAMS =================
st.sidebar.header("Filters")
with st.sidebar.expander("Model parameters", expanded=True):
    service_level = st.select_slider(
        "Target service level",
        options=[0.90, 0.95, 0.98, 0.99],
        value=0.95,
        format_func=lambda x: f"{int(x*100)}%"
    )
    holding_mult = st.slider(
        "Holding cost adjustment",
        min_value=0.8,
        max_value=1.2,
        value=1.0,
        step=0.05,
        help="1.0 = base holding cost. Increase to simulate higher capital cost."
    )


with st.sidebar.expander("Inventory filters", expanded=True):
    risk_view = st.radio(
        "Risk view",
        options=["All items", "At risk only", "Overstock only", "Custom"],
        index=0
    )

    min_cov, max_cov = st.slider(
        "Days of cover",
        min_value=0,
        max_value=120,
        value=(0, 120)
    )
    category_filter = st.multiselect(
        "Category",
        options=sorted(base_df["category"].unique()),
        default=sorted(base_df["category"].unique())
    )

    supplier_filter = st.multiselect(
        "Supplier",
        options=sorted(base_df["supplier"].unique()),
        default=sorted(base_df["supplier"].unique())
    )



    if risk_view == "All items":
        risk_filter = ["Stock-out", "Below ROP", "Healthy", "Overstock"]
    elif risk_view == "At risk only":
        risk_filter = ["Stock-out", "Below ROP"]
    elif risk_view == "Overstock only":
        risk_filter = ["Overstock"]
    else:
        risk_filter = st.multiselect(
            "Risk status (custom)",
            options=["Stock-out", "Below ROP", "Healthy", "Overstock"],
            default=["Stock-out", "Below ROP", "Overstock"]
        )


# Map service level to z-score (approx)
z_map = {0.90: 1.28, 0.95: 1.65, 0.98: 2.05, 0.99: 2.33}
z_value = z_map[service_level]

df_policy = apply_policy(base_df, z=z_value, holding_multiplier=holding_mult)

# Apply filters
df_f = df_policy.copy()
if category_filter:
    df_f = df_f[df_f["category"].isin(category_filter)]
if supplier_filter:
    df_f = df_f[df_f["supplier"].isin(supplier_filter)]
if risk_filter:
    df_f = df_f[df_f["risk_flag"].isin(risk_filter)]

df_f = df_f[
    (df_f["days_of_cover"] >= min_cov) &
    (df_f["days_of_cover"] <= max_cov)
]


# ================= TOP KPI BANNERS =================
total_stock_value = df_f["stock_value"].sum()
items_at_risk = (df_f["risk_flag"].isin(["Stock-out", "Below ROP"])).sum()
overstock_items = (df_f["risk_flag"] == "Overstock").sum()
avg_days_cover = df_f["days_of_cover"].mean()
total_rec_qty = df_f["recommended_order_qty"].sum()
rec_budget = (df_f["recommended_order_qty"] * df_f["unit_cost"]).sum()


def kpi_banner(title: str, value: str, color: str = "#006699"):
    st.markdown(
        f"""
        <div style="
            background-color:{color};
            color:black;
            padding:0.9rem 1rem;
            border-radius:2rem;
            border-color:#006699;
            border:6px solid #006699;
            text-align:center;
            box-shadow:0 0 12px rgba(0,0,0,0.25);
        ">
            <div style="font-size:1.6rem; opacity:0.9; margin-bottom:0.2rem;">
                {title}
            </div>
            <div style="font-size:2.1rem; font-weight:700;">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_banner("Total Stock Value", f"${total_stock_value:,.0f}", color=white_color)
with c2:
    kpi_banner("Items At Risk", f"{int(items_at_risk)}", color=white_color)
with c3:
    kpi_banner("Overstock Items", f"{int(overstock_items)}", color=white_color)
with c4:
    kpi_banner(
        "Avg Days of Cover",
        f"{avg_days_cover:,.1f}" if not np.isnan(avg_days_cover) else "N/A",
        color=white_color,
    )

st.caption(
    f"Policy: service level **{int(service_level*100)}%** "
    f"(z = {z_value}) · holding cost x **{holding_mult:.2f}**"
)

# ================= TABS =================
tab_overview, tab_planner, tab_sku = st.tabs(
    ["📊 Overview", "📦 Replenishment Planner", "🔍 SKU Drilldown"]
)
# ---------- TAB 1: OVERVIEW ----------
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

# ---------- TAB 2: REPLENISHMENT PLANNER ----------
with tab_planner:
    st.subheader("Replenishment Plan (Below ROP / Stock-out)")
    plan_df = df_f[df_f["risk_flag"].isin(["Stock-out", "Below ROP"])].copy()
    plan_df = plan_df[
        [
            "sku_id", "category", "supplier",
            "current_stock", "rop", "eoq",
            "recommended_order_qty", "days_of_cover",
            "avg_daily_sales", "lead_time_days",
            "unit_cost"
        ]
    ].sort_values("recommended_order_qty", ascending=False)

    p1, p2 = st.columns(2)
    p1.metric("Total Recommended Quantity", int(total_rec_qty))
    p2.metric("Budget for Recommended Orders", f"${rec_budget:,.0f}")

    if len(plan_df) > 0:
        st.dataframe(plan_df, use_container_width=True, height=420)
    else:
        st.info("No SKUs currently below ROP under this policy and filters.")


# ---------- TAB 3: SKU DRILLDOWN ----------
@st.cache_data
def simulate_daily_demand(seed: int, avg: float, std: float, days: int = 60):
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.today(), periods=days, freq="D")
    demand = rng.normal(loc=avg, scale=std, size=days)
    demand = np.clip(demand, 0, None)
    return pd.DataFrame({"date": dates, "demand": demand})


with tab_sku:
    if len(df_f) == 0:
        st.info("No data for current filters.")
    else:
        st.subheader("SKU Drilldown")

        sku_choice = st.selectbox(
            "Select SKU",
            options=sorted(df_f["sku_id"].unique())
        )

        sku_row = df_f[df_f["sku_id"] == sku_choice].iloc[0]

        c1, c2, c3 = st.columns(3)
        c1.metric("Current stock", int(sku_row["current_stock"]))
        c2.metric("Reorder point (ROP)", int(sku_row["rop"]))
        c3.metric("Recommended order qty", int(sku_row["recommended_order_qty"]))

        c4, c5, c6 = st.columns(3)
        c4.metric("Avg daily sales", f"{sku_row['avg_daily_sales']:.1f} units")
        c5.metric("Days of cover", f"{sku_row['days_of_cover']:.1f}")
        c6.metric("Lead time", f"{int(sku_row['lead_time_days'])} days")

        st.markdown(
            f"**Risk status:** `{sku_row['risk_flag']}` · "
            f"Supplier: `{sku_row['supplier']}` · "
            f"Category: `{sku_row['category']}`"
        )

        st.markdown("---")
        st.markdown("**Simulated last 60 days of demand**")

        sim_df = simulate_daily_demand(
            seed=int(sku_row.name),
            avg=float(sku_row["avg_daily_sales"]),
            std=float(sku_row["demand_std"])
        )

        fig_d = px.line(
            sim_df,
            x="date",
            y="demand",
            labels={"demand": "Units"},
        )
        fig_d.update_traces(line=dict(color=PRIMARY_COLOR))
        fig_d = style_fig(fig_d, height=350)
        st.plotly_chart(fig_d, use_container_width=True)


df_policy.to_csv("inventory_policy_data.csv", index=False)
df_f.to_csv("inventory_filtered_data.csv", index=False)
