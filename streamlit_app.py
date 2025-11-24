# streamlit_app.py
# Versi defensif: aman terhadap error import di baris awal (line 3 dll).
import sys

# 1) Pastikan streamlit terpasang — jika tidak, kita harus berhenti karena tidak ada UI.
try:
    import streamlit as st
except Exception as e:
    raise RuntimeError(
        "Streamlit tidak ditemukan di environment ini. "
        "Pasang dulu dengan: pip install streamlit\n\n"
        f"Detail error: {e}"
    ) from e

# 2) Import library lain secara aman — jika gagal, tampilkan pesan di UI (jangan crash).
missing_packages = []
try:
    import pandas as pd
except Exception as e:
    pd = None
    missing_packages.append(("pandas", e))

try:
    import matplotlib.pyplot as plt
except Exception as e:
    plt = None
    missing_packages.append(("matplotlib", e))

from datetime import datetime

# --- Jika ada paket yang hilang, tampilkan instruksi yang jelas di UI dan non-aktifkan fitur yang butuh paket itu ---
st.set_page_config(page_title="Aplikasi Keuangan (Aman)", layout="wide")
st.title("📊 Aplikasi Pengelola Keuangan — Versi Aman (Error-safe)")

if missing_packages:
    st.error("Beberapa paket Python yang diperlukan belum terpasang.")
    for pkg, err in missing_packages:
        st.write(f"- **{pkg}**: `{err}`")
    st.info("Pasang paket yang hilang, lalu reload aplikasi. Contoh:")
    st.code("pip install pandas matplotlib", language="bash")
    # Tampilkan menu minimal agar pengguna tetap bisa melihat antarmuka
    st.stop()

# --- Setelah semua import OK, lanjutkan aplikasi normal ---
st.success("Semua paket yang diperlukan tersedia. Aplikasi berjalan normal.")

# ---------- Utility functions ----------
def safe_read_file(uploaded):
    """Baca CSV atau Excel dengan penanganan error."""
    try:
        if uploaded.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded)
        else:
            df = pd.read_excel(uploaded)
        return df
    except Exception as e:
        st.error(f"Gagal membaca file: {e}")
        return None

def ensure_columns(df, required):
    missing = [c for c in required if c not in df.columns]
    return missing

# ---------- UI utama ----------
st.markdown("**Upload file CSV/Excel yang berisi kolom minimal:** `Tanggal`, `Jenis` (Pengeluaran/Pemasukan), `Kategori` (opsional), `Jumlah`")

uploaded = st.file_uploader("Upload file CSV/Excel (contoh kolom: Tanggal, Jenis, Kategori, Jumlah)", type=["csv", "xlsx"])

# Sedia dataframe kosong agar menu selalu muncul
df = pd.DataFrame(columns=["Tanggal", "Jenis", "Kategori", "Jumlah"])

if uploaded:
    df_read = safe_read_file(uploaded)
    if df_read is not None:
        # Normalisasi nama kolom (mengizinkan variasi huruf besar/kecil)
        df_read.columns = [c.strip() for c in df_read.columns]
        # Try several common column name variants
        mapping = {}
        cols_low = [c.lower() for c in df_read.columns]
        if "tanggal" in cols_low:
            mapping[df_read.columns[cols_low.index("tanggal")]] = "Tanggal"
        if "date" in cols_low:
            mapping[df_read.columns[cols_low.index("date")]] = "Tanggal"
        if "jenis" in cols_low:
            mapping[df_read.columns[cols_low.index("jenis")]] = "Jenis"
        if "type" in cols_low:
            mapping[df_read.columns[cols_low.index("type")]] = "Jenis"
        if "kategori" in cols_low:
            mapping[df_read.columns[cols_low.index("kategori")]] = "Kategori"
        if "category" in cols_low:
            mapping[df_read.columns[cols_low.index("category")]] = "Kategori"
        if "jumlah" in cols_low:
            mapping[df_read.columns[cols_low.index("jumlah")]] = "Jumlah"
        if "amount" in cols_low:
            mapping[df_read.columns[cols_low.index("amount")]] = "Jumlah"

        df_read = df_read.rename(columns=mapping)
        df = df_read.copy()

        required = ["Tanggal", "Jenis", "Jumlah"]
        missing = ensure_columns(df, required)
        if missing:
            st.error(f"File harus mengandung kolom: {', '.join(required)}. Kolom yang hilang: {', '.join(missing)}")
            st.stop()

        # Konversi tipe
        try:
            df["Tanggal"] = pd.to_datetime(df["Tanggal"])
        except Exception as e:
            st.error(f"Gagal konversi kolom Tanggal: {e}")
            st.stop()

        try:
            df["Jumlah"] = pd.to_numeric(df["Jumlah"], errors="coerce")
        except Exception as e:
            st.error(f"Gagal konversi kolom Jumlah: {e}")
            st.stop()

        st.success("File berhasil dimuat.")
        st.dataframe(df.head(50))

# ---------- Menu selalu muncul ----------
st.sidebar.header("Menu")
menu = st.sidebar.radio("Pilih aksi:", [
    "Lihat Data",
    "Tambah Transaksi",
    "Hapus Transaksi",
    "Analisis Terpisah",
    "Download CSV"
])

