import streamlit as st
import pandas as pd
import os

CSV_FILE = "transactions.csv"

def load_transactions():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")
        df["Jumlah"] = pd.to_numeric(df["Jumlah"], errors="coerce")
        return df
    else:
        return pd.DataFrame(columns=["Tanggal", "Deskripsi", "Jumlah", "Kategori", "Type"])

def save_transactions(df):
    df.to_csv(CSV_FILE, index=False)

def add_transaction(date, description, amount, category, ttype):
    df = load_transactions()

    # Penanda pemasukan/pengeluaran
    if ttype == "Pengeluaran":
        amount = -abs(amount)
    else:
        amount = abs(amount)

    new_row = {
        "Tanggal": date,
        "Deskripsi": description,
        "Jumlah": amount,
        "Kategori": category,
        "Type": ttype
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_transactions(df)

st.title("📘 Aplikasi Manajemen Keuangan Anak Kos — Versi Lengkap")
st.write("Aplikasi ini mengelola keuangan dengan database CSV dan mendukung upload data Excel/CSV.")

menu = st.sidebar.selectbox(
    "Menu",
    ["Tambah Transaksi", "Upload File", "Lihat Transaksi", "Ringkasan", "Analisis Lanjutan", "Grafik"]
)

if menu == "Tambah Transaksi":
    st.subheader("➕ Tambah Transaksi Manual")

    ttype = st.selectbox("Jenis Transaksi", ["Pengeluaran", "Pemasukan"])
    date = st.date_input("Tanggal")
    description = st.text_input("Deskripsi")
    amount = st.number_input("Jumlah (Rp)", min_value=0.0)
    category = st.text_input("Kategori (contoh: Makanan, Transport)")

    if st.button("Simpan Transaksi"):
        add_transaction(date, description, amount, category, ttype)
        st.success("Transaksi berhasil ditambahkan!")

elif menu == "Upload File":
    st.subheader("📤 Upload File CSV atau Excel")

    uploaded = st.file_uploader("Pilih file CSV/Excel", type=["csv", "xlsx"])

    if uploaded:
        # Auto detect format
        if uploaded.name.endswith(".csv"):
            df_new = pd.read_csv(uploaded)
        elif uploaded.name.endswith(".xlsx"):
            df_new = pd.read_excel(uploaded)

        # Standardisasi format
        df_new["Tanggal"] = pd.to_datetime(df_new["Tanggal"])
        df_new["Jumlah"] = pd.to_numeric(df_new["Jumlah"])

        # Gabungkan dengan database utama
        df_old = load_transactions()
        df_all = pd.concat([df_old, df_new], ignore_index=True)
        save_transactions(df_all)

        st.success("Data berhasil di-upload & digabung ke database!")
        st.dataframe(df_all.tail())

elif menu == "Lihat Transaksi":
    st.subheader("📃 Daftar Transaksi")
    df = load_transactions()

    if df.empty:
        st.warning("Belum ada transaksi.")
    else:
        st.dataframe(df.sort_values("Tanggal", ascending=False))

elif menu == "Ringkasan":
    st.subheader("📊 Ringkasan Keuangan")
    df = load_transactions()

    if df.empty:
        st.warning("Belum ada data.")
    else:
        total_income = df[df["Type"] == "Pemasukan"]["Jumlah"].sum()
        total_expense = abs(df[df["Type"] == "Pengeluaran"]["Jumlah"].sum())
        balance = total_income - total_expense

        st.metric("Total Pemasukan", f"Rp {total_income:,.0f}")
        st.metric("Total Pengeluaran", f"Rp {total_expense:,.0f}")
        st.metric("Saldo Akhir", f"Rp {balance:,.0f}")

        st.subheader("🔎 Pengeluaran per kategori")
        exp_by_cat = (
            df[df["Type"] == "Pengeluaran"]
            .groupby("Kategori")["Jumlah"]
            .sum()
            .abs()
        )
        st.dataframe(exp_by_cat)

elif menu == "Grafik":
    st.subheader("📊 Grafik Keuangan")
    df = load_transactions()

    if df.empty:
        st.warning("Tidak ada data grafik.")
    else:
        st.write("### Grafik Tren Harian")
        st.line_chart(df.groupby("Tanggal")["Jumlah"].sum())

        st.write("### Grafik Pengeluaran Berdasarkan Kategori")
        st.bar_chart(df[df["Type"] == "Pengeluaran"].groupby("Kategori")["Jumlah"].sum().abs())
