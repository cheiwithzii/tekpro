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

    # Penyesuaian tanda nilai
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

st.title("📘 Aplikasi Pelacak Keuangan Anak Kos")
st.write("Kelola pemasukan dan pengeluaran harian menggunakan database CSV.")

menu = st.sidebar.selectbox(
    "Menu",
    ["Tambah Transaksi", "Lihat Transaksi", "Ringkasan", "Grafik"]
)

if menu == "Tambah Transaksi":
    st.subheader("➕ Tambah Transaksi")

    ttype = st.selectbox("Jenis Transaksi", ["Pengeluaran", "Pemasukan"])
    date = st.date_input("Tanggal")
    description = st.text_input("Deskripsi")
    amount = st.number_input("Jumlah (Rp)", min_value=0.0)
    category = st.text_input("Kategori (contoh: Makanan, Transport)")

    if st.button("Simpan Transaksi"):
        add_transaction(date, description, amount, category, ttype)
        st.success("Transaksi berhasil ditambahkan!")

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
        st.warning("Belum ada data untuk diringkas.")
    else:
        total_income = df[df["Type"] == "Pemasukan"]["Jumlah"].sum()
        total_expense = abs(df[df["Type"] == "Pengeluaran"]["Jumlah"].sum())
        balance = total_income - total_expense

        st.write(f"**Total Pemasukan:** Rp {total_income:,.0f}")
        st.write(f"**Total Pengeluaran:** Rp {total_expense:,.0f}")
        st.write(f"**Saldo Akhir:** Rp {balance:,.0f}")

        st.subheader("🔎 Pengeluaran berdasarkan kategori")
        expense_summary = (
            df[df["Type"] == "Pengeluaran"]
            .groupby("Kategori")["Jumlah"]
            .sum()
            .abs()
        )

        st.dataframe(expense_summary)

elif menu == "Grafik":
    st.subheader("📈 Grafik Keuangan")
    df = load_transactions()

    if df.empty:
        st.warning("Belum ada data untuk divisualisasikan.")
    else:
        st.line_chart(df.groupby("Tanggal")["Jumlah"].sum())

        expense_only = df[df["Type"] == "Pengeluaran"]
        st.bar_chart(expense_only.groupby("Kategori")["Jumlah"].sum().abs())
