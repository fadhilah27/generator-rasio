import streamlit as st
import pandas as pd
import random
import io
import calendar

# --- DATABASE MULTI-KORIDOR ---
DATABASE_KORIDOR = {
    "K7": {
        "nopol": {
            f"LB{str(i).zfill(2)}": nopol for i, nopol in zip(range(1, 16), [
                "S 7051 UJ", "S 7091 UJ", "S 7044 UJ", "S 7039 UJ", "S 7096 UJ", 
                "S 7048 UJ", "S 7093 UJ", "S 7094 UJ", "S 7047 UJ", "S 7052 UJ", 
                "S 7056 UJ", "S 7090 UJ", "S 7095 UJ", "S 7042 UJ", "S 7092 UJ"
            ])
        },
        "default_km": 297,
        "cash_harian": 600000
    },
    "FD06": {
        "nopol": {
            "WW 108": "L 7121 UF", "WW 109": "L 7111 UF", "WW 110": "L 7116 UF", "WW 111": "L 7124 UF",
            "WW 112": "L 7123 UF", "WW 113": "L 7114 UF", "WW 114": "L 7110 UF", "WW 115": "L 7115 UF",
            "WW 116": "L 7127 UF", "WW 117": "L 7126 UF", "WW 118": "L 7113 UF", "WW 119": "L 7118 UF",
            "WW 120": "L 7109 UF", "WW 121": "L 7112 UF", "WW 122": "L 7120 UF", "WW 123": "L 7119 UF",
            "WW 124": "L 7125 UF", "WW 125": "L 7108 UF", "WW 126": "L 7122 UF" 
        },
        "default_km": 209.76, 
        "cash_harian": 35000 
    },
    "R5": {
        "nopol": {
            "SB 39": "L 7060 UF", "SB 40": "L 7061 UF", "SB 41": "L 7062 UF", "SB 42": "L 7063 UF", "SB 43": "L 7064 UF",
            "SB 44": "L 7065 UF", "SB 45": "L 7066 UF", "SB 46": "L 7067 UF", "SB 47": "L 7068 UF", "SB 48": "L 7069 UF",
            "SB 49": "L 7071 UF", "SB 50": "L 7072 UF", "SB 51": "L 7073 UF", "SB 52": "L 7074 UF", "SB 53": "L 7075 UF",
            "SB 54": "L 7076 UF", "SB 55": "L 7077 UF", "SB 56": "L 7092 UF", "SB 57": "L 7093 UF", "SB 58": "L 7094 UF", 
            "SB 76": "L 7099 UF", "SB 77": "L 7101 UF", "SB 78": "L 7102 UF" 
        },
        "default_km": 210, 
        "cash_harian": 500000 
    }
}

HARGA_BIO_SOLAR = 6800

BULAN_DICT = {
    "Januari": 1, "Februari": 2, "Maret": 3, "April": 4, 
    "Mei": 5, "Juni": 6, "Juli": 7, "Agustus": 8, 
    "September": 9, "Oktober": 10, "November": 11, "Desember": 12
}

st.set_page_config(page_title="Generator Rasio BBM", layout="wide")
st.title("🚌 Auto-Generator LPJ (Lutfi Laeli Nur Afita ❤️)")

# --- 1. PENGATURAN PARAMETER ---
st.markdown("### 1. Pengaturan Utama")
col0, col1, col2, col3, col4, col5, col6 = st.columns(7) 

with col0:
    pilihan_koridor = st.selectbox("Koridor", list(DATABASE_KORIDOR.keys()))

konfig_aktif = DATABASE_KORIDOR[pilihan_koridor]
NOPOL_BUS = konfig_aktif["nopol"]
LIST_ARMADA = list(NOPOL_BUS.keys())
DEFAULT_KM = konfig_aktif["default_km"]
CASH_HARIAN = konfig_aktif["cash_harian"]

with col1:
    target_min = st.number_input("Rasio Minimal", value=4.15, step=0.01)
with col2:
    target_max = st.number_input("Rasio Maksimal", value=4.20, step=0.01)
with col3:
    pilihan_bulan = st.selectbox("Bulan", list(BULAN_DICT.keys()), index=9)
with col4:
    pilihan_tahun = st.number_input("Tahun", value=2026, min_value=2020, max_value=2035)
with col5:
    harga_non_sub_acuan = st.number_input("Harga Non-Sub (Rp)", value=21412, step=100)
with col6:
    nama_spbu = st.text_input("Nama SPBU", value="Sidogembul")

