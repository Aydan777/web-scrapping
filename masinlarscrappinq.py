import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Veb-saytın URL-i
url = 'https://masinlar.az/masin-satisi'

# Əlaqə sorğuları üçün User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

print(f"Məlumatlar '{url}' ünvanından toplanır...")

# Səhifəyə GET sorğusu göndərmək
try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # HTTP xətalarını (4xx, 5xx) yoxla

    # HTML məzmununu parse etmək
    soup = BeautifulSoup(response.content, 'html.parser')

    # Məlumatları saxlamaq üçün boş siyahılar
    avtomobil_adlari = []
    qiymetler = []

    # Bütün elan bloklarını tapmaq
    # Həm VIP, həm də normal elanlar üçün uyğun sinifləri axtarırıq.
    # Bu elementləri özündə saxlayan ən ümumi sinifləri seçirik.
    # VIP elanlar: <div class="nobj prod vipebg">
    # Normal elanlar: <div class="nobj prod prodbig">
    # Hər ikisi "nobj" və "prod" siniflərinə sahibdir, bu səbəbdən biz onları bir yerdə axtara bilərik.
    elan_bloklari = soup.find_all('div', class_=lambda x: x and 'nobj' in x.split() and 'prod' in x.split() and ('vipebg' in x.split() or 'prodbig' in x.split()))

    if not elan_bloklari:
        print("Xəbərdarlıq: Səhifədə heç bir elan bloku (nobj prod vipebg və ya nobj prod prodbig sinifli) tapılmadı. Zəhmət olmasa, class adlarını bir daha yoxlayın.")
    else:
        for blok in elan_bloklari:
            # Avtomobil adını çıxarır (Marka, Model, İl)
            # Strukturu: <div class="prodname"><a href="..." title="..."><b>[Avtomobil Adı]</b>...</a></div>
            avto_ad = 'Ad Tapılmadı'
            prodname_div = blok.find('div', class_='prodname')
            if prodname_div:
                b_tag = prodname_div.find('b')
                if b_tag:
                    avto_ad = b_tag.get_text(strip=True)
            avtomobil_adlari.append(avto_ad)

            # Qiyməti çıxarır
            # Strukturu: <span class="sprice">[Qiymət]</span>
            qiymet_val = 'Qiymət Tapılmadı'
            sprice_span = blok.find('span', class_='sprice')
            if sprice_span:
                qiymet_text = sprice_span.get_text(strip=True)
                # Qiyməti təmizləmək (rəqəmləri, boşluqları və valyuta işarəsini almaq)
                matches = re.findall(r'(\d[\d\s.,]*)\s*([a-zA-Z\u20BC\u20BD\u0024\u00A3\u20AC\u20B4\u20B8\u20B9\u20AA\u20AB\u20B5\u20BA\u20BA\u20B3\u20B1\u20B6\u20B7\u20AE\u20B0\u20B2\u20A3\u20A4\u20A7\u20A0\u20A1\u20A6\u20A8\u20A9\u20AF\u20C0-\u20CF\u2100-\u214F\u2190-\u21FF\u2200-\u22FF\u2300-\u23FF\u2400-\u243F\u2440-\u245F\u2500-\u257F\u2580-\u259F\u25A0-\u25FF\u2600-\u26FF\u2700-\u27BF\u2B00-\u2BFF\u2E80-\u2FFF\u3000-\u303F\u3040-\u309F\u30A0-\u30FF\u3100-\u312F\u3130-\u318F\u3190-\u319F\u31A0-\u31BF\u31C0-\u31EF\u31F0-\u32FF\u31F0-\u32FF\u3300-\u33FF\u3400-\u4DBF\u4DC0-\u4DFF\u4E00-\u9FFF\uA000-\uA48F\uA490-\uA4CF\uA4D0-\uA4FF\uA500-\uA63F\uA640-\uA69F\uA6A0-\uA6FF\uA700-\uA71F\uA720-\uA7FF\uA800-\uA82F\uA830-\uA83F\uA840-\uA87F\uA880-\uA8BF\uA8C0-\uA8DF\uA8E0-\uA8FF\uA900-\uA92F\uA930-\uA95F\uA960-\uA97F\uA980-\uA9DF\uA9E0-\uA9FF\uAA00-\uAA3F\uAA40-\uAA6F\uAA70-\uAAAF\uAAB0-\uAADF\uAAE0-\uAAFF\uAB00-\uAB2F\uAB30-\uAB6F\uAB70-\uABBF\uABC0-\uABFF\uAC00-\uD7FF\uE000-\uF8FF\uF900-\uFAFF\uFB00-\uFB4F\uFB50-\uFDFF\uFE00-\uFE0F\uFE10-\uFE1F\uFE20-\uFE2F\uFE30-\uFE4F\uFE50-\uFE6F\uFE70-\uFEFF\uFF00-\uFFEF\uFFF0-\uFFFF]*)', qiymet_text, re.IGNORECASE)

                if matches:
                    number_part = matches[0][0].replace(' ', '').replace(',', '.')
                    currency_part = matches[0][1].strip().upper()

                    if not currency_part:
                        currency_part = "AZN"
                    elif currency_part in ["AZN", "MANAT"]:
                        currency_part = "AZN"
                    
                    qiymet_val = f"{number_part} {currency_part}"
                else:
                    qiymet_val = qiymet_text
            
            qiymetler.append(qiymet_val)

    # Məlumatları DataFrame-ə çevirmək
    data = {'Avtomobil Adı': avtomobil_adlari, 'Qiymət': qiymetler}
    df = pd.DataFrame(data)

    # DataFrame-i Excel faylına yazmaq
    excel_faylinin_adi = 'masinlar_az_elanlari.xlsx'
    df.to_excel(excel_faylinin_adi, index=False)

    print(f"Avtomobil adları və qiymətləri '{excel_faylinin_adi}' adlı Excel faylına uğurla yazıldı.")

except requests.exceptions.RequestException as e:
    print(f"Səhifəyə qoşularkən xəta baş verdi: {e}")
except Exception as e:
    print(f"Skrapinq zamanı gözlənilməyən xəta baş verdi: {e}")
