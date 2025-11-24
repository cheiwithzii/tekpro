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

    # Try import chardet but don't fail if not installed
    try:
        import chardet
        _HAS_CHARDET = True
    except Exception:
        _HAS_CHARDET = False

    uploaded = st.file_uploader("Pilih file CSV", type="csv")

    if uploaded is not None:
        # Read raw bytes once
        try:
            uploaded_bytes = uploaded.read()
        except Exception as e:
            st.error("Gagal membaca file upload (I/O). Coba ulangi.")
            st.code(str(e))
            uploaded.seek(0)
            continue  # move on; in some envs 'continue' inside streamlit is fine as flow control

        # --- 1) DETEKSI ENCODING (dengan fallback) ---
        encoding = None
        if _HAS_CHARDET:
            try:
                det = chardet.detect(uploaded_bytes)
                encoding = det.get("encoding")
            except Exception:
                encoding = None

        # If chardet not available or returned None, try common encodings
        if not encoding:
            for enc_try in ("utf-8", "utf-8-sig", "utf-16", "latin1", "cp1252"):
                try:
                    uploaded_bytes.decode(enc_try)
                    encoding = enc_try
                    break
                except Exception:
                    continue

        if not encoding:
            # last resort
            encoding = "utf-8"

        # Prepare text for sniffing/reading
        try:
            text = uploaded_bytes.decode(encoding, errors="replace")
        except Exception as e:
            st.error("Gagal meng-decode file. Encoding terdeteksi tidak cocok.")
            st.code(str(e))
            uploaded.seek(0)
            continue

        # --- 2) DETEKSI DELIMITER (sniffer safe) ---
        delimiter = ","
        try:
            sample = text[:4096]  # don't pass giant text to sniffer
            # Sniffer can raise Error, so protect it
            dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";", "|", "\t"])
            delimiter = dialect.delimiter
            # If sniffer thinks it's headerless, ensure has header:
            has_header = csv.Sniffer().has_header(sample)
        except Exception:
            # Fallback heuristics: count common delimiters in sample
            counts = {",": sample.count(","), ";": sample.count(";"), "|": sample.count("|"), "\t": sample.count("\t")}
            delimiter = max(counts, key=counts.get)
            if counts[delimiter] == 0:
                delimiter = ","  # ultimate fallback

        # --- 3) BACA DENGAN PANDAS via StringIO (lebih stabil) ---
        try:
            str_io = io.StringIO(text)
            new_df = pd.read_csv(str_io, sep=delimiter, engine="python")
        except Exception as e:
            st.error("❌ Gagal membaca CSV dengan pandas. Berikut detail teknis:")
            st.code(str(e))
            st.info(f"Deteksi encoding: {encoding} | Delimiter: '{delimiter}'")
            uploaded.seek(0)
            continue

        # --- 4) NORMALISASI NAMA KOLOM: trim spasi & samakan kapitalisasi sederhana ---
        new_df.columns = [col.strip() for col in new_df.columns]

        # optional: try to map common alternative names to required ones
        col_map = {}
        cols_lower = {c.lower(): c for c in new_df.columns}
        # common alternatives
        if "tanggal" in cols_lower and "Tanggal" not in new_df.columns:
            col_map[cols_lower["tanggal"]] = "Tanggal"
        if "deskripsi" in cols_lower and "Deskripsi" not in new_df.columns:
            col_map[cols_lower["deskripsi"]] = "Deskripsi"
        if "jumlah" in cols_lower and "Jumlah" not in new_df.columns:
            col_map[cols_lower["jumlah"]] = "Jumlah"
        if "kategori" in cols_lower and "Kategori" not in new_df.columns:
            col_map[cols_lower["kategori"]] = "Kategori"
        # handle common local variations
        if "type" not in new_df.columns:
            for alt in ("tipe", "jenis", "type"):
                if alt in cols_lower and "Type" not in new_df.columns:
                    col_map[cols_lower[alt]] = "Type"
        if col_map:
            new_df = new_df.rename(columns=col_map)

        # --- 5) CEK KOLOM REQUIRED ---
        required_cols = ["Tanggal", "Deskripsi", "Jumlah", "Kategori", "Type"]
        missing = [c for c in required_cols if c not in new_df.columns]
        if missing:
            st.error(f"❌ Format CSV tidak sesuai. Kolom yang hilang: {missing}")
            st.info(f"Kolom terdeteksi: {list(new_df.columns)}")
            st.warning("Saya bisa mencoba otomatis memperbaiki jika Anda ingin (mis. map 'tipe'->'Type').")
            continue

        # --- 6) KONVERSI TIPE DATA DENGAN PERBAIKAN ---
        new_df["Tanggal"] = pd.to_datetime(new_df["Tanggal"].astype(str).str.strip(), dayfirst=True, errors="coerce")
        # If many NaT, try alternative parse
        if new_df["Tanggal"].isna().sum() > 0:
            # Try parsing with infer_datetime_format True as fallback
            try:
                new_df["Tanggal"] = pd.to_datetime(new_df["Tanggal"].astype(str).str.strip(), infer_datetime_format=True, errors="coerce")
            except Exception:
                pass

        # Bersihkan kolom Jumlah dari tanda non-digit (Rp, ., ,) lalu numeric
        new_df["Jumlah"] = new_df["Jumlah"].astype(str).str.replace(r"[^\d\-]", "", regex=True)
        new_df["Jumlah"] = pd.to_numeric(new_df["Jumlah"], errors="coerce")

        # Jika ada baris dengan NaN di 'Tanggal' atau 'Jumlah', tunjukkan preview dan minta konfirmasi
        bad_rows = new_df[new_df[["Tanggal", "Jumlah"]].isna().any(axis=1)]
        if not bad_rows.empty:
            st.warning("Beberapa baris memiliki Tanggal atau Jumlah yang tidak valid. Tampilkan preview sebelum menyimpan:")
            st.dataframe(bad_rows)
            if st.button("Simpan tetap (abaikan baris invalid)"):
                # drop invalid rows then save
                good = new_df.dropna(subset=["Tanggal", "Jumlah"])
                old_df = load_transactions()
                combined_df = pd.concat([old_df, good], ignore_index=True)
                save_transactions(combined_df)
                st.success("CSV digabungkan (baris invalid diabaikan).")
            else:
                st.info("Periksa dan perbaiki file CSV Anda, atau klik tombol 'Simpan tetap' untuk menyimpan baris valid saja.")
            continue

        # --- 7) Gabungkan dan Simpan ---
        try:
            old_df = load_transactions()
            combined_df = pd.concat([old_df, new_df], ignore_index=True)
            save_transactions(combined_df)
            st.success("✅ CSV berhasil diupload & digabungkan ke database!")
            st.info(f"Encoding terdeteksi: **{encoding}** | Delimiter: **'{delimiter}'**")
            st.dataframe(new_df)
        except Exception as e:
            st.error("Gagal menggabungkan dan menyimpan data ke database.")
            st.code(str(e))

        # reset file pointer (just in case)
        uploaded.seek(0)


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
