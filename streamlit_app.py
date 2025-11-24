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

    import csv
    import io

    uploaded = st.file_uploader("Pilih file CSV", type="csv")

    if uploaded is not None:
        # --- AUTO DETECT ENCODING ---
        raw_data = uploaded.read()
        detected = chardet.detect(raw_data)
        encoding = detected["encoding"] if detected["encoding"] else "utf-8"
        uploaded.seek(0)

        # --- AUTO DETECT DELIMITER ---
        try:
            text_sample = raw_data.decode(encoding, errors="ignore")
            dialect = csv.Sniffer().sniff(text_sample, delimiters=",;|\t")
            delimiter = dialect.delimiter
        except:
            delimiter = ";"  # fallback default (karena CSV Anda pakai ;)

        uploaded.seek(0)

        # --- LOAD CSV DENGAN PENGAMAN ---
        try:
            new_df = pd.read_csv(
                uploaded,
                encoding=encoding,
                delimiter=delimiter,
                engine="python"
            )

            required_cols = ["Tanggal", "Deskripsi", "Jumlah", "Kategori", "Type"]

            # Cek apakah semua kolom ada
            if not all(col in new_df.columns for col in required_cols):
                st.error("❌ Format CSV tidak sesuai. Pastikan kolom: Tanggal, Deskripsi, Jumlah, Kategori, Type")
            else:
                # Normalisasi format data
                new_df["Tanggal"] = pd.to_datetime(new_df["Tanggal"], errors="coerce")
                new_df["Jumlah"] = pd.to_numeric(new_df["Jumlah"], errors="coerce")

                # Load database lama
                old_df = load_transactions()

                # Gabungkan
                combined_df = pd.concat([old_df, new_df], ignore_index=True)

                # Simpan
                save_transactions(combined_df)

                st.success("✅ CSV berhasil diupload & digabungkan ke database!")
                st.info(f"Encoding terdeteksi: **{encoding}** | Delimiter: **'{delimiter}'**")

                st.dataframe(new_df)

        except Exception as e:
            st.error("❌ Terjadi kesalahan saat membaca file, tetapi ini bukan kesalahan Anda.")
            st.code(str(e))

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

import streamlit as st

# ====== PINK PASTEL THEME ======
st.markdown("""
<style>

[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #ffe6ee 0%, #fff6fa 60%, #ffffff 100%);
}

[data-testid="stHeader"] {
    background-color: rgba(255, 255, 255, 0);
}

[data-testid="stSidebar"] {
    background-color: #ffeef4;
}

.stButton > button {
    background-color: #ffb6c9 !important;
    color: white !important;
    border-radius: 8px !important;
    border: none;
}

.stButton > button:hover {
    background-color: #ff9db8 !important;
}

.stTextInput > div > div > input,
.stSelectbox > div > div > select,
[data-baseweb="textarea"] > textarea {
    background-color: #fff1f6 !important;
}

</style>
""", unsafe_allow_html=True)
