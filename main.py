import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ── Page Setup ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🛠️ Demo Electromechanical Inventory Dashboard",
    layout="wide"
)

# ── Sample Data (Electromechanical Items) ───────────────────────────────
@st.cache_data
def load_sample_data():
    """
    Generates sample inventory for electromechanical components.
    """
    items = [
        "AC Motor", "DC Motor", "Stepper Motor", "Solenoid Valve",
        "Electromechanical Relay", "Bearing A (6200)", "Bearing B (6301)",
        "Limit Switch", "Proximity Sensor", "Thermal Fuse",
        "Pressure Sensor", "Transformer 24V", "Circuit Breaker",
        "Terminal Block", "Encoder", "Gearbox", "PLC Module",
        "Linear Actuator", "Power Supply 12V", "Inductive Coil"
    ]
    min_qty = np.random.randint(10, 30, len(items))
    max_qty = min_qty + np.random.randint(20, 50, len(items))
    qty = np.random.randint(0, 100, len(items))
    return pd.DataFrame({
        "Item": items,
        "Qty": qty,
        "MinQty": min_qty,
        "MaxQty": max_qty,
    })

# ── Load Data ───────────────────────────────────────────────────────────
df = load_sample_data()
# Compute Out‑of‑Bounds and Difference
out = df.copy()
out['Status'] = np.where(out.Qty < out.MinQty, 'Under Min',
                          np.where(out.Qty > out.MaxQty, 'Over Max', 'OK'))
out = out[out.Status != 'OK']
out['Diff'] = np.where(
    out.Status == 'Under Min', out.Qty - out.MinQty, out.Qty - out.MaxQty
)

# ── Sidebar Controls: Separate Sliders ───────────────────────────────────
st.sidebar.header("🔢 Alert Configuration")
# Max number of possible out items
total_under = len(out[out.Status == 'Under Min'])
total_over = len(out[out.Status == 'Over Max'])
# Slider for Under-Min items
n_under = st.sidebar.slider(
    label="📉 Top Under-Min Items",
    min_value=1,
    max_value=total_under if total_under > 1 else 1,
    value=min(5, total_under),
    help="Number of items below minimum to display"
)
# Slider for Over-Max items
n_over = st.sidebar.slider(
    label="📈 Top Over-Max Items",
    min_value=1,
    max_value=total_over if total_over > 1 else 1,
    value=min(5, total_over),
    help="Number of items above maximum to display"
)

# ── App Title and Metrics ─────────────────────────────────────────────────
st.title("🎛️ Ánalisis de inventario MATELPA ")
col1, col2 = st.columns(2)
col1.metric("📦 Total SKUs", len(df))
col2.metric("⚠️ Items Out-of-Bounds", len(out))

st.markdown("---")

# ── Display Top Under and Over based on sliders ─────────────────────────
st.subheader(f"🔻 Top {n_under} Under-Minimum Items")
top_under = out[out.Status == 'Under Min'].nsmallest(n_under, 'Qty')
st.dataframe(top_under.reset_index(drop=True), use_container_width=True)

st.subheader(f"🔺 Top {n_over} Over-Maximum Items")
top_over = out[out.Status == 'Over Max'].nlargest(n_over, 'Qty')
st.dataframe(top_over.reset_index(drop=True), use_container_width=True)

# ── Charts: Quantity Deviation ───────────────────────────────────────────
st.subheader("📊 Deviation from Threshold")
combined = pd.concat([top_under, top_over])
bar = alt.Chart(combined).mark_bar().encode(
    x=alt.X('Diff:Q', title='Qty − Threshold'),
    y=alt.Y('Item:N', sort='-x'),
    color=alt.Color(
        'Status:N',
        scale=alt.Scale(domain=['Under Min', 'Over Max'], range=['#1f77b4', '#d62728']),
        legend=alt.Legend(title='Status')
    ),
    tooltip=['Item', 'Qty', 'MinQty', 'MaxQty', 'Diff']
).properties(width=800, height=400)
st.altair_chart(bar, use_container_width=True)

# ── Footer ───────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Demo with hard‑coded electromechanical items—swap. NOT suited for commercial use yet.")