bulan_angka = BULAN_DICT[pilihan_bulan]
jumlah_hari = calendar.monthrange(pilihan_tahun, bulan_angka)[1]

# --- 2. TABEL MATRIKS KM ---
session_key_km = f'df_matriks_km_{pilihan_koridor}'

if session_key_km not in st.session_state:
    data_awal = {"Hari ke-": list(range(1, 32))}
    for lb in LIST_ARMADA:
        data_awal[lb] = [DEFAULT_KM] * 31
    st.session_state[session_key_km] = pd.DataFrame(data_awal)

st.markdown(f"### 2. Matriks Jarak Tempuh (KM) - {pilihan_koridor}")
df_input = st.session_state[session_key_km].head(jumlah_hari)
edited_km = st.data_editor(df_input, num_rows="dynamic", use_container_width=True)

# --- 3. TABEL PENGECUALIAN DEXLITE ---
st.markdown("### 3. Pengecualian Struk (Non-Subsidi)")
session_key_override = f'df_override_{pilihan_koridor}'

if session_key_override not in st.session_state:
    st.session_state[session_key_override] = pd.DataFrame({
        "Hari ke-": [10],
        "Armada": [LIST_ARMADA[0]],
        "Jenis BBM": ["Dexlite"],
        "Harga per Liter": [13700],
        "Total Beli (Rp)": [0]
    })

edited_override = st.data_editor(
    st.session_state[session_key_override],
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Hari ke-": st.column_config.NumberColumn(min_value=1, max_value=jumlah_hari),
        "Armada": st.column_config.SelectboxColumn(options=LIST_ARMADA),
        "Jenis BBM": st.column_config.SelectboxColumn(options=["Dexlite", "Pertamina Dex"]),
        "Harga per Liter": st.column_config.NumberColumn(step=100),
        "Total Beli (Rp)": st.column_config.NumberColumn(step=1000)
    }
)

if 'hasil_simulasi' not in st.session_state:
    st.session_state.hasil_simulasi = None

# --- 4. TOMBOL GENERATE ---
if st.button(f"🎲 Generate Data {pilihan_koridor}", type="primary"):
    dict_pengecualian = {}
    for _, row_ov in edited_override.iterrows():
        if row_ov['Total Beli (Rp)'] > 0:
            kunci = (int(row_ov['Hari ke-']), row_ov['Armada'])
            harga_liter = int(row_ov['Harga per Liter'])
            total_rp = int(row_ov['Total Beli (Rp)'])
            liter_dex = round(total_rp / harga_liter, 2)
            
            dict_pengecualian[kunci] = {
                'Jenis BBM': row_ov['Jenis BBM'],
                'Harga': harga_liter,
                'Total Rp': total_rp,
                'Liter': liter_dex
            }
            
    dict_hasil = {}
    
    for armada in LIST_ARMADA:
        nopol = NOPOL_BUS.get(armada, "-")
        data_sheet = []
        
        for idx, row in edited_km.iterrows():
            km_val = int(row[armada])
            hari = int(row['Hari ke-'])
            kunci_cek = (hari, armada)
            
            # PENGATURAN JAM DIMULAI DARI JAM 10 PAGI - 23 MALAM
            jam = random.randint(10, 23)
            menit = random.randint(0, 59)
            detik = random.randint(0, 59)
            tanggal_str = f"{pilihan_tahun}-{str(bulan_angka).zfill(2)}-{str(hari).zfill(2)} {str(jam).zfill(2)}:{str(menit).zfill(2)}:{str(detik).zfill(2)}"
            
            if km_val > 0:
                acak_rasio = random.uniform(target_min, target_max)
                liter_total_harian = round(km_val / acak_rasio, 2)
                rasio_gabungan = round(km_val / liter_total_harian, 2) 
                
                if kunci_cek in dict_pengecualian:
                    data_dex = dict_pengecualian[kunci_cek]
                    jenis_dex = data_dex['Jenis BBM']
                    harga_dex = data_dex['Harga']
                    pemb_dex = data_dex['Total Rp']
                    liter_dex = data_dex['Liter']
                    
                    liter_bio_sisa = round(liter_total_harian - liter_dex, 2)
                    
                    if liter_bio_sisa > 0:
                        non_sub_dex = pemb_dex 
                        data_sheet.append([
                            tanggal_str, armada, nopol, km_val, rasio_gabungan,
                            nama_spbu, jenis_dex, liter_dex, harga_dex, pemb_dex,
                            non_sub_dex, 0, CASH_HARIAN, pemb_dex - CASH_HARIAN
                        ])
                        
                        pemb_bio = liter_bio_sisa * HARGA_BIO_SOLAR
                        non_sub_bio = liter_bio_sisa * harga_non_sub_acuan
                        subsidi_bio = non_sub_bio - pemb_bio
                        
                        data_sheet.append([
                            "", "", "", "", "",
                            nama_spbu, "Bio Solar", liter_bio_sisa, HARGA_BIO_SOLAR, pemb_bio,
                            non_sub_bio, subsidi_bio, 0, pemb_bio
                        ])
                    else:
                        data_sheet.append([
                            tanggal_str, armada, nopol, km_val, rasio_gabungan,
                            nama_spbu, jenis_dex, liter_dex, harga_dex, pemb_dex,
                            pemb_dex, 0, CASH_HARIAN, pemb_dex - CASH_HARIAN
                        ])
                else:
                    pembayaran = liter_total_harian * HARGA_BIO_SOLAR
                    total_non_sub = liter_total_harian * harga_non_sub_acuan
                    total_subsidi = total_non_sub - pembayaran
                    
                    data_sheet.append([
                        tanggal_str, armada, nopol, km_val, rasio_gabungan,
                        nama_spbu, "Bio Solar", liter_total_harian, HARGA_BIO_SOLAR, pembayaran,
                        total_non_sub, total_subsidi, CASH_HARIAN, pembayaran - CASH_HARIAN
                    ])
            else:
                data_sheet.append([
                    tanggal_str, armada, nopol, "", "",
                    nama_spbu, "-", 0, 0, 0,
                    0, 0, CASH_HARIAN, -CASH_HARIAN
                ])
        
        kolom = ['Tanggal', 'No. Lambung', 'No. Polisi', 'KM', 'Rasio', 'SPBU', 'Jenis BBM', 'Liter', 'Harga BBM', 'Jumlah Pembayaran', 'Non Sub', 'Subsidi', 'Cash', 'Change']
        dict_hasil[armada] = pd.DataFrame(data_sheet, columns=kolom)
    
    st.session_state.hasil_simulasi = dict_hasil
    st.success(f"✅ Data LPJ {pilihan_koridor} untuk {pilihan_bulan} {pilihan_tahun} berhasil di-generate!")

