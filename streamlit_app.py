import pandas as pd
import numpy as np
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

# Save the dummy DataFrame to a CSV file
df_dummy.to_csv('transaksi_keuangan.csv', index=False)
print("Dummy 'transaksi_keuangan.csv' created successfully.")

# Memuat data transaksi keuangan dari file CSV
try:
    df_keuangan = pd.read_csv('transaksi_keuangan.csv')
    print("\nData loaded successfully. First 5 rows:")
    print(df_keuangan.head())
    print("\nDataFrame Info:")
    df_keuangan.info()
except FileNotFoundError:
    print("Error: 'transaksi_keuangan.csv' not found. Please ensure the file is in the correct directory.")

df_keuangan['Tanggal'] = pd.to_datetime(df_keuangan['Tanggal'])
print("Data types after converting 'Tanggal' column:")
df_keuangan.info()

df_keuangan['Pemasukan'] = np.where(df_keuangan['Jenis'] == 'Pemasukan', df_keuangan['Jumlah'], 0)
print("Kolom 'Pemasukan' berhasil dibuat.")

df_keuangan['Pengeluaran'] = np.where(df_keuangan['Jenis'] == 'Pengeluaran', df_keuangan['Jumlah'], 0)
print("Kolom 'Pengeluaran' berhasil dibuat.")

print("Lima baris pertama df_keuangan dengan kolom 'Pemasukan' dan 'Pengeluaran':")
print(df_keuangan.head())

df_keuangan['Bulan_Tahun'] = df_keuangan['Tanggal'].dt.to_period('M')
print("Kolom 'Bulan_Tahun' berhasil dibuat.")
print(df_keuangan.head())

monthly_summary = df_keuangan.groupby('Bulan_Tahun').agg(
    Pemasukan=('Pemasukan', 'sum'),
    Pengeluaran=('Pengeluaran', 'sum')
).reset_index()
print("Summary of monthly income and expenses created.")

monthly_summary['Arus_Kas_Bersih'] = monthly_summary['Pemasukan'] - monthly_summary['Pengeluaran']
print("Kolom 'Arus_Kas_Bersih' berhasil dibuat.")

print("Lima baris pertama dari ringkasan bulanan:")
print(monthly_summary.head())

rata_rata_pemasukan = monthly_summary['Pemasukan'].mean()
print(f"Rata-rata Pemasukan Bulanan: {rata_rata_pemasukan:,.2f}")

rata_rata_pengeluaran = monthly_summary['Pengeluaran'].mean()
print(f"Rata-rata Pengeluaran Bulanan: {rata_rata_pengeluaran:,.2f}")

rata_rata_arus_kas_bersih = monthly_summary['Arus_Kas_Bersih'].mean()
print(f"Rata-rata Arus Kas Bersih Bulanan: {rata_rata_arus_kas_bersih:,.2f}")

plt.figure(figsize=(12, 6))
plt.plot(monthly_summary['Bulan_Tahun'].astype(str), monthly_summary['Pemasukan'], label='Pemasukan', marker='o')
plt.plot(monthly_summary['Bulan_Tahun'].astype(str), monthly_summary['Pengeluaran'], label='Pengeluaran', marker='o')
plt.plot(monthly_summary['Bulan_Tahun'].astype(str), monthly_summary['Arus_Kas_Bersih'], label='Arus Kas Bersih', marker='o')

plt.title('Tren Keuangan Bulanan')
plt.xlabel('Bulan dan Tahun')
plt.ylabel('Jumlah (IDR)')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
```
