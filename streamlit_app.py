import streamlit as st
import pandas as pd
import os

st.title("Aplikasi Manajemen & Visualisasi Pengeluaran")

st.write("""
Aplikasi ini memungkinkan Anda mengelola data pengeluaran/pemasukan,
menghapus data yang salah, serta menampilkan visualisasi pengeluaran bulanan.
""")

# ---------------------------------------------------------
# Upload File
# ---------------------------------------------------------
st.header("1. Upload Data Pengeluaran (CSV)")
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("Data Awal")
    st.dataframe(df)

    # Cek kolom wajib
    required_cols = ["tanggal", "jumlah"]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"File harus memiliki kolom '{col}'")
            st.stop()

    # Convert tanggal
    df["tanggal"] = pd.to_datetime(df["tanggal"])

    # ---------------------------------------------------------
    # FITUR HAPUS DATA
    # ---------------------------------------------------------
    st.header("2. Kelola Data – Hapus Data yang Salah")

    opsi_hapus = st.selectbox(
        "Pilih cara menghapus data:",
        ["Pilih", "Hapus berdasarkan index", "Hapus berdasarkan tanggal", "Hapus berdasarkan kategori (jika ada)"]
    )

    if opsi_hapus == "Hapus berdasarkan index":
        st.write("Index data:")
        st.dataframe(df.reset_index())

        index_hapus = st.number_input("Masukkan index yang ingin dihapus:", min_value=0, max_value=len(df)-1, step=1)
        if st.button("Hapus"):
            df = df.drop(df.index[index_hapus]).reset_index(drop=True)
            st.success(f"Data index {index_hapus} berhasil dihapus!")
            st.dataframe(df)

    elif opsi_hapus == "Hapus berdasarkan tanggal":
        unique_dates = df["tanggal"].dt.date.unique()
        date_pick = st.selectbox("Pilih tanggal yang ingin dihapus:", unique_dates)

        if st.button("Hapus tanggal"):
            df = df[df["tanggal"].dt.date != date_pick].reset_index(drop=True)
            st.success(f"Data tanggal {date_pick} berhasil dihapus!")
            st.dataframe(df)

    elif opsi_hapus == "Hapus berdasarkan kategori (jika ada)":
        if "kategori" not in df.columns:
            st.error("Kolom 'kategori' tidak ditemukan.")
        else:
            unique_cat = df["kategori"].unique()
            cat_pick = st.selectbox("Pilih kategori yang ingin dihapus:", unique_cat)

            if st.button("Hapus kategori"):
                df = df[df["kategori"] != cat_pick].reset_index(drop=True)
                st.success(f"Kategori '{cat_pick}' berhasil dihapus!")
                st.dataframe(df)

    # ---------------------------------------------------------
    # ANALISIS & VISUALISASI
    # ---------------------------------------------------------
    st.header("3. Analisis Pengeluaran Bulanan")

    df["bulan"] = df["tanggal"].dt.strftime("%Y-%m")
    monthly_expense = df.groupby("bulan")["jumlah"].sum()

    st.subheader("Total Pengeluaran per Bulan")
    st.dataframe(monthly_expense)

    # Rata-rata bulanan
    rata_rata = monthly_expense.mean()
    st.info(f"📌 **Rata-rata pengeluaran per bulan: Rp {rata_rata:,.0f}**")

    # Pie chart
    st.subheader("Distribusi Pengeluaran per Bulan (Pie Chart)")
    fig, ax = plt.subplots()
    ax.pie(
        monthly_expense.values,
        labels=monthly_expense.index,
        autopct="%1.1f%%",
        startangle=90
    )
    ax.set_title("Pie Chart Pengeluaran Bulanan")
    st.pyplot(fig)

else:
    st.info("Unggah file CSV untuk mulai.")

