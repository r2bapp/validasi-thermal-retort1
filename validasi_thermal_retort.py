import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import io
import csv

def extract_suhu_from_umkm_excel(file):
    try:
        xls = pd.ExcelFile(file)
        df_raw = xls.parse('Sheet1', header=None)

        # Cari baris tempat data suhu dimulai
        start_row = None
        for i, row in df_raw.iterrows():
            if row.astype(str).str.contains("DATA PANTAUAN", case=False).any():
                start_row = i + 1
                break

        if start_row is None:
            raise ValueError("Baris data suhu tidak ditemukan.")

        df_data = df_raw.iloc[start_row:].reset_index(drop=True)

        # Cari kolom yang mengandung angka > 100 (indikasi suhu)
        suhu_col = None
        for col in df_data.columns:
            numeric_col = pd.to_numeric(df_data[col], errors='coerce')
            if (numeric_col > 90).sum() > 2:
                suhu_col = col
                break

        if suhu_col is None:
            suhu_col = 1  # fallback

        temps = pd.to_numeric(df_data[suhu_col], errors='coerce').dropna().tolist()
        return temps

    except Exception as e:
        st.error(f"Gagal ekstrak suhu dari file: {e}")
        return []
            
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
    pdf.cell(200, 10, txt=f"Durasi Suhu >=121°C: {durasi_121} menit", ln=True)
    pdf.cell(200, 10, txt=f"Status Validasi: {'VALID' if valid else 'TIDAK VALID'}", ln=True)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# Streamlit UI
st.title("Validasi Thermal Proses Sterilisasi - PT Rumah Retort Bersama")
uploaded_file = st.file_uploader("Unggah file Excel suhu per menit", type=['xlsx'])

    if uploaded_file:
        temps = extract_suhu_from_umkm_excel(uploaded_file)

        if len(temps) == 0:
            st.error("❌ Tidak ada data suhu valid ditemukan.")
        else:
            st.info(f"📊 Data suhu valid ditemukan: {len(temps)} menit")
            st.line_chart(temps, use_container_width=True)

            f0 = calculate_f0(temps)

            if f0[-1] == 0:
                st.warning("⚠️ Suhu sudah >90°C, tapi nilai F₀ masih nol. Cek kembali logika atau durasi suhu tinggi.")
            else:
                st.success(f"✅ Nilai F₀ Total: {f0[-1]:.2f}")

            # Plot dengan suhu dan F0
            fig, ax = plt.subplots()
            ax.plot(range(1, len(temps)+1), temps, label="Suhu (°C)", marker='o')
            ax.axhline(90, color='red', linestyle='--', label="Ambang F₀ (90°C)")
            ax.set_xlabel("Menit")
            ax.set_ylabel("Suhu (°C)")

            ax2 = ax.twinx()
            ax2.plot(range(1, len(f0)+1), f0, color='orange', label="F₀ Akumulatif", linestyle='--')
            ax2.set_ylabel("F₀")

            ax.legend(loc="upper left")
            ax2.legend(loc="upper right")
            st.pyplot(fig)