# Jika belum ada data (user belum upload) — banyak fitur non-aktifkan.
has_data = not df.empty and "Tanggal" in df.columns and "Jumlah" in df.columns and "Jenis" in df.columns

# ---------- 1. Lihat Data ----------
if menu == "Lihat Data":
    st.header("📄 Tabel Data")
    if has_data:
        st.dataframe(df)
    else:
        st.info("Belum ada data. Upload file CSV/Excel untuk melihat data.")

# ---------- 2. Tambah Transaksi ----------
elif menu == "Tambah Transaksi":
    st.header("➕ Tambah Transaksi Manual")
    tgl = st.date_input("Tanggal")
    jenis = st.selectbox("Jenis", ["Pengeluaran", "Pemasukan"])
    kategori = st.text_input("Kategori (opsional)")
    jumlah = st.number_input("Jumlah (Rp)", min_value=0.0, step=1000.0)

    if st.button("Tambahkan"):
        row = {"Tanggal": pd.to_datetime(tgl), "Jenis": jenis, "Kategori": kategori, "Jumlah": jumlah}
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        st.success("Transaksi ditambahkan.")
        st.dataframe(df.tail(10))

# ---------- 3. Hapus Transaksi ----------
elif menu == "Hapus Transaksi":
    st.header("🗑 Hapus Transaksi")
    if not has_data:
        st.info("Belum ada data untuk dihapus.")
    else:
        st.write("Tabel (reset index ditampilkan untuk memilih index):")
        st.dataframe(df.reset_index())
        idx = st.number_input("Masukkan index baris yang ingin dihapus", min_value=0, max_value=len(df)-1, step=1)
        if st.button("Hapus index"):
            df = df.drop(df.index[int(idx)]).reset_index(drop=True)
            st.success(f"Baris index {idx} dihapus.")
            st.dataframe(df.head(20))

# ---------- 4. Analisis Terpisah ----------
elif menu == "Analisis Terpisah":
    st.header("📊 Analisis Terpisah")
    if not has_data:
        st.info("Upload data dulu untuk melihat analisis.")
    else:
        # Total pemasukan & pengeluaran
        pemasukan = df[df["Jenis"].str.lower() == "pemasukan"]["Jumlah"].sum()
        pengeluaran = df[df["Jenis"].str.lower() == "pengeluaran"]["Jumlah"].sum()
        saldo = pemasukan - pengeluaran

        st.subheader("Ringkasan Keuangan")
        st.write(f"- Total Pemasukan: Rp {pemasukan:,.0f}")
        st.write(f"- Total Pengeluaran: Rp {pengeluaran:,.0f}")
        st.write(f"- Saldo (Pemasukan - Pengeluaran): Rp {saldo:,.0f}")

        # Rata-rata harian dan bulanan (pengeluaran)
        pengeluaran_df = df[df["Jenis"].str.lower() == "pengeluaran"].copy()
        pengeluaran_df["Hari"] = pengeluaran_df["Tanggal"].dt.date
        daily_avg = pengeluaran_df.groupby("Hari")["Jumlah"].sum().mean()
        monthly_sum = pengeluaran_df.groupby(df["Tanggal"].dt.to_period("M"))["Jumlah"].sum()
        monthly_avg = monthly_sum.mean()

        st.subheader("Rata-rata")
        st.write(f"- Rata-rata pengeluaran per hari: Rp {daily_avg:,.0f}")
        st.write(f"- Rata-rata pengeluaran per bulan: Rp {monthly_avg:,.0f}")

        # Distribusi per kategori
        if "Kategori" in df.columns:
            st.subheader("Distribusi per Kategori")
            cat_sum = pengeluaran_df.groupby("Kategori")["Jumlah"].sum().sort_values(ascending=False)
            st.dataframe(cat_sum)
            # Bar chart
            fig_cat, ax_cat = plt.subplots()
            ax_cat.bar(cat_sum.index.astype(str), cat_sum.values)
            ax_cat.set_title("Pengeluaran per Kategori")
            ax_cat.set_ylabel("Jumlah (Rp)")
            ax_cat.set_xticklabels(cat_sum.index.astype(str), rotation=45, ha="right")
            st.pyplot(fig_cat)

        # Tren bulanan (line)
        st.subheader("Tren Pengeluaran Bulanan")
        fig_line, ax_line = plt.subplots()
        ms = monthly_sum.sort_index()
        ax_line.plot([str(x) for x in ms.index.astype(str)], ms.values, marker="o")
        ax_line.set_title("Total Pengeluaran per Bulan")
        ax_line.set_xlabel("Bulan")
        ax_line.set_ylabel("Jumlah (Rp)")
        plt.xticks(rotation=45)
        st.pyplot(fig_line)

        # Pie chart distribusi bulanan (safe)
        st.subheader("Pie Chart Distribusi Bulanan")
        fig_pie, ax_pie = plt.subplots()
        ax_pie.pie(ms.values, labels=ms.index.astype(str), autopct="%1.1f%%", startangle=90)
        ax_pie.axis("equal")
        st.pyplot(fig_pie)

# ---------- 5. Download CSV ----------
elif menu == "Download CSV":
    st.header("💾 Download Data")
    if df.empty:
        st.info("Belum ada data untuk didownload.")
    else:
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV hasil", csv_bytes, "transactions_updated.csv", "text/csv")
