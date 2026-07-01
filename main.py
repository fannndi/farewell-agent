from storage import add_contact, get_all_contacts, search_contacts, delete_contact

def show_menu():
    print("\n=== MANAJEMEN KONTAK ===")
    print("1. Tambah Kontak")
    print("2. Lihat Semua Kontak")
    print("3. Cari Kontak")
    print("4. Hapus Kontak")
    print("5. Keluar")

def input_kontak():
    nama = input("Nama: ").strip()
    if not nama:
        raise ValueError("Nama tidak boleh kosong")
    telp = input("Telepon: ").strip()
    if not telp:
        raise ValueError("Telepon tidak boleh kosong")
    email = input("Email: ").strip()
    return nama, telp, email

def cmd_tambah():
    try:
        nama, telp, email = input_kontak()
        add_contact(nama, telp, email)
        print(f"Kontak '{nama}' berhasil ditambahkan")
    except ValueError as e:
        print(f"Error: {e}")

def cmd_lihat():
    kontak = get_all_contacts()
    if not kontak:
        print("Belum ada kontak.")
        return
    print(f"\nDaftar Kontak ({len(kontak)}):")
    print("-" * 40)
    for nama, info in sorted(kontak.items()):
        print(f"{nama:15s} | {info['telp']:15s} | {info['email']}")

def cmd_cari():
    q = input("Cari (nama/telp/email): ").strip().lower()
    if not q:
        print("Kata kunci tidak boleh kosong")
        return
    hasil = search_contacts(q)
    if not hasil:
        print(f"Tidak ditemukan kontak dengan '{q}'")
        return
    print(f"\nHasil pencarian ({len(hasil)}):")
    print("-" * 40)
    for nama, info in hasil:
        print(f"{nama:15s} | {info['telp']:15s} | {info['email']}")

def cmd_hapus():
    nama = input("Nama kontak yang akan dihapus: ").strip()
    if not nama:
        print("Nama tidak boleh kosong")
        return
    if delete_contact(nama):
        print(f"Kontak '{nama}' berhasil dihapus")
    else:
        print(f"Kontak '{nama}' tidak ditemukan")

def main():
    while True:
        show_menu()
        pilihan = input("Pilih menu (1-5): ").strip()
        if pilihan == "1":
            cmd_tambah()
        elif pilihan == "2":
            cmd_lihat()
        elif pilihan == "3":
            cmd_cari()
        elif pilihan == "4":
            cmd_hapus()
        elif pilihan == "5":
            print("Terima kasih!")
            break
        else:
            print("Pilihan tidak valid. Masukkan 1-5.")

if __name__ == "__main__":
    main()
