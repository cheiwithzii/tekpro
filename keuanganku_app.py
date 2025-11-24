import streamlit as st
import pandas as pd
import datetime as dt

# ====================================================
#     HEADER PROFESIONAL APLIKASI "KEUANGANKU"
# ====================================================

st.title("📊 Keuanganku – Sistem Manajemen Keuangan Pribadi")

st.subheader("""
Platform profesional untuk membantu Anda memantau arus kas harian, 
mengelola pengeluaran, dan mengevaluasi kondisi finansial secara komprehensif.
""")

st.markdown("""
Selamat datang di **Keuanganku**, aplikasi yang dirancang untuk memberikan 
wawasan finansial yang akurat, transparan, dan terstruktur.  
Gunakan fitur-fitur yang tersedia untuk mengunggah data pengeluaran, 
menganalisis pola keuangan, serta mengoptimalkan pengelolaan budget Anda.
""")

st.write("---")

# ====================================================
#                INISIASI STATE DATA
# ====================================================

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["Tanggal", "Deskripsi", "Jumlah", "Kategori", "Tipe"])


# ====================================================
#                MENU INTERAKTIF BUTTON
# ====================================================

menu = st.segmented_control(
    "Navigasi",
    options=["📁 Upload CSV", "➕ Input Transaksi", "📝 Edit / Hapus Data", "📈 Statistik", "📃 Lihat Tabel"],
    default="📁 Upload CSV"
)


# ====================================================
#               1. UPLOAD FILE CSV
# ====================================================

if menu == "📁 Upload CSV":
    st.header("📁 Upload File CSV")

    uploaded = st.file_uploader("Unggah file CSV pengeluaran Anda", type=["csv"])

    if uploaded is not None:
        df_new = pd.read_csv(uploaded)

        # Normalisasi format tanggal jika perlu
        if "Tanggal" in df_new.columns:
            df_new["Tanggal"] = pd.to_datetime(df_new["Tanggal"], errors="coerce")

        st.session_state.df = df_new
        st.success("Data berhasil dimuat ke dalam sistem!")

        st.dataframe(df_new, use_container_width=True)


# ====================================================
#               2. INPUT TRANSAKSI BARU
# ====================================================

if menu == "➕ Input Transaksi":
    st.header("➕ Tambah Transaksi Baru")

    col1, col2 = st.columns(2)

    with col1:
        tgl = st.date_input("Tanggal", dt.date.today())
        deskripsi = st.text_input("Deskripsi")
        kategori = st.selectbox("Kategori", ["Makanan", "Transport", "Harian", "Hiburan", "Tagihan", "Lainnya"])

    with col2:
        jumlah = st.number_input("Jumlah (Rp)", step=1000, min_value=0)
        tipe = st.selectbox("Tipe Transaksi", ["Pengeluaran", "Pemasukan"])

    if st.button("Simpan Transaksi"):
        new_row = {
            "Tanggal": tgl,
            "Deskripsi": deskripsi,
            "Jumlah": jumlah if tipe == "Pemasukan" else -jumlah,
            "Kategori": kategori,
            "Tipe": tipe,
        }

        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
        st.success("Transaksi berhasil ditambahkan!")


# ====================================================
#              3. EDIT / HAPUS DATA
# ====================================================

if menu == "📝 Edit / Hapus Data":
    st.header("📝 Edit atau Hapus Data")

    df = st.session_state.df.copy()

    if df.empty:
        st.info("Belum ada data untuk diedit.")
    else:
        st.dataframe(df, use_container_width=True)

        idx = st.number_input("Masukkan index baris yang akan diedit/dihapus:", min_value=0, max_value=len(df)-1)

        st.write("### Edit Kolom")
        col1, col2 = st.columns(2)

        with col1:
            new_desc = st.text_input("Deskripsi baru", df.loc[idx, "Deskripsi"])
            new_kat = st.text_input("Kategori baru", df.loc[idx, "Kategori"])

        with col2:
            new_tgl = st.date_input("Tanggal baru", df.loc[idx, "Tanggal"])
            new_jumlah = st.number_input("Jumlah baru (Rp)", value=float(abs(df.loc[idx, "Jumlah"])))
            new_tipe = st.selectbox("Tipe baru", ["Pengeluaran", "Pemasukan"])

        colA, colB = st.columns(2)
        with colA:
            if st.button("Update Data"):
                df.loc[idx, "Tanggal"] = new_tgl
                df.loc[idx, "Deskripsi"] = new_desc
                df.loc[idx, "Kategori"] = new_kat
                df.loc[idx, "Jumlah"] = new_jumlah if new_tipe == "Pemasukan" else -new_jumlah
                df.loc[idx, "Tipe"] = new_tipe

                st.session_state.df = df
                st.success("Data berhasil diperbarui!")

        with colB:
            if st.button("Hapus Data"):
                df = df.drop(idx).reset_index(drop=True)
                st.session_state.df = df
                st.warning("Data berhasil dihapus!")


# ====================================================
#              4. STATISTIK RINGKAS
# ====================================================

if menu == "📈 Statistik":
    st.header("📈 Statistik Finansial")

    df = st.session_state.df.copy()

    if df.empty:
        st.info("Belum ada data untuk dianalisis.")
    else:
        total_keluar = df[df["Jumlah"] < 0]["Jumlah"].sum()
        total_masuk = df[df["Jumlah"] > 0]["Jumlah"].sum()
        saldo = total_masuk + total_keluar

        st.metric("Total Pemasukan", f"Rp {total_masuk:,.0f}")
        st.metric("Total Pengeluaran", f"Rp {total_keluar:,.0f}")
        st.metric("Saldo Akhir", f"Rp {saldo:,.0f}")

        st.subheader("Pengeluaran per Kategori")
        st.bar_chart(df[df["Jumlah"] < 0].groupby("Kategori")["Jumlah"].sum().abs())


# ====================================================
#               5. TAMPILAN TABEL + DOWNLOAD
# ====================================================

if menu == "📃 Lihat Tabel":
    st.header("📃 Seluruh Data Transaksi")

    df = st.session_state.df.copy()

    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "💾 Download CSV",
        data=csv,
        file_name="keuanganku_database.csv",
        mime="text/csv"
    )
