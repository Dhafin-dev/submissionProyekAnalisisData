import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Konfigurasi halaman dashboard
st.set_page_config(page_title="E-Commerce Public Dataset Dashboard", layout="wide")

# Fungsi memuat data dengan cache agar cepat
@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv")
    datetime_cols = [
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
    for col in datetime_cols:
        df[col] = pd.to_datetime(df[col])
    return df

all_df = load_data()

# --- SIDEBAR FILTER ---
st.sidebar.header("Filter Rentang Waktu")
min_date = all_df["order_purchase_timestamp"].min().date()
max_date = all_df["order_purchase_timestamp"].max().date()

start_date, end_date = st.sidebar.date_input(
    label="Pilih Rentang Tanggal Transaksi",
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

# Filter data sesuai pilihan sidebar
main_df = all_df[
    (all_df["order_purchase_timestamp"].dt.date >= start_date) &
    (all_df["order_purchase_timestamp"].dt.date <= end_date)
].copy()

# --- HEADER & METRIK UTAMA ---
st.title("📊 E-Commerce Public Dataset Dashboard")
st.markdown("Dashboard interaktif untuk memantau performa penjualan kategori produk, kepuasan pelanggan berdasarkan ketepatan pengiriman, serta segmentasi pelanggan (RFM).")

col1, col2, col3 = st.columns(3)
with col1:
    total_orders = main_df["order_id"].nunique()
    st.metric("Total Pesanan (Delivered)", value=f"{total_orders:,}")
with col2:
    total_revenue = main_df["price"].sum()
    st.metric("Total Pendapatan", value=f"${total_revenue:,.2f}")
with col3:
    avg_rating = main_df.drop_duplicates(subset=["order_id"])["review_score"].mean()
    st.metric("Rata-Rata Skor Ulasan", value=f"{avg_rating:.2f} / 5.0")

st.divider()

# --- VISUALISASI 1: PENDAPATAN KATEGORI PRODUK ---
st.subheader("1. Performa Kategori Produk Berdasarkan Total Pendapatan")
cat_rev = main_df.groupby("product_category_name_english")["price"].sum().reset_index()
cat_rev.rename(columns={"price": "total_revenue"}, inplace=True)

top_5 = cat_rev.sort_values(by="total_revenue", ascending=False).head(5)
bottom_5 = cat_rev.sort_values(by="total_revenue", ascending=True).head(5)

fig1, ax1 = plt.subplots(nrows=1, ncols=2, figsize=(16, 6))
colors_top = ["#1f77b4", "#a6cee3", "#a6cee3", "#a6cee3", "#a6cee3"]
colors_bottom = ["#d62728", "#fbb4ae", "#fbb4ae", "#fbb4ae", "#fbb4ae"]

sns.barplot(x="total_revenue", y="product_category_name_english", data=top_5, palette=colors_top, hue="product_category_name_english", legend=False, ax=ax1[0])
ax1[0].set_title("5 Kategori Pendapatan Tertinggi", fontsize=14, fontweight="bold")
ax1[0].set_xlabel("Total Pendapatan")
ax1[0].set_ylabel(None)

sns.barplot(x="total_revenue", y="product_category_name_english", data=bottom_5, palette=colors_bottom, hue="product_category_name_english", legend=False, ax=ax1[1])
ax1[1].set_title("5 Kategori Pendapatan Terendah", fontsize=14, fontweight="bold")
ax1[1].set_xlabel("Total Pendapatan")
ax1[1].set_ylabel(None)

plt.tight_layout()
st.pyplot(fig1)

st.divider()

# --- VISUALISASI 2: KETERLAMBATAN PENGIRIMAN VS SKOR ULASAN ---
st.subheader("2. Pengaruh Ketepatan Pengiriman terhadap Skor Ulasan Pelanggan")
orders_unique = main_df[["order_id", "order_delivered_customer_date", "order_estimated_delivery_date", "review_score"]].drop_duplicates(subset=["order_id"]).dropna()

orders_unique["delivery_status"] = np.where(
    orders_unique["order_delivered_customer_date"] > orders_unique["order_estimated_delivery_date"],
    "Terlambat (Late)",
    "Tepat Waktu (On-Time)"
)

review_summary = orders_unique.groupby("delivery_status")["review_score"].mean().reset_index()

fig2, ax2 = plt.subplots(figsize=(8, 4))
sns.barplot(x="delivery_status", y="review_score", data=review_summary, palette=["#2ca02c", "#d62728"], hue="delivery_status", legend=False, ax=ax2)
for container in ax2.containers:
    ax2.bar_label(container, fmt="%.2f", fontsize=11, fontweight="bold", padding=3)
ax2.set_title("Rata-Rata Skor Ulasan (Skala 1–5)", fontsize=13, fontweight="bold")
ax2.set_xlabel("Status Pengiriman")
ax2.set_ylabel("Rata-Rata Skor")
ax2.set_ylim(0, 5.2)
st.pyplot(fig2)

st.divider()

# --- VISUALISASI 3: ANALISIS RFM ---
st.subheader("3. Pelanggan Terbaik Berdasarkan Parameter RFM")
rfm_df = main_df.groupby(by="customer_unique_id", as_index=False).agg(
    max_order_timestamp=("order_purchase_timestamp", "max"),
    frequency=("order_id", "nunique"),
    monetary=("price", "sum")
)
recent_date = main_df["order_purchase_timestamp"].max()
rfm_df["recency"] = (recent_date - rfm_df["max_order_timestamp"]).dt.days
rfm_df["short_id"] = rfm_df["customer_unique_id"].str[:8]

fig3, ax3 = plt.subplots(nrows=1, ncols=3, figsize=(18, 5))
colors_rfm = ["#1f77b4", "#a6cee3", "#a6cee3", "#a6cee3", "#a6cee3"]

top_recency = rfm_df.sort_values(by="recency", ascending=True).head(5)
sns.barplot(y="recency", x="short_id", data=top_recency, palette=colors_rfm, hue="short_id", legend=False, ax=ax3[0])
ax3[0].set_title("By Recency (Hari)", fontsize=13, fontweight="bold")
ax3[0].set_xlabel("Customer ID")
ax3[0].set_ylabel(None)
ax3[0].tick_params(axis="x", rotation=45)

top_frequency = rfm_df.sort_values(by="frequency", ascending=False).head(5)
sns.barplot(y="frequency", x="short_id", data=top_frequency, palette=colors_rfm, hue="short_id", legend=False, ax=ax3[1])
ax3[1].set_title("By Frequency (Pesanan)", fontsize=13, fontweight="bold")
ax3[1].set_xlabel("Customer ID")
ax3[1].set_ylabel(None)
ax3[1].tick_params(axis="x", rotation=45)

top_monetary = rfm_df.sort_values(by="monetary", ascending=False).head(5)
sns.barplot(y="monetary", x="short_id", data=top_monetary, palette=colors_rfm, hue="short_id", legend=False, ax=ax3[2])
ax3[2].set_title("By Monetary (Total Belanja)", fontsize=13, fontweight="bold")
ax3[2].set_xlabel("Customer ID")
ax3[2].set_ylabel(None)
ax3[2].tick_params(axis="x", rotation=45)

plt.tight_layout()
st.pyplot(fig3)