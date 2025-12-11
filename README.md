

###   <h1 align="center">Inventory Management BI System</h1>   

# Executive Summary

End-to-end Python + Streamlit inventory management BI system. Simulated SKU-level data, EOQ & ROP policy, risk classification (stock-out / below ROP / overstock), and an interactive control room for replenishment decisions.

-----

<p align="center">
  <a href="https://inventory-management-bi-system.streamlit.app/" target="_blank">
    <img src="https://img.shields.io/badge/View%20Interactive BI System on%20Streamlit-006699?style=for-the-badge&logo=tableau&logoColor=white"/>
  </a>
</p>

![Screenshot 2025-12-11 231534](https://github.com/user-attachments/assets/e9cbc89d-9e72-4a2d-876a-a52f01d4a11b)
<img width="2790" height="650" alt="Screenshot 2025-12-11 232219 - Copy" src="https://github.com/user-attachments/assets/e4357fb4-6c98-4fab-91fe-4d06a5ff4898" />

### <h1 align="center">🎯 Main Business Questions & KPIs</h1>  

This project focuses on answering 4 key questions about **inventory risk, stock availability, and replenishment planning** in the *Inventory Management BI System*.

---

### 1️⃣ Which categories & SKUs drive the most stock value and risk?

Identify which **categories, suppliers, and SKUs** concentrate:

- **High stock value** (capital at risk)  
- **High demand** (avg_daily_sales)  
- **Critical risk flags**: `Stock-out`, `Below ROP`, `Overstock`  

This helps prioritize where planners should focus first when monitoring inventory health.

---

### 2️⃣ Where are we exposed to stock-outs and service level failures?

Analyze items that are:

- At or **below Reorder Point (ROP)**  
- Already in **Stock-out** status  
- With **low Days of Cover** relative to demand and lead time  

Goal: surface SKUs that threaten **service level** and require **immediate replenishment actions**.

---

### 3️⃣ Where is working capital locked in overstocked or slow-moving items?

Detect segments where:

- **Days of Cover** is very high  
- **Stock Value** is high but **demand is weak**  
- Items are tagged as **Overstock**  

This supports decisions on **stock reduction**, **markdowns**, or **order postponement** to free up cash.

---

### 4️⃣ What replenishment plan balances availability and holding cost?

Using the EOQ & ROP policy, evaluate:

- **Total recommended order quantity** and **budget**  
- Impact of **service level (z-score)** and **holding cost multiplier**  
- Recommended orders by **category, supplier, and SKU**

The goal is to generate a **data-driven replenishment plan** that:

- Minimizes **stock-out risk**  
- Controls **holding & ordering costs**  
- Aligns inventory investment with **actual demand behavior**

###   <h1 align="center">SKU Drilldown</h1>   

![Screenshot 2025-12-11 232326](https://github.com/user-attachments/assets/c065dce4-d894-46a2-8c9b-1f0a2265e443)

<h1 align="center">📊 Project Measures, KPIs & Calculated Fields</h1>
<hr>

<table>
  <tr>
    <!-- LEFT COLUMN -->
    <td width="50%" valign="top" style="padding-right:20px;">

  <h2>📌 Current_Stock</h2>
  <ul>
    <li>The physical units currently available on hand for each SKU.</li>
    <li>Used to evaluate stock-out risk and decide whether a new order is needed.</li>
  </ul>
  <hr>

  <h2>📌 Avg_Daily_Sales</h2>
  <ul>
    <li>Average number of units sold per day.</li>
    <li>Core driver for demand, Days of Cover, EOQ and ROP calculations.</li>
  </ul>
  <hr>

  <h2>📌 Lead_Time_Days</h2>
  <ul>
    <li>Number of days between placing a purchase order and receiving the stock.</li>
    <li>Higher lead time increases safety stock and ROP.</li>
  </ul>
  <hr>

  <h2>📌 Stock_Value</h2>
  <ul>
    <li>Total inventory value locked in a SKU or category.</li>
    <li><strong>Stock_Value = Current_Stock × Unit_Cost</strong></li>
    <li>Used to monitor where working capital is concentrated.</li>
  </ul>
  <hr>

  <h2>📌 Risk_Flag</h2>
  <ul>
    <li>Business rule that classifies each SKU into:
      <ul>
        <li><code>Stock-out</code> – Current_Stock ≤ 0</li>
        <li><code>Below ROP</code> – Current_Stock &lt; ROP</li>
        <li><code>Overstock</code> – Days_of_Cover is very high</li>
        <li><code>Healthy</code> – everything else</li>
      </ul>
    </li>
    <li>Drives the alerts and focus areas in the control room.</li>
  </ul>
  <hr>

  <h2>📌 Calculated Field: Days_of_Cover</h2>
  <pre><code>Days_of_Cover = Current_Stock / Avg_Daily_Sales</code></pre>
  <ul>
    <li>How many days we can keep selling before running out (if demand stays stable).</li>
    <li>Key KPI for service level and overstock detection.</li>
  </ul>
  <hr>

  <h2>📌 Calculated Field: Annual_Demand</h2>
  <pre><code>Annual_Demand = Avg_Daily_Sales × 365</code></pre>
  <ul>
    <li>Used as the demand input for EOQ calculations.</li>
  </ul>
  <hr>

</td>

<!-- RIGHT COLUMN -->
<td width="50%" valign="top" style="padding-left:20px;">

  <h2>📌 Order_Cost</h2>
  <ul>
    <li>Fixed cost per purchase order (logistics, admin, processing).</li>
    <li>Higher order cost pushes EOQ upward (larger but fewer orders).</li>
  </ul>
  <hr>

  <h2>📌 Holding_Cost</h2>
  <ul>
    <li>Annual cost of holding one unit in stock (capital, storage, risk of obsolescence).</li>
    <li>In the app, a multiplier lets planners simulate different capital cost scenarios.</li>
  </ul>
  <hr>

  <h2>📌 Calculated Field: EOQ</h2>
  <pre><code>EOQ = √( 2 × Annual_Demand × Order_Cost / Holding_Cost_Adjusted )</code></pre>
  <ul>
    <li>Economic Order Quantity: the theoretical “optimal” order size.</li>
    <li>Balances ordering cost vs. holding cost.</li>
  </ul>
  <hr>

  <h2>📌 Calculated Field: Safety_Stock</h2>
  <pre><code>Safety_Stock = z × Demand_Std × √(Lead_Time_Days)</code></pre>
  <ul>
    <li>Extra buffer stock to protect the desired service level.</li>
    <li><code>z</code> comes from the chosen service level (e.g. 95%, 98%, 99%).</li>
  </ul>
  <hr>

  <h2>📌 Calculated Field: ROP (Reorder Point)</h2>
  <pre><code>ROP = (Avg_Daily_Sales × Lead_Time_Days) + Safety_Stock</code></pre>
  <ul>
    <li>Inventory level at which a new order should be placed.</li>
    <li>Ensures stock arrives just before we hit zero, under normal demand.</li>
  </ul>
  <hr>

  <h2>📌 Calculated Field: Recommended_Order_Qty</h2>
  <pre><code>IF Current_Stock &lt; ROP:
    Recommended_Order_Qty = MAX( round(EOQ), ROP - Current_Stock )
ELSE:
    Recommended_Order_Qty = 0</code></pre>
  <ul>
    <li>Prescriptive quantity used in the Replenishment Planner.</li>
    <li>Combines the EOQ logic with the actual stock gap vs ROP.</li>
  </ul>
  <hr>

</td>
  </tr>
</table>



###   <h1 align="center">Replenishment Planner</h1>   

![Screenshot 2025-12-11 232306](https://github.com/user-attachments/assets/130d2f19-90bd-416e-ae47-d4007205b313)

<p align="center">
<img width="550" height="400" alt="Screenshot 2025-12-04 225311" src="https://github.com/user-attachments/assets/4df172ff-6259-4af7-ad3e-51924d2be2a1" />
  </p>
  
### 🎯 Insights

- **Home Cleaning carries the highest stock value**, at around **$0.8M**, putting it roughly **25–30% higher** than the lowest category and making it the main contributor to total inventory value.
- **Kitchen has the lowest stock value**, at about **$0.63M**, suggesting either lower demand or more conservative replenishment compared to the other categories.
- **Paper and Personal Care sit in the mid-range (~$0.75M and ~$0.67M)**, meaning overall stock value is relatively balanced across categories, but capital is most concentrated in **Home Cleaning + Paper**, which should be monitored closely for over- or under-stock risk.

  ---

#### Demand vs Days of Cover
<p align="center">
<img width="550" height="400" alt="Screenshot 2025-12-04 225311" src="https://github.com/user-attachments/assets/a81b20fb-8555-43a8-be5c-61d316f03313" />
  </p>

### 🎯 Insights

- **Overstock SKUs cluster at high Days of Cover (25–45 days)**, many of them with medium-to-high demand (30–80 units/day), meaning a lot of inventory is tied up in fast or medium movers that are currently over-protected.
- **Below ROP items sit mostly below ~15 Days of Cover**, and they appear across almost the full demand range, including very fast movers – these are the SKUs with the highest near-term stock-out risk.
- The chart highlights a **double-sided risk profile**: some high-demand SKUs are under-protected (Below ROP, low cover), while others with similar demand are heavily overstocked, indicating clear opportunities to rebalance inventory between SKUs.

  ---
  
#### Stock Value by Supplier (Donut)
  <p align="center">
<img width="550" height="400" alt="Screenshot 2025-12-04 225311" src="https://github.com/user-attachments/assets/ef3508b5-99db-4267-8ad7-4c3138319fc8" />
  </p>

### 🎯 Insights

- **P&G holds the largest share of stock value (~26%)**, making it the single biggest supplier exposure in the portfolio.
- **Sano (~23%) and Unilever (~21%) together account for almost half of the remaining value**, meaning that roughly **70% of inventory value** is concentrated in just three major suppliers.
- **Local Supplier A and B jointly represent about one-third of the total value (~30%)**, providing some diversification, but any disruption with the top 2–3 global suppliers would still have a disproportionate impact on stock availability.

---
  #### Number of SKUs by Category (Line)
  <p align="center">
<img width="550" height="400" alt="Screenshot 2025-12-04 225311" src="https://github.com/user-attachments/assets/f18f2e15-af86-49de-afe3-e03e2b8d244e" />
  </p>


### 🎯 Insights

- **Kitchen and Home Cleaning carry the widest assortment**, with ~42 and ~41 SKUs respectively, indicating that most of the portfolio complexity sits in these two categories.
- **Paper has the smallest assortment (~32 SKUs)**, while **Personal Care is slightly higher (~35 SKUs)**, suggesting fewer items to manage but potentially higher volume per SKU.
- The overall spread is relatively narrow, but the **heavier SKU mix in Kitchen & Home Cleaning** means that optimization efforts (delisting, rationalization, or focused planning) in these categories will have the biggest impact on operational complexity.

---


#### Inventory Risk Distribution
  <p align="center">
<img width="550" height="400" alt="Screenshot 2025-12-04 225311" src="https://github.com/user-attachments/assets/8b6836b7-3936-4975-bf76-7ec92f761374" />
  </p>

### 🎯 Insights

- **Overstock items dominate the risk profile**, with roughly **~95 SKUs flagged as Overstock vs ~55 Below ROP**, meaning the portfolio is more exposed to excess inventory than to immediate shortages.
- The high count of **Overstock SKUs** suggests significant working capital tied up in slow-moving or over-protected items that could be reduced without harming service level.
- **Below ROP SKUs still represent a sizeable minority of the portfolio**, indicating that while the main problem is overstock, there is also a non-trivial group of items that require urgent replenishment to avoid service level failures.

**Takeaways & Actions**

- The **largest risk is capital locked in overstock**, especially SKUs with **high Days of Cover (25–45 days)** and medium–high demand.  
  → Tighten reorder rules and reduce future order quantities for these items to free working capital.

- **Below ROP items are clustered at low Days of Cover (< 15 days)** across all demand levels.  
  → These SKUs should be **prioritized in the replenishment plan**, using the Recommended_Order_Qty as a minimum to protect service levels.

- Inventory value is **highly concentrated in a few categories and big suppliers**  
  (e.g., Home Cleaning + Paper, and P&G/Sano/Unilever).  
  → Any forecast or lead-time error in these pockets has a **disproportionate impact** on both availability and cash, so they require closer monitoring and more frequent policy reviews.

---

# 🤝 Stakeholder Recommendations

1. **Rebalance inventory between Overstock and Below ROP SKUs**  
   - Gradually **reduce orders** (or skip cycles) for SKUs with high Days_of_Cover and Overstock flags.  
   - Use part of the freed budget to **immediately replenish Below ROP and Stock-out items**, especially high-demand SKUs with low cover.

2. **Tighten policies for high-value categories & key suppliers**  
   - For categories with the highest **Stock_Value** (Home Cleaning, Paper), review EOQ and ROP settings to avoid excessive safety stock.  
   - For major suppliers (P&G, Sano, Unilever), align on **more reliable lead times** and **smaller, more frequent orders** where possible to reduce risk and holding cost.

3. **Simplify the assortment where complexity is highest**  
   - In categories with the **largest SKU counts (Kitchen & Home Cleaning)**, identify slow movers and overlapping SKUs for potential delisting or phase-out.  
   - This will **reduce planning complexity**, free shelf space, and focus capital on SKUs with stronger demand and better rotation.

--------
### 🧰 Tools Kit


<img width="1856" height="490" alt="tools" src="https://github.com/user-attachments/assets/fac8516e-083a-40f7-9b88-ada21124e578" />

<p align="center">
  <a href="https://inventory-management-bi-system.streamlit.app/" target="_blank">
    <img src="https://img.shields.io/badge/View%20Interactive BI System on%20Streamlit-006699?style=for-the-badge&logo=tableau&logoColor=white"/>
  </a>
</p>

<p align="center">
  <a href="Inventory_Management_BI_System.py" target="_blank">
    <img src="https://img.shields.io/badge/View%20 Python Code-ff9933?style=for-the-badge&logo=tableau&logoColor=white"/>
  </a>
</p>

