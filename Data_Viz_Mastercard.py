import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="🛍️ MasterClothe Dashboard", layout="wide")
st.title("🛍️ MasterClothe Remodel Analysis Dashboard")
st.caption("Powered by pandas, slay, and Streamlit 💅")

# Load Data
@st.cache_data

def load_data():
    scenario_df = pd.read_csv("Scenario3_Data.csv")
    competitor_df = pd.read_csv("Competitor_Master.csv")
    store_df = pd.read_csv("Store_Master.csv")
    customer_df = pd.read_csv("Customer_Master.csv")
    item_df = pd.read_csv("Item_Master.csv")
    return scenario_df, competitor_df, store_df, customer_df, item_df

scenario_df, competitor_df, store_df, customer_df, item_df = load_data()

# Toggle-based visualization selection
visual_option = st.selectbox(
    "Choose a visualization to explore:",
    [
        "Store Distribution by Market (All, Top, Bottom)",
        "Competitor Store Count by Market",
        "Top vs Bottom 7 Store Sales"
    ]
)

# Store Distribution by Market (Final Key Visual)
if visual_option == "Store Distribution by Market (All, Top, Bottom)":
    sales_data = scenario_df
    store_sales = sales_data.groupby('store_id', as_index=False).agg(units_sold=('units_sold', 'sum'))
    merged_data = pd.merge(store_sales, store_df, on="store_id", how="left")
    total_stores_per_market = merged_data.groupby('store_market', as_index=False).size()
    total_stores_per_market['group'] = 'All Stores'

    top_stores = merged_data.nlargest(7, 'units_sold')
    bottom_stores = merged_data.nsmallest(10, 'units_sold')

    top_locations = top_stores.groupby('store_market', as_index=False).size()
    bottom_locations = bottom_stores.groupby('store_market', as_index=False).size()

    top_locations['group'] = 'Top Performing Stores'
    bottom_locations['group'] = 'Bottom Performing Stores'

    comparison_locations = pd.concat([total_stores_per_market, top_locations, bottom_locations], ignore_index=True)
    comparison_locations = comparison_locations.pivot(index="store_market", columns="group", values="size").fillna(0).reset_index()
    comparison_locations = comparison_locations.melt(id_vars="store_market", var_name="group", value_name="count")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x='store_market', y='count', hue='group', data=comparison_locations,
                palette='Set1', dodge=True, ax=ax)

    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.text(p.get_x() + p.get_width()/2, height - (height * 0.2), f'{int(height)}',
                    ha='center', fontsize=12, fontweight='bold', color='white')

    ax.set_title('Store Distribution by Market (All, Top, Bottom) - Units Sold', fontsize=16, fontweight='bold')
    ax.set_xlabel('Store Market')
    ax.set_ylabel('Number of Stores')
    plt.xticks(rotation=45, ha='right')
    ax.legend(title="Store Category", loc="upper right")
    st.pyplot(fig)

# Competitor Store Count by Market
elif visual_option == "Competitor Store Count by Market":
    competitor_counts = competitor_df.groupby("comp_market").size().reset_index(name="num_competitors")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(competitor_counts["comp_market"], competitor_counts["num_competitors"], color="steelblue")
    ax.set_xlabel("Number of Competitor Stores")
    ax.set_ylabel("Market")
    ax.set_title("Number of Competitors in Each Market")
    st.pyplot(fig)

