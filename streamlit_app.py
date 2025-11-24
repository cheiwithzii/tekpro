import streamlit as st
import pandas as pd
import os

# ============================
# 1. Konfigurasi & Fungsi Utils
# ============================

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

# ============================
# 2. Tampilan Streamlit
# ============================

st.title("📘 Spendee Fast")
st.write("Kelola pemasukan dan pengeluaran harian Anda tanpa terlewat")

menu = st.sidebar.selectbox(
    "Menu",
    ["Tambah Transaksi", "Lihat Transaksi", "Ringkasan", "Grafik", "Upload CSV", "Perbaikan Data"]
)

# ============================
# Menu 1: Tambah Transaksi
# ============================
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

# ============================
# Menu 2: Lihat Transaksi
# ============================
elif menu == "Lihat Transaksi":
    st.subheader("📃 Daftar Transaksi")
    df = load_transactions()

    if df.empty:
        st.warning("Belum ada transaksi.")
    else:
        st.dataframe(df.sort_values("Tanggal", ascending=False))

# ============================
# Menu 3: Ringkasan
# ============================
elif menu == "Ringkasan":
    st.subheader("📊 Ringkasan keuangan Anda")
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

# ============================
# Menu 4: Grafik
# ============================
elif menu == "Grafik":
    st.subheader("📈 Grafik keuangan Anda")
    df = load_transactions()

    if df.empty:
        st.warning("Belum ada data untuk divisualisasikan.")
    else:
        st.line_chart(df.groupby("Tanggal")["Jumlah"].sum())

        expense_only = df[df["Type"] == "Pengeluaran"]
        st.bar_chart(expense_only.groupby("Kategori")["Jumlah"].sum().abs())

# ============================
# Menu 5: Upload CSV
# ============================
elif menu == "Upload CSV":
    st.subheader("📤 Upload File CSV untuk ditambahkan ke database dalam format tanggal, deskripsi, jumlah, kategori, dan type")

    uploaded = st.file_uploader("Pilih file CSV", type="csv")

    if uploaded is not None:
        new_df = pd.read_csv(uploaded)

        try:
            # Normalisasi kolom
            required_cols = ["Tanggal", "Deskripsi", "Jumlah", "Kategori", "Type"]
            if not all(col in new_df.columns for col in required_cols):
                st.error("Format CSV tidak sesuai. Pastikan kolom sesuai format database.")
            else:
                # Konversi tipe data
                new_df["Tanggal"] = pd.to_datetime(new_df["Tanggal"], errors="coerce")
                new_df["Jumlah"] = pd.to_numeric(new_df["Jumlah"], errors="coerce")

                old_df = load_transactions()
                combined_df = pd.concat([old_df, new_df], ignore_index=True)

                save_transactions(combined_df)
                st.success("CSV berhasil diupload dan digabungkan ke database!")
                st.dataframe(new_df)

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

# ============================
# Menu 6: Perbaikan Data
# ============================
elif menu == "Perbaikan Data":
    st.subheader("🛠️ Silakan perbaiki data Anda yang salah")

    df = load_transactions()

    if df.empty:
        st.warning("Tidak ada data untuk diperbaiki.")
    else:
        st.write("🔍 Data saat ini:")
        st.dataframe(df)

        st.write("---")
        st.write("### Hapus Baris Berdasarkan Index")

        index_to_delete = st.number_input("Masukkan index baris yang ingin dihapus", min_value=0, max_value=len(df)-1)

        if st.button("Hapus Baris"):
            df = df.drop(index_to_delete).reset_index(drop=True)
            save_transactions(df)
            st.success(f"Baris dengan index {index_to_delete} berhasil dihapus!")
            st.dataframe(df)

        st.write("---")
        st.write("### Hapus Data Berdasarkan Kategori")

        kategori_list = df["Kategori"].unique()
        kategori_select = st.selectbox("Pilih kategori untuk dihapus", kategori_list)

        if st.button("Hapus Kategori Ini"):
            df = df[df["Kategori"] != kategori_select]
            save_transactions(df)
            st.success(f"Kategori '{kategori_select}' berhasil dihapus!")
            st.dataframe(df)

        st.write("---")
        st.write("### Hapus Transaksi dengan Nilai Tidak Masuk Akal")

        if st.button("Bersihkan Nilai Tidak Wajar! "):
            before = len(df)
            df = df[df["Jumlah"].abs() < 10_000_000]
            removed = before - len(df)
            save_transactions(df)
            st.success(f"{removed} baris tidak wajar berhasil dibersihkan!")
            
        st.write("---")
        st.write("### Reset Database (opsional)")

        if st.button("RESET SEMUA DATA ⚠️"):
            save_transactions(pd.DataFrame(columns=["Tanggal", "Deskripsi", "Jumlah", "Kategori", "Type"]))
            st.error("Semua data telah dihapus!")

