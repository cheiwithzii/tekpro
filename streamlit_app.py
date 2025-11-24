import pandas as pd
import os

# --- 1. Inisialisasi: Pengaturan Awal ---
CSV_FILE = 'expenses.csv'

def load_expenses():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE, parse_dates=['Tanggal'])
        # Ensure correct dtypes if loaded from CSV
        df['Jumlah'] = pd.to_numeric(df['Jumlah'], errors='coerce')
        df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
    else:
        df = pd.DataFrame(columns=['Tanggal', 'Deskripsi', 'Jumlah', 'Kategori'])
        # Explicitly set dtypes for the empty DataFrame to avoid FutureWarning
        df['Tanggal'] = df['Tanggal'].astype('datetime64[ns]')
        df['Jumlah'] = df['Jumlah'].astype('float64')
    return df

def save_expenses(df):
    df.to_csv(CSV_FILE, index=False)

# --- 2. Fungsi Tambah Pengeluaran ---
def add_expense(df, date, description, amount, category):
    try:
        # Convert date string to datetime object
        date = pd.to_datetime(date)
        # Convert amount to float
        amount = float(amount)
    except ValueError:
        print("Error: Format tanggal atau jumlah tidak valid.")
        return df

    new_expense = pd.DataFrame([{'Tanggal': date, 'Deskripsi': description, 'Jumlah': amount, 'Kategori': category}])
    df = pd.concat([df, new_expense], ignore_index=True)
    save_expenses(df)
    print(f"Pengeluaran '{description}' sejumlah Rp{amount:,.2f} berhasil ditambahkan.")
    return df

# --- 3. Fungsi Lihat Pengeluaran ---
def view_expenses(df):
    if df.empty:
        print("Belum ada pengeluaran yang tercatat.")
    else:
        print("Daftar Pengeluaran:")
        # Using .to_string() for console display
        print(df.sort_values(by='Tanggal', ascending=False).to_string(index=False))

# --- 4. Fungsi Ringkasan Pengeluaran ---
def summarize_expenses(df):
    if df.empty:
        print("Belum ada pengeluaran yang tercatat untuk diringkas.")
        return

    print("\n--- Ringkasan Pengeluaran ---")
    total_expenses = df['Jumlah'].sum()
    print(f"Total Pengeluaran Keseluruhan: Rp{total_expenses:,.2f}")

    print("\nPengeluaran Berdasarkan Kategori:")
    category_summary = df.groupby('Kategori')['Jumlah'].sum().sort_values(ascending=False)
    if not category_summary.empty:
        # Using .to_string() for console display
        print(category_summary.to_frame().to_string())
    else:
        print("Tidak ada pengeluaran yang dikategorikan.")
    print("----------------------------")

# --- 5. Antarmuka Pengguna (Menu Utama) ---
def main_menu():
    global expenses_df
    while True:
        print("\n--- Aplikasi Pelacak Pengeluaran ---")
        print("1. Tambah Pengeluaran")
        print("2. Lihat Pengeluaran")
        print("3. Ringkas Pengeluaran")
        print("4. Keluar")
        choice = input("Pilih opsi: ")

        if choice == '1':
            date = input("Masukkan tanggal (YYYY-MM-DD): ")
            description = input("Masukkan deskripsi: ")
            amount = input("Masukkan jumlah: ")
            category = input("Masukkan kategori: ")
            expenses_df = add_expense(expenses_df, date, description, amount, category)
        elif choice == '2':
            view_expenses(expenses_df)
        elif choice == '3':
            summarize_expenses(expenses_df)
        elif choice == '4':
            print("Terima kasih telah menggunakan aplikasi pelacak pengeluaran.")
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

# --- Jalankan Aplikasi ---
# Muat data pengeluaran saat aplikasi dimulai
expenses_df = load_expenses()

# Jalankan menu utama
main_menu()
