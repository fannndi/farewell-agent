_kontak: dict = {}

def add_contact(nama: str, telp: str, email: str) -> None:
    if nama in _kontak:
        raise ValueError(f"Kontak '{nama}' sudah ada")
    _kontak[nama] = {"telp": telp, "email": email}

def get_all_contacts() -> dict:
    return dict(_kontak)

def search_contacts(query: str) -> list:
    q = query.lower()
    hasil = []
    for nama, info in _kontak.items():
        if q in nama.lower() or q in info["telp"] or q in info["email"].lower():
            hasil.append((nama, info))
    return hasil

def delete_contact(nama: str) -> bool:
    if nama in _kontak:
        del _kontak[nama]
        return True
    return False
