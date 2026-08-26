"""
Generuje plik danych o lokalnym asortymencie dla Google Merchant Center
na podstawie istniejącego feedu produktowego sklepasg.pl (Shoper).

Wynik: local_inventory.txt (TSV, kolumny: id, store_code, quantity, availability, price)
"""

import requests
import xml.etree.ElementTree as ET

# --- Konfiguracja ---
FEED_URL = "https://sklep305688.shoparena.pl/console/integration/execute/name/GoogleProductSearch"
STORE_CODE = "11072484000919481729"  # kod sklepu z Profilu Firmy (Ustawienia zaawansowane)
OUTPUT_FILE = "local_inventory.txt"

# Placeholder ilości, gdy nie mamy dokładnego stanu magazynowego z feedu.
QUANTITY_IN_STOCK = 999
QUANTITY_OUT_OF_STOCK = 0

NS = {"g": "http://base.google.com/ns/1.0"}
ATOM_ENTRY = "{http://www.w3.org/2005/Atom}entry"


def fetch_feed(url: str) -> bytes:
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.content


def parse_and_transform(xml_bytes: bytes) -> list[list[str]]:
    root = ET.fromstring(xml_bytes)
    rows = []

    for entry in root.iter(ATOM_ENTRY):
        product_id_el = entry.find("g:id", NS)
        availability_el = entry.find("g:availability", NS)
        price_el = entry.find("g:price", NS)

        if product_id_el is None or availability_el is None:
            continue

        product_id = product_id_el.text.strip()
        availability = availability_el.text.strip()
        price = price_el.text.strip() if price_el is not None else ""

        quantity = QUANTITY_IN_STOCK if availability == "in stock" else QUANTITY_OUT_OF_STOCK

        rows.append([product_id, STORE_CODE, str(quantity), availability, price])

    return rows


def write_tsv(rows: list[list[str]], path: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("id\tstore_code\tquantity\tavailability\tprice\n")
        for row in rows:
            f.write("\t".join(row) + "\n")


def main() -> None:
    xml_bytes = fetch_feed(FEED_URL)
    rows = parse_and_transform(xml_bytes)
    write_tsv(rows, OUTPUT_FILE)
    print(f"Zapisano {len(rows)} produktów do {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
