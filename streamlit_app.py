import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# -----------------------------
# FUNGSI MEMUAT DATA
# -----------------------------
def load_data(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    elif file.name.endswith(".xlsx"):
        df = pd.read_excel(file)
    else:
        st.error("Format file tidak didukung!")
        return None

    # Pastikan kolom wajib ada
    required_cols = ["Tanggal", "Kategori", "Jenis", "Jumlah"]
    if not all(c in df.columns for c in required_cols):
        st.error("Kolom wajib: Tanggal, Kategori, Jenis, Jumlah")
        return None

    # Konversi tanggal
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    return df

# -----------------------------
# FUNGSI TAMBAH TRANSAKSI
# -----------------------------
def add_transaction(df, tanggal, kategori, jenis, jumlah):
    new_row = {
        "Tanggal": tanggal,
        "Kategori": kategori,
        "Jenis": jenis,
        "Jumlah": jumlah
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    return df

# -----------------------------
# FUNGSI HAPUS TRANSAKSI
# -----------------------------
def delete_transaction(df, index):
    df = df.drop(index).reset_index(drop=True)
    return df

# -----------------------------
# TITLE
# -----------------------------
st.title("📊 Aplikasi Pengelola Keuangan Mahasiswa")
st.write("Kelola pemasukan & pengeluaran menggunakan CSV/Excel sebagai database.")

# -----------------------------
# UPLOAD FILE
# -----------------------------
uploaded = st.file_uploader("Unggah file CSV atau Excel", type=["csv", "xlsx"])

if uploaded:
    df = load_data(uploaded)
    if df is not None:

        st.success("File berhasil dimuat!")

        menu = st.sidebar.radio(
            "Menu",
            ["📄 Lihat Data", "➕ Tambah Transaksi", "❌ Hapus Transaksi", "📈 Analisis", "💾 Download Data"]
        )

        # --------------------------------------
        # 1. LIHAT DATA
        # --------------------------------------
        if menu == "📄 Lihat Data":
            st.subheader("📄 Tabel Transaksi")
            st.dataframe(df)

        # --------------------------------------
        # 2. TAMBAH TRANSAKSI
        # --------------------------------------
        elif menu == "➕ Tambah Transaksi":
            st.subheader("➕ Tambah Transaksi Baru")

            tanggal = st.date_input("Tanggal")
            kategori = st.text_input("Kategori (makan, kos, transport, dsb)")
            jenis = st.selectbox("Jenis Transaksi", ["Pengeluaran", "Pemasukan"])
            jumlah = st.number_input("Jumlah (Rp)", min_value=0)

            if st.button("Tambah"):
                df = add_transaction(df, tanggal, kategori, jenis, jumlah)
                st.success("Transaksi berhasil ditambahkan!")

                # Simpan otomatis ke session state
                st.session_state["df"] = df

        # --------------------------------------
        # 3. HAPUS TRANSAKSI
        # --------------------------------------
        elif menu == "❌ Hapus Transaksi":
            st.subheader("❌ Hapus Transaksi")

            st.write("Pilih nomor baris yang ingin dihapus:")

            st.dataframe(df)

            idx = st.number_input("Nomor indeks baris", min_value=0, max_value=len(df)-1)

            if st.button("Hapus"):
                df = delete_transaction(df, idx)
                st.session_state["df"] = df
                st.success(f"Baris {idx} berhasil dihapus!")

        # --------------------------------------
        # 4. ANALISIS
        # --------------------------------------
        elif menu == "📈 Analisis":
            st.subheader("📈 Analisis Keuangan")

            pengeluaran = df[df["Jenis"] == "Pengeluaran"]["Jumlah"].sum()
            pemasukan = df[df["Jenis"] == "Pemasukan"]["Jumlah"].sum()
            selisih = pemasukan - pengeluaran

            rata_harian = df[df["Jenis"] == "Pengeluaran"]["Jumlah"].mean()
            rata_bulanan = df.groupby(df["Tanggal"].dt.to_period("M"))["Jumlah"].sum().mean()

            st.markdown("### 🔎 Ringkasan")
            st.write(f"**Total Pengeluaran:** Rp{pengeluaran:,.0f}")
            st.write(f"**Total Pemasukan:** Rp{pemasukan:,.0f}")
            st.write(f"**Selisih:** Rp{selisih:,.0f}")
            st.write(f"**Rata-rata Pengeluaran Harian:** Rp{rata_harian:,.0f}")
            st.write(f"**Rata-rata Pengeluaran Bulanan:** Rp{rata_bulanan:,.0f}")

            st.markdown("---")

            # ------- Distribusi kategori -------
            st.markdown("### 📌 Distribusi Pengeluaran per Kategori")
            cat = df[df["Jenis"] == "Pengeluaran"].groupby("Kategori")["Jumlah"].sum()

            fig1, ax1 = plt.subplots()
            ax1.pie(cat, labels=cat.index, autopct="%1.1f%%")
            plt.title("Distribusi Kategori")
            st.pyplot(fig1)

            # ------- Grafik Tren -------
            st.markdown("### 📈 Tren Pengeluaran per Hari")
            daily = df[df["Jenis"] == "Pengeluaran"].groupby("Tanggal")["Jumlah"].sum()

            fig2, ax2 = plt.subplots()
            ax2.plot(daily.index, daily.values)
            ax2.set_title("Tren Pengeluaran")
            ax2.set_xlabel("Tanggal")
            ax2.set_ylabel("Jumlah (Rp)")
            st.pyplot(fig2)

        # --------------------------------------
        # 5. DOWNLOAD DATA
        # --------------------------------------
        elif menu == "💾 Download Data":
            st.subheader("💾 Download Data Terkini")

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv, "updated_transactions.csv")

else:
    st.info("Unggah file CSV atau Excel untuk mulai menggunakan aplikasi.")
