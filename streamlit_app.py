import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # use non-interactive backend for headless servers
import matplotlib.pyplot as plt

# Create dummy data for 'transaksi_keuangan.csv'
data = {
    'Tanggal': pd.to_datetime(['2023-01-01', '2023-01-05', '2023-01-10', '2023-01-15', '2023-01-20', '2023-02-01', '2023-02-07', '2023-02-14', '2023-02-20', '2023-03-01']),
    'Deskripsi': [
        'Gaji Januari',
        'Belanja Bulanan',
        'Tagihan Listrik',
        'Penjualan Produk A',
        'Makan Malam',
        'Gaji Februari',
        'Sewa Apartemen',
        'Penjualan Produk B',
        'Transportasi',
        'Gaji Maret'
    ],
    'Jumlah': [
        5000000, 1500000, 300000, 2000000, 250000,
        5000000, 2000000, 1500000, 100000, 5000000
    ],
    'Jenis': [
        'Pemasukan', 'Pengeluaran', 'Pengeluaran', 'Pemasukan', 'Pengeluaran',
        'Pemasukan', 'Pengeluaran', 'Pemasukan', 'Pengeluaran', 'Pemasukan'
    ]
}
df_dummy = pd.DataFrame(data)

# Save the dummy DataFrame to a CSV file (if needed)
df_dummy.to_csv('transaksi_keuangan.csv', index=False)

st.write("Dummy 'transaksi_keuangan.csv' created (or overwritten) in app directory.")

# Memuat data transaksi keuangan dari file CSV
try:
    df_keuangan = pd.read_csv('transaksi_keuangan.csv')
    st.write("Data loaded successfully. First 5 rows:")
    st.dataframe(df_keuangan.head())
except FileNotFoundError:
    st.error("Error: 'transaksi_keuangan.csv' not found. Please ensure the file is in the correct directory.")
    st.stop()

# Pastikan tipe tanggal
df_keuangan['Tanggal'] = pd.to_datetime(df_keuangan['Tanggal'])

# Buat kolom Pemasukan dan Pengeluaran
df_keuangan['Pemasukan'] = np.where(df_keuangan['Jenis'] == 'Pemasukan', df_keuangan['Jumlah'], 0)
df_keuangan['Pengeluaran'] = np.where(df_keuangan['Jenis'] == 'Pengeluaran', df_keuangan['Jumlah'], 0)

st.write("Kolom 'Pemasukan' dan 'Pengeluaran' telah dibuat.")

# Buat kolom Bulan_Tahun untuk agregasi bulanan
df_keuangan['Bulan_Tahun'] = df_keuangan['Tanggal'].dt.to_period('M')

monthly_summary = df_keuangan.groupby('Bulan_Tahun').agg(
    Pemasukan=('Pemasukan', 'sum'),
    Pengeluaran=('Pengeluaran', 'sum')
).reset_index()

monthly_summary['Arus_Kas_Bersih'] = monthly_summary['Pemasukan'] - monthly_summary['Pengeluaran']

st.write("Ringkasan bulanan:")
st.dataframe(monthly_summary)

rata_rata_pemasukan = monthly_summary['Pemasukan'].mean()
rata_rata_pengeluaran = monthly_summary['Pengeluaran'].mean()
rata_rata_arus_kas_bersih = monthly_summary['Arus_Kas_Bersih'].mean()

st.write(f"Rata-rata Pemasukan Bulanan: {rata_rata_pemasukan:,.2f}")
st.write(f"Rata-rata Pengeluaran Bulanan: {rata_rata_pengeluaran:,.2f}")
st.write(f"Rata-rata Arus Kas Bersih Bulanan: {rata_rata_arus_kas_bersih:,.2f}")

# Plotting using a Figure and show via Streamlit
fig, ax = plt.subplots(figsize=(12, 6))
x = monthly_summary['Bulan_Tahun'].astype(str)
ax.plot(x, monthly_summary['Pemasukan'], label='Pemasukan', marker='o')
ax.plot(x, monthly_summary['Pengeluaran'], label='Pengeluaran', marker='o')
ax.plot(x, monthly_summary['Arus_Kas_Bersih'], label='Arus Kas Bersih', marker='o')

ax.set_title('Tren Keuangan Bulanan')
ax.set_xlabel('Bulan dan Tahun')
ax.set_ylabel('Jumlah (IDR)')
ax.legend()
ax.grid(True)
plt.xticks(rotation=45, ha='right')
fig.tight_layout()

st.pyplot(fig)