# --- 5. PREVIEW & EXPORT ---
if st.session_state.hasil_simulasi:
    st.markdown("---")
    st.markdown(f"### 4. Preview Hasil Laporan {pilihan_koridor}")
    
    pilih_unit = st.selectbox("Pilih unit untuk melihat detail datanya:", LIST_ARMADA)
    
    df_tampil = st.session_state.hasil_simulasi[pilih_unit].copy()
    
    df_tampil['Rasio'] = df_tampil['Rasio'].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) and pd.notna(x) and str(x).strip() != "" else "")
    
    kolom_uang = ['Harga BBM', 'Jumlah Pembayaran', 'Non Sub', 'Subsidi', 'Cash', 'Change']
    for k in kolom_uang:
        df_tampil[k] = df_tampil[k].apply(lambda x: f"Rp {x:,.0f}".replace(',', '.') if isinstance(x, (int, float)) and pd.notna(x) and str(x).strip() != "" else "")
        
    st.dataframe(df_tampil, use_container_width=True)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D9D9D9', 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        cell_center = workbook.add_format({'border': 1, 'align': 'center'})
        ratio_format = workbook.add_format({'border': 1, 'align': 'center', 'num_format': '0.00'})
        money_format = workbook.add_format({'border': 1, 'num_format': 'Rp #,##0'})
        date_format = workbook.add_format({'border': 1, 'align': 'center', 'num_format': 'yyyy-mm-dd hh:mm:ss'})
        
        for sheet_name, df_sheet in st.session_state.hasil_simulasi.items():
            df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)
            worksheet = writer.sheets[sheet_name]
            
            for col_num, value in enumerate(df_sheet.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            worksheet.set_column('A:A', 19, date_format) 
            worksheet.set_column('B:C', 13, cell_center)
            worksheet.set_column('D:D', 8, cell_center)
            worksheet.set_column('E:E', 8, ratio_format)
            worksheet.set_column('F:G', 12, cell_center)
            worksheet.set_column('H:H', 10, cell_center)
            worksheet.set_column('I:N', 15, money_format)
            
    st.markdown("### 5. Unduh Laporan")
    st.download_button(
        label=f"📥 Download Laporan {pilihan_koridor} {pilihan_bulan} {pilihan_tahun} (Excel)",
        data=output.getvalue(),
        file_name=f"LPJ_{pilihan_koridor}_{pilihan_bulan}_{pilihan_tahun}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )