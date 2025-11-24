import pandas as pd
import os

# --- 1. Inisialisasi: Pengaturan Awal ---
CSV_FILE = 'transactions.csv' # Changed from expenses.csv to transactions.csv

def load_transactions(): # Renamed from load_expenses
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE, parse_dates=['Tanggal'])

        # Ensure correct dtypes if loaded from CSV
        df['Jumlah'] = pd.to_numeric(df['Jumlah'], errors='coerce')
        df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')

        # If 'Type' column doesn't exist, assume all previous entries were 'Pengeluaran'
        # and make amounts negative. Then add the 'Type' column.
        if 'Kategori' in df.columns and 'Type' not in df.columns:
            print("Kolom 'Type' tidak ditemukan di CSV. Mengasumsikan semua entri yang ada adalah 'Pengeluaran'.")
            df['Type'] = 'Pengeluaran'
            df['Jumlah'] = df['Jumlah'].abs() * -1 # Make amounts negative for expenses
        elif 'Type' not in df.columns:
            df['Type'] = 'Pengeluaran' # Default to Pengeluaran if no Kategori either

        # Ensure 'Type' column is string
        df['Type'] = df['Type'].astype(str)

    else:
        df = pd.DataFrame(columns=['Tanggal', 'Deskripsi', 'Jumlah', 'Kategori', 'Type'])
        # Explicitly set dtypes for the empty DataFrame to avoid FutureWarning
        df['Tanggal'] = df['Tanggal'].astype('datetime64[ns]')
        df['Jumlah'] = df['Jumlah'].astype('float64')
        df['Type'] = df['Type'].astype(str)
    return df

def save_transactions(df): # Renamed from save_expenses
    df.to_csv(CSV_FILE, index=False)

# --- 2. Fungsi Tambah Transaksi ---
def add_transaction(df, date, description, amount, category, transaction_type): # Renamed from add_expense, added transaction_type
    try:
        # Convert date string to datetime object
        date = pd.to_datetime(date)
        # Convert amount to float
        amount = float(amount)
    except ValueError:
        print("Error: Format tanggal atau jumlah tidak valid.")
        return df

    # Adjust amount based on transaction type
    if transaction_type == 'Pengeluaran':
        amount = -abs(amount) # Ensure amount is negative for expenses
    elif transaction_type == 'Pemasukan':
        amount = abs(amount)  # Ensure amount is positive for income
    else:
        print("Error: Tipe transaksi tidak valid. Gunakan 'Pengeluaran' atau 'Pemasukan'.")
        return df

    new_transaction = pd.DataFrame([{'Tanggal': date, 'Deskripsi': description, 'Jumlah': amount, 'Kategori': category, 'Type': transaction_type}])
    df = pd.concat([df, new_transaction], ignore_index=True)
    save_transactions(df) # Renamed from save_expenses
    print(f"{transaction_type} '{description}' sejumlah Rp{abs(amount):,.2f} berhasil ditambahkan.") # Adjusted message
    return df

# --- 3. Fungsi Lihat Transaksi ---
def view_transactions(df): # Renamed from view_expenses
    if df.empty:
        print("Belum ada transaksi yang tercatat.")
    else:
        print("Daftar Transaksi:")
        # Using .to_string() for console display
        print(df.sort_values(by='Tanggal', ascending=False).to_string(index=False))

# --- 4. Fungsi Ringkasan Transaksi ---
def summarize_transactions(df): # Renamed from summarize_expenses
    if df.empty:
        print("Belum ada transaksi yang tercatat untuk diringkas.")
        return

    print("\n--- Ringkasan Transaksi ---")
    # Calculate total balance (sum of all amounts)
    total_balance = df['Jumlah'].sum()
    total_income = df[df['Type'] == 'Pemasukan']['Jumlah'].sum()
    total_expenses = df[df['Type'] == 'Pengeluaran']['Jumlah'].sum() * -1 # Display expenses as positive for summary

    print(f"Total Pemasukan: Rp{total_income:,.2f}")
    print(f"Total Pengeluaran: Rp{total_expenses:,.2f}")
    print(f"Saldo Akhir: Rp{total_balance:,.2f}")

    print("\nRingkasan Pengeluaran Berdasarkan Kategori:")
    expense_summary = df[df['Type'] == 'Pengeluaran'].groupby('Kategori')['Jumlah'].sum().abs().sort_values(ascending=False)
    if not expense_summary.empty:
        # Using .to_string() for console display
        print(expense_summary.to_frame().to_string())
    else:
        print("Tidak ada pengeluaran yang dikategorikan.")
    print("----------------------------")

# --- 5. Antarmuka Pengguna (Menu Utama) ---
def main_menu():
    global transactions_df # Renamed from expenses_df
    while True:
        print("\n--- Aplikasi Pelacak Keuangan ---") # Changed application name
        print("1. Tambah Pengeluaran")
        print("2. Tambah Pemasukan")
        print("3. Lihat Transaksi")
        print("4. Ringkas Transaksi")
        print("5. Keluar")
        choice = input("Pilih opsi: ")

        if choice == '1':
            date = input("Masukkan tanggal (YYYY-MM-DD): ")
            description = input("Masukkan deskripsi: ")
            amount = input("Masukkan jumlah: ")
            category = input("Masukkan kategori: ")
            transactions_df = add_transaction(transactions_df, date, description, amount, category, 'Pengeluaran')
        elif choice == '2':
            date = input("Masukkan tanggal (YYYY-MM-DD): ")
            description = input("Masukkan deskripsi: ")
            amount = input("Masukkan jumlah: ")
            category = input("Masukkan kategori: ") # Income can also have categories
            transactions_df = add_transaction(transactions_df, date, description, amount, category, 'Pemasukan')
        elif choice == '3':
            view_transactions(transactions_df)
        elif choice == '4':
            summarize_transactions(transactions_df)
        elif choice == '5':
            print("Terima kasih telah menggunakan aplikasi pelacak keuangan.")
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

# --- Jalankan Aplikasi ---
# Muat data transaksi saat aplikasi dimulai
transactions_df = load_transactions() # Renamed from expenses_df, load_expenses

# Jalankan menu utama
main_menu()