# Top vs Bottom 7 Store Sales
elif visual_option == "Top vs Bottom 7 Store Sales":
    data = {
        "store_id": [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010,
                     1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020,
                     1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030,
                     1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039, 1040,
                     1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048, 1049, 1050],
        "units_sold": [37756, 37851, 36704, 36880, 36898, 37235, 37857, 18734, 36602, 18465,
                       37380, 18342, 37734, 18329, 37016, 37030, 37543, 38871, 37857, 18050,
                       37533, 37336, 37403, 37433, 18697, 37736, 37464, 38494, 36410, 37351,
                       37732, 37800, 38590, 37413, 18036, 36623, 36990, 37835, 38726, 18215,
                       19022, 38403, 38211, 38126, 37446, 17957, 37160, 36397, 37485, 37191]
    }

    df = pd.DataFrame(data)
    top_stores = df.nlargest(7, "units_sold")
    bottom_stores = df.nsmallest(7, "units_sold")
    comparison_df = pd.concat([top_stores, bottom_stores]).sort_values(by="units_sold", ascending=False)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(comparison_df["store_id"].astype(str), comparison_df["units_sold"], marker='o', linestyle='-', color='purple', label="Top & Bottom 7 Stores")
    ax.scatter(top_stores["store_id"].astype(str), top_stores["units_sold"], color='blue', s=100, label="Top 7 Stores")
    ax.scatter(bottom_stores["store_id"].astype(str), bottom_stores["units_sold"], color='red', s=100, label="Bottom 7 Stores")

    top_total = top_stores["units_sold"].sum()
    bottom_total = bottom_stores["units_sold"].sum()
    difference = top_total - bottom_total

    callout_text = f"Difference: {difference:,.0f} units"
    ax.text(0.75, 0.95, callout_text, ha='center', va='center', transform=ax.transAxes,
             fontsize=14, color='black', bbox=dict(facecolor='yellow', alpha=0.5, boxstyle='round,pad=0.5'))

    ax.set_xlabel("Store ID")
    ax.set_ylabel("Total Units Sold")
    ax.set_title("Performance of Top 7 vs Bottom 7 Stores")
    ax.set_xticklabels(comparison_df["store_id"].astype(str), rotation=45)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.legend()
    st.pyplot(fig)

# all in one dashboard code here
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

st.set_page_config(page_title="🛍️ MasterClothe Dashboard", layout="wide")

st.title("🛍️ MasterClothe Remodel Analysis Dashboard")
st.caption("Powered by pandas, slay, and Streamlit 💅")

# Load Data
@st.cache_data

def load_data():
    scenario_df = pd.read_csv("Scenario3_Data.csv")
    competitor_df = pd.read_csv("Competitor_Master.csv")
    store_df = pd.read_csv("Store_Master.csv")
    customer_df = pd.read_csv("Customer_Master.csv")  # Formerly Customer_Intel.csv
    item_df = pd.read_csv("Item_Master.csv")
    return scenario_df, competitor_df, store_df, customer_df, item_df

scenario_df, competitor_df, store_df, customer_df, item_df = load_data()

# --- FINAL KEY VISUAL ---
st.header("📊 Store Distribution by Market (All, Top, Bottom) - Units Sold")

# Prepare data
sales_data = scenario_df
store_sales = sales_data.groupby('store_id', as_index=False).agg(units_sold=('units_sold', 'sum'))
merged_data = pd.merge(store_sales, store_df, on="store_id", how="left")
total_stores_per_market = merged_data.groupby('store_market', as_index=False).size()
total_stores_per_market['group'] = 'All Stores'
top_stores = merged_data.nlargest(7, 'units_sold')
bottom_stores = merged_data.nsmallest(10, 'units_sold')
top_locations = top_stores.groupby('store_market', as_index=False).size()
bottom_locations = bottom_stores.groupby('store_market', as_index=False).size()
top_locations['group'] = 'Top Performing Stores'
bottom_locations['group'] = 'Bottom Performing Stores'
comparison_locations = pd.concat([total_stores_per_market, top_locations, bottom_locations], ignore_index=True)
comparison_locations = comparison_locations.pivot(index="store_market", columns="group", values="size").fillna(0).reset_index()
comparison_locations = comparison_locations.melt(id_vars="store_market", var_name="group", value_name="count")

