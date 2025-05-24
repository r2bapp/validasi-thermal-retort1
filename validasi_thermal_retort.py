import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import io
import csv

# Konstanta untuk perhitungan F0
T_REF = 121.1
Z_VALUE = 10

def hitung_f0(data):
    f0_total = 0
    suhu_121_ke_atas = []
    durasi_121 = 0

    for i in range(len(data)):
        suhu = data[i]
        if pd.isna(suhu):
            continue

        delta_t = 1  # menit
        f0 = 10 ** ((suhu - T_REF) / Z_VALUE) * delta_t
        f0_total += f0

        if suhu >= 121:
            suhu_121_ke_atas.append(1)
            durasi_121 += 1
        else:
            suhu_121_ke_atas.append(0)

    return round(f0_total, 2), durasi_121

def buat_grafik(suhu):
    fig, ax = plt.subplots()
    ax.plot(range(len(suhu)), suhu, marker='o')
    ax.axhline(121, color='red', linestyle='--', label='121°C')
    ax.set_xlabel('Menit')
    ax.set_ylabel('Suhu (°C)')
    ax.set_title('Grafik Suhu per Menit')
    ax.legend()
    st.pyplot(fig)

def simpan_log_csv(nama_file, f0, valid, durasi_121):
    log_path = 'log_validasi.csv'
    waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = ['timestamp', 'nama_file', 'F0', 'status_validasi', 'durasi_121C']
    row = [waktu, nama_file, f0, valid, durasi_121]

    try:
        with open(log_path, 'a', newline='') as f:
            writer = csv.writer(f)
            if f.tell() == 0:
                writer.writerow(header)
            writer.writerow(row)
    except Exception as e:
        st.error(f"Gagal menyimpan log: {e}")

def buat_pdf_laporan(nama_file, f0, valid, durasi_121):
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="LAPORAN VALIDASI THERMAL RETORT", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Nama File: {nama_file}", ln=True)
    pdf.cell(200, 10, txt=f"Nilai F0: {f0}", ln=True)
    pdf.cell(200, 10, txt=f"Durasi Suhu ≥121°C: {durasi_121} menit", ln=True)
    pdf.cell(200, 10, txt=f"Status Validasi: {'VALID' if valid else 'TIDAK VALID'}", ln=True)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# Streamlit UI
st.title("Validasi Thermal Proses Sterilisasi - PT Rumah Retort Bersama")
uploaded_file = st.file_uploader("Unggah file Excel suhu per menit", type=['xlsx'])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        st.write("### Data Suhu Mentah")
        st.dataframe(df)

        # Ambil hanya kolom suhu otomatis
        suhu_col = [col for col in df.columns if "suhu" in col.lower()][0]
        suhu_data = df[suhu_col].tolist()

        # Hitung F0 dan validasi suhu ≥121°C selama 3 menit
        f0, durasi_121 = hitung_f0(suhu_data)
        is_valid = durasi_121 >= 3

        # Tampilkan hasil
        st.success(f"Nilai F0: {f0}")
        st.info(f"Durasi suhu ≥121°C: {durasi_121} menit")
        st.markdown(f"### Status: {'✅ PROSES STERIL VALID' if is_valid else '❌ TIDAK MEMENUHI SYARAT'}")

        # Tampilkan grafik
        st.write("### Grafik Suhu")
        buat_grafik(suhu_data)

        # Simpan log
        simpan_log_csv(uploaded_file.name, f0, 'VALID' if is_valid else 'TIDAK VALID', durasi_121)

        # Tombol unduh PDF
        pdf_buffer = buat_pdf_laporan(uploaded_file.name, f0, is_valid, durasi_121)
        st.download_button(
            label="Unduh Laporan PDF",
            data=pdf_buffer,
            file_name="laporan_validasi.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses file: {e}")
