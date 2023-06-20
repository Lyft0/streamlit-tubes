import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from geopy.geocoders import Nominatim

st.set_page_config(layout="wide")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def format_number(number):
    if abs(number) >= 1_000_000:
        return f"{number / 1_000_000:.2f}M"
    elif abs(number) >= 1_000:
        return f"{number / 1_000:.2f}K"
    else:
        return str(number)


# Membaca dataset
df = pd.read_csv("supermarket_sales.csv")
branch_A = df[df["Branch"] == 'A']
branch_B = df[df["Branch"] == 'B']
branch_C = df[df["Branch"] == 'C']


# BARIS 1
# Menampilkan judul
col1_1, col1_2 = st.columns(2)

with col1_1:
    st.title("Supermarket Sales Dashboard")

with col1_2:
    options = ['A', 'B', 'C']
    branch = st.selectbox('Pilih Cabang :', options)


#  BARIS 2
# Menampilkan jumlah penjualan, pendapatan total, dan pendapatan kotor
if(branch == 'A'):
    branch_data = branch_A
elif(branch == 'B'):
    branch_data = branch_B
elif(branch == 'C'):
    branch_data = branch_C

total_sales = format_number(branch_data["Quantity"].sum())
total_revenue = format_number(branch_data["Total"].sum())
total_gross_income = format_number(branch_data["gross income"].sum())
gross_margin = format_number(branch_data['gross margin percentage'].sum())

col2_1, col2_2, col2_3, col2_4 = st.columns(4)
with col2_1:
    st.metric("Jumlah Penjualan", total_sales)
with col2_2:
    st.metric("Pendapatan Total", total_revenue)
with col2_3:
    st.metric("Pendapatan Kotor", total_gross_income)
with col2_4:
    st.metric("Persentase Gross Margin", gross_margin[:-1] + " %")

# BARIS 3

col3_1, col3_2, col3_3 = st.columns((1.8, 2.4, 0.8))

# Menampilkan penjualan dalam rentang periode waktu (Line Plot)
with col3_1:
    branch_data["Date"] = pd.to_datetime(branch_data["Date"])
    sales_over_time = branch_data.groupby(
        "Date")["Quantity"].sum().reset_index()
    fig1 = px.line(sales_over_time, x="Date", y="Quantity",
                   title="Penjualan dalam Rentang Periode Waktu", width=450, height=400)
    fig1.update_traces()
    st.plotly_chart(fig1)

    # Menampilkan tingkat rating yang diberikan pelanggan (Bar Chart/Radial Gauge Chart)
    rating_counts = branch_data["Rating"].value_counts().reset_index()
    rating_counts.columns = ["Rating", "Count"]
    # fig6 = px.bar(rating_counts, x="Rating",
    #               y="Count", title="Tingkat Rating yang Diberikan Pelanggan", width=450, height=390)
    # st.plotly_chart(fig6)
    rating_counts['Color'] = ['red' if rating >
                              7 else 'blue' for rating in rating_counts['Rating']]

    fig6 = px.bar(rating_counts, x="Rating", y="Count",
                  title="Tingkat Rating yang Diberikan Pelanggan", width=450, height=390,
                  color='Color')  # Set the color parameter to the 'Color' column
    fig6.update_layout(showlegend=False)
    st.plotly_chart(fig6)


with col3_2:
    # Menampilkan penjualan berdasarkan kategori setiap produk (Horizontal Bar Chart)
    category_sales = branch_data.groupby(
        "Product line")["Quantity"].sum().reset_index()
    category_sales = category_sales.sort_values(by="Quantity", ascending=False)
    fig3 = px.bar(category_sales, x="Quantity", y="Product line",
                  orientation="h", title="Penjualan berdasarkan Kategori Produk",
                  text="Quantity", width=580, height=400)
    fig3.update_traces(textposition="auto")
    st.plotly_chart(fig3)

    # Membuat peta berdasarkan city
    city_sales = df.groupby("City")["Quantity"].sum().reset_index()
    # Membuat kolom Latitude dan Longitude baru
    geolocator = Nominatim(user_agent="my_app")
    city_sales["Latitude"] = city_sales["City"].apply(
        lambda city: geolocator.geocode(
            city).latitude if geolocator.geocode(city) else None
    )
    city_sales["Longitude"] = city_sales["City"].apply(
        lambda city: geolocator.geocode(
            city).longitude if geolocator.geocode(city) else None
    )
    # Menghilangkan baris dengan nilai koordinat kosong
    city_sales = city_sales.dropna(subset=["Latitude", "Longitude"])
    # Membuat scatter plot dengan plotly
    fig = px.scatter_mapbox(
        city_sales,
        lat="Latitude",
        lon="Longitude",
        hover_name="City",
        hover_data={"Latitude": False, "Longitude": False, "Quantity": True},
        zoom=2,
        mapbox_style="open-street-map",
        width=600, height=600,
        title="Penjualan Berdasarkan Lokasi"
    )
    # Mengatur tampilan marker
    fig.update_traces(marker=dict(size=15, color="blue", opacity=0.8))
    # Mengatur label nama kota pada hover
    fig.update_layout(hoverlabel=dict(
        bgcolor="black", font_size=15, font_family="Arial"))
    # Menampilkan peta menggunakan plotly chart
    st.plotly_chart(fig)


with col3_3:

    # Menampilkan Informasi Berdasarkan Gender
    gender_counts = branch_data["Gender"].value_counts().reset_index()
    gender_counts.columns = ["Gender", "Count"]
    fig8 = px.pie(gender_counts, values="Count",
                  names="Gender", title="Penjualan Berdasarkan Gender", width=300, height=280)
    st.plotly_chart(fig8)

    # Menampilkan Informasi Berdasarkan customer type
    customer_counts = branch_data["Customer type"].value_counts().reset_index()
    customer_counts.columns = ["Customer type", "Count"]
    fig8 = px.pie(customer_counts, values="Count",
                  names="Customer type", title="Penjualan Berdasarkan Tipe", width=300, height=280)
    st.plotly_chart(fig8)

    # Menampilkan profiler pelanggan untuk member atau pelanggan biasa (Bar Chart)
    customer_profiler = branch_data.groupby(
        "Payment")["Quantity"].sum().reset_index()
    fig7 = px.bar(customer_profiler, x="Payment", y="Quantity", text="Quantity", width=300, height=280,
                  title=f"Penjualan Berdasarkan Pembayaran")
    fig7.update_traces(textposition="auto")
    st.plotly_chart(fig7)


# # Menampilkan data raw dari setiap penjualan (Tabel)
# st.subheader("Data Penjualan")
# st.dataframe(branch_data)