# Plotting - main chart
fig1, ax1 = plt.subplots(figsize=(12, 6))
sns.barplot(x='store_market', y='count', hue='group', data=comparison_locations,
                 palette='Set1', dodge=True, ax=ax1)
for p in ax1.patches:
    height = p.get_height()
    if height > 0:
        ax1.text(p.get_x() + p.get_width()/2, height - (height * 0.2), f'{int(height)}',
                ha='center', fontsize=12, fontweight='bold', color='white')
ax1.set_title('Store Distribution by Market (All, Top, Bottom) - Units Sold', fontsize=16, fontweight='bold')
ax1.set_xlabel('Store Market', fontsize=12)
ax1.set_ylabel('Number of Stores', fontsize=12)
ax1.tick_params(axis='x', rotation=45)
ax1.legend(title="Store Category", loc="upper right")
fig1.tight_layout()

# --- COMPETITOR MARKET VISUAL ---
# Count unique competitor markets per region
competitor_counts = competitor_df.groupby("comp_market").size().reset_index(name="num_competitors")
fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.barh(competitor_counts["comp_market"], competitor_counts["num_competitors"], color="steelblue")
ax2.set_xlabel("Number of Competitor Stores")
ax2.set_ylabel("Market")
ax2.set_title("Number of Competitors in Each Market")

# --- TOP VS BOTTOM STORE SALES VISUAL ---
data = {
    "store_id": list(range(1001, 1051)),
    "units_sold": [37756, 37851, 36704, 36880, 36898, 37235, 37857, 18734, 36602, 18465,
                   37380, 18342, 37734, 18329, 37016, 37030, 37543, 38871, 37857, 18050,
                   37533, 37336, 37403, 37433, 18697, 37736, 37464, 38494, 36410, 37351,
                   37732, 37800, 38590, 37413, 18036, 36623, 36990, 37835, 38726, 18215,
                   19022, 38403, 38211, 38126, 37446, 17957, 37160, 36397, 37485, 37191]
}
df = pd.DataFrame(data)
top_stores = df.nlargest(7, "units_sold")
bottom_stores = df.nsmallest(7, "units_sold")
comparison_df = pd.concat([top_stores, bottom_stores]).sort_values(by="units_sold", ascending=False)
fig3, ax3 = plt.subplots(figsize=(12, 6))
ax3.plot(comparison_df["store_id"].astype(str), comparison_df["units_sold"], marker='o', linestyle='-', color='purple', label="Top & Bottom 7 Stores")
ax3.scatter(top_stores["store_id"].astype(str), top_stores["units_sold"], color='blue', s=100, label="Top 7 Stores")
ax3.scatter(bottom_stores["store_id"].astype(str), bottom_stores["units_sold"], color='red', s=100, label="Bottom 7 Stores")
top_total = top_stores["units_sold"].sum()
bottom_total = bottom_stores["units_sold"].sum()
difference = top_total - bottom_total
callout_text = f"Difference: {difference:,.0f} units"
ax3.text(0.75, 0.95, callout_text, ha='center', va='center', transform=ax3.transAxes,
         fontsize=14, color='black', bbox=dict(facecolor='yellow', alpha=0.5, boxstyle='round,pad=0.5'))
ax3.set_xlabel("Store ID")
ax3.set_ylabel("Total Units Sold")
ax3.set_title("Performance of Top 7 vs Bottom 7 Stores")
ax3.tick_params(axis='x', rotation=45)
ax3.grid(axis="y", linestyle="--", alpha=0.7)
ax3.legend()
fig3.tight_layout()

# Show all three plots side-by-side as a super visual
st.subheader("📸 All Visuals Showcase")
col1, col2, col3 = st.columns(3)

with col1:
    st.pyplot(fig1)
    st.caption("🔹 Store Distribution by Market")

with col2:
    st.pyplot(fig2)
    st.caption("🔹 Competitor Count by Market")

with col3:
    st.pyplot(fig3)
    st.caption("🔹 Top vs Bottom Store Sales")
