from bs4 import BeautifulSoup
import re

with open("vietlott.html", "r") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("--- DRAW DATE & PERIOD ---")
h5s = soup.find_all('h5')
for idx, h in enumerate(h5s[:10]):
    print(f"H5-{idx}:", h.text.strip().replace('\n', ' ').replace('\r', ''))
    
print("\n--- WINNING NUMBERS ---")
number_divs = soup.select('.day_so_ket_qua_v2 span, .day-so-ket-qua-v2 span')
print([n.text.strip() for n in number_divs])

print("\n--- JACKPOT VALUE ---")
jackpot_els = soup.select('.gia-tri-nhat h5 b, .gia-tri-nhat h5, .gia-tri-giai')
for j in jackpot_els:
    print(j.text.strip())
