import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("📊 Aplikasi Manajemen & Analisis Keuangan Harian/Mingguan/Bulanan")

st.write("""
Aplikasi ini digunakan untuk mengelola, mengedit, dan menganalisis pengeluaran.
Anda bisa upload file CSV/Excel, menambah transaksi baru, menghapus data, dan melihat analisis keuangan.
""")

# ============================================
# 1. UPLOAD FILE
# ============================================
st.header("1️⃣ Upload Data (CSV / Excel)")

file = st.file_uploader("Upload file CSV/Excel", type=["csv", "xlsx"])

if file:

    # Membaca file
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    # Tampilkan data awal
    st.subheader("📄 Data Anda")
    st.dataframe(df)

    # Validasi kolom wajib
    required_columns = ["tanggal", "jumlah"]
    for col in required_columns:
        if col not in df.columns:
            st.error(f"❌ File harus memiliki kolom '{col}'")
            st.stop()

    # Konversi format tanggal
    df["tanggal"] = pd.to_datetime(df["tanggal"])

    # ============================================
    # 2. MENU PENGELOLAAN DATA
    # ============================================
    st.header("2️⃣ Kelola Data")

    menu = st.selectbox(
        "Pilih opsi:",
        [
            "Pilih",
            "Tambah transaksi",
            "Hapus berdasarkan index",
            "Hapus berdasarkan tanggal",
            "Hapus berdasarkan kategori (jika ada)"
        ]
    )

    # ---------------- Tambah transaksi ----------------
    if menu == "Tambah transaksi":
        st.subheader("📌 Tambah Transaksi Baru")

        tgl = st.date_input("Tanggal")
        nominal = st.number_input("Jumlah (Rp)", min_value=0)

        # Opsional kategori
        kategori = ""
        if "kategori" in df.columns:
            kategori = st.text_input("Kategori (opsional)")

        if st.button("Tambah"):
            new_row = {
                "tanggal": pd.to_datetime(tgl),
                "jumlah": nominal
            }
            if "kategori" in df.columns:
                new_row["kategori"] = kategori

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            st.success("Transaksi berhasil ditambahkan!")
            st.dataframe(df)

    # ---------------- Hapus index ----------------
    if menu == "Hapus berdasarkan index":
        st.subheader("🗑 Hapus Berdasarkan Index")

        st.dataframe(df.reset_index())

        idx = st.number_input(
            "Masukkan index yang ingin dihapus:",
            min_value=0,
            max_value=len(df) - 1,
            step=1
        )

        if st.button("Hapus Index"):
            df = df.drop(df.index[int(idx)]).reset_index(drop=True)
            st.success(f"Index {idx} berhasil dihapus!")
            st.dataframe(df)

    # ---------------- Hapus tanggal ----------------
    if menu == "Hapus berdasarkan tanggal":
        st.subheader("🗑 Hapus Berdasarkan Tanggal")

        tanggal = st.selectbox(
            "Pilih tanggal:",
            df["tanggal"].dt.date.unique()
        )

        if st.button("Hapus Tanggal"):
            df = df[df["tanggal"].dt.date != tanggal].reset_index(drop=True)
            st.success(f"Tanggal {tanggal} berhasil dihapus!")
            st.dataframe(df)

    # ---------------- Hapus kategori ----------------
    if menu == "Hapus berdasarkan kategori (jika ada)":
        if "kategori" not in df.columns:
            st.error("Kolom 'kategori' tidak tersedia di data.")
        else:
            st.subheader("🗑 Hapus Berdasarkan Kategori")

            kategori = st.selectbox("Pilih kategori:", df["kategori"].unique())

            if st.button("Hapus Kategori"):
                df = df[df["kategori"] != kategori].reset_index(drop=True)
                st.success(f"Kategori '{kategori}' berhasil dihapus!")
                st.dataframe(df)

    # ============================================
    # 3. ANALISIS KEUANGAN TERPISAH
    # ============================================

    st.header("3️⃣ Analisis Keuangan")

    df["bulan"] = df["tanggal"].dt.strftime("%Y-%m")
    monthly = df.groupby("bulan")["jumlah"].sum()

    # --------------------- Analisis 1 ---------------------
    st.subheader("📌 1. Total Pengeluaran per Bulan")
    st.dataframe(monthly)

    # --------------------- Analisis 2 ---------------------
    st.subheader("📌 2. Rata-rata Pengeluaran per Bulan")
    avg = monthly.mean()
    st.info(f"💰 Rata-rata: **Rp {avg:,.0f}** per bulan")

    # --------------------- Analisis 3 ---------------------
    st.subheader("📈 3. Grafik Pengeluaran Bulanan (Line Plot)")
    fig1, ax1 = plt.subplots()
    ax1.plot(monthly.index, monthly.values, marker="o")
    ax1.set_title("Pengeluaran Bulanan")
    ax1.set_ylabel("Jumlah (Rp)")
    ax1.set_xticklabels(monthly.index, rotation=45)
    st.pyplot(fig1)

    # --------------------- Analisis 4 ---------------------
    st.subheader("📊 4. Analisis Pengeluaran Berdasarkan Kategori")
    if "kategori" in df.columns:
        kategori_sum = df.groupby("kategori")["jumlah"].sum()
        st.dataframe(kategori_sum)

        # Grafik batang
        fig2, ax2 = plt.subplots()
        ax2.bar(kategori_sum.index, kategori_sum.values)
        ax2.set_title("Pengeluaran per Kategori")
        ax2.set_ylabel("Jumlah (Rp)")
        ax2.set_xticklabels(kategori_sum.index, rotation=45)
        st.pyplot(fig2)
    else:
        st.info("Kolom 'kategori' tidak ditemukan — bagian ini dilewati.")

    # --------------------- Analisis 5 ---------------------
    st.subheader("🥧 5. Pie Chart Distribusi Pengeluaran Bulanan")
    fig3, ax3 = plt.subplots()
    ax3.pie(
        monthly.values,
        labels=monthly.index,
        autopct="%1.1f%%",
        startangle=90
    )
    ax3.set_title("Distribusi Pengeluaran Bulanan")
    st.pyplot(fig3)

else:
    st.info("Silakan upload file CSV/Excel untuk mulai analisis.")
