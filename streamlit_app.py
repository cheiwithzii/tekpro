import streamlit as st
import pandas as pd
import os
import uuid

# -----------------------------
# Session unik per user
# -----------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# Optional: tampilkan session di dashboard
st.write(f"Session User ID: {st.session_state.user_id}")

# ============================
# 1. Konfigurasi & Fungsi Utils
# ============================

CSV_FILE = f"transactions_{st.session_state.user_id}.csv"

def load_transactions():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE, parse_dates=['Tanggal'])
        df['Jumlah'] = pd.to_numeric(df['Jumlah'], errors='coerce')
        df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
        return df
    else:
        # Data kosong per user
        return pd.DataFrame(columns=['Tanggal','Deskripsi','Jumlah','Kategori','Type'])

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
    st.subheader("📈 Grafik Keuangan Anda")
    df = load_transactions()

    if df.empty:
        st.warning("Belum ada data untuk divisualisasikan.")
    else:
        # Pastikan tanggal urut
        df = df.sort_values("Tanggal")

        # Filter: ambil bulan terbanyak (misal user mengisi Januari saja)
        df["Bulan"] = df["Tanggal"].dt.to_period("M")
        bulan_terbanyak = df["Bulan"].mode()[0]
        df = df[df["Bulan"] == bulan_terbanyak]

        st.info(f"Menampilkan grafik untuk bulan: **{bulan_terbanyak}**")

        # Grafik garis jumlah per hari
        daily = df.groupby("Tanggal")["Jumlah"].sum()

        st.line_chart(daily)

        # Grafik batang per kategori (hanya pengeluaran)
        expense_only = df[df["Type"] == "Pengeluaran"]
        category_sum = expense_only.groupby("Kategori")["Jumlah"].sum().abs()

        st.bar_chart(category_sum)

# ============================
# Menu 5: Upload CSV
# ============================
elif menu == "Upload CSV":
    st.subheader("📤 Upload File CSV untuk ditambahkan ke database")

    uploaded = st.file_uploader("Pilih file CSV", type="csv")

    if uploaded is not None:
        try:
            # Baca sampel untuk deteksi delimiter
            sample = uploaded.read().decode(errors="ignore")
            uploaded.seek(0)

            header = sample.split("\n")[0]
            if ";" in header:
                delimiter = ";"
            elif "," in header:
                delimiter = ","
            elif "\t" in header:
                delimiter = "\t"
            else:
                delimiter = ";"

            # Coba berbagai encoding
            encodings = ["utf-8-sig", "utf-8", "latin1", "cp1252"]
            new_df = None
            for enc in encodings:
                try:
                    uploaded.seek(0)
                    new_df = pd.read_csv(uploaded, sep=delimiter, encoding=enc)
                    break
                except:
                    continue

            if new_df is None:
                st.error("❌ Gagal membaca file CSV.")
                st.stop()

            # Hapus baris kosong
            new_df = new_df.dropna(how="all")

            # Kolom wajib
            required_cols = ["Tanggal", "Deskripsi", "Jumlah", "Kategori", "Type"]
            if not all(col in new_df.columns for col in required_cols):
                st.error(f"❌ Kolom tidak sesuai. Harus ada: {', '.join(required_cols)}")
                st.dataframe(new_df)
                st.stop()

            # ==========================
            # 🔥 PARSER TANGGAL SUPER LENGKAP
            # ==========================
            from dateutil import parser
            
            def flexible_date_parser(x):
                try:
                    return parser.parse(str(x), dayfirst=True)
                except:
                    return None

            new_df["Tanggal"] = new_df["Tanggal"].apply(flexible_date_parser)

            # ==========================
            # 🔥 PARSER JUMLAH SUPER FLEKSIBEL
            # ==========================
            new_df["Jumlah"] = (
                new_df["Jumlah"]
                .astype(str)
                .str.replace(",", "")
                .str.replace(" ", "")
            )
            new_df["Jumlah"] = pd.to_numeric(new_df["Jumlah"], errors="coerce")

            # Hapus baris yang gagal diparse
            new_df = new_df.dropna(subset=["Tanggal", "Jumlah"])

            # Gabungkan dengan database lama
            old_df = load_transactions()
            combined_df = pd.concat([old_df, new_df], ignore_index=True)

            save_transactions(combined_df)

            st.success(f"✅ Berhasil! {len(new_df)} baris ditambahkan ke database.")
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
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1350&q=80");
        background-size: cover;
        background-attachment: fixed;
        background-repeat: no-repeat;
        background-position: center;
        background-color: #ffc0cb;  /* fallback pink pastel */
        height: 100vh;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Test Background")
st.write("Jika ini muncul, background juga harus terlihat.")

