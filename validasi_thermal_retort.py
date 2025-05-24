import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime

st.set_page_config(page_title="Validasi Thermal Retort", layout="wide")
st.title("🔥 Validasi Thermal Proses Sterilisasi - PT Rumah Retort Bersama")

st.markdown("""
Aplikasi ini menghitung nilai **F₀ (F-nol)** dari data suhu per menit selama proses sterilisasi.
Gunakan input manual atau upload file Excel berisi suhu tiap menit.
""")

# Fungsi hitung F0
def calculate_f0(temps, T_ref=121.1, z=10):
    """Menghitung akumulasi nilai F₀ berdasarkan suhu tiap menit."""
    f0_values = []
    for T in temps:
        if T < 90:
            f0_values.append(0)
        else:
            f0_values.append(10 ** ((T - T_ref) / z))
    return np.cumsum(f0_values)

# Simpan riwayat upload ke CSV lokal
def log_upload(filename, total_f0, max_temp, avg_temp):
    log_file = "riwayat_upload.csv"
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = pd.DataFrame([{
        "Waktu": waktu,
        "Nama File": filename,
        "F₀ Total": round(total_f0, 2),
        "Suhu Maks": round(max_temp, 2),
        "Suhu Rata-rata": round(avg_temp, 2)
    }])
    if os.path.exists(log_file):
        data.to_csv(log_file, mode='a', header=False, index=False)
    else:
        data.to_csv(log_file, index=False)

# INPUT METODE
input_method = st.radio("🔘 Pilih Metode Input", ["Manual", "Upload Excel"])

if input_method == "Manual":
    st.subheader("📋 Input Manual Suhu per Menit")
    waktu = st.number_input("Jumlah menit", min_value=1, max_value=120, value=10)
    temps = []
    for i in range(waktu):
        temp = st.number_input(f"Menit ke-{i+1}: Suhu (°C)", value=25.0, step=0.1)
        temps.append(temp)

    if st.button("Hitung F₀"):
        f0 = calculate_f0(temps)
        st.success(f"✅ Nilai F₀ Total: {f0[-1]:.2f}")
        st.write(f"🌡️ Suhu Maksimum: {max(temps):.2f}°C")
        st.write(f"📈 Suhu Rata-rata: {np.mean(temps):.2f}°C")

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

elif input_method == "Upload Excel":
    st.subheader("📤 Upload File Excel")
    uploaded_file = st.file_uploader("Pilih file Excel (.xlsx)", type=["xlsx"])
    
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, header=None)
            st.write("📄 Preview Data:", df.head(15))

            # Cari baris setelah "DATA PANTAUAN"
            start_row = None
            for i, row in df.iterrows():
                if row.astype(str).str.contains("DATA PANTAUAN", case=False, na=False).any():
                    start_row = i + 1
                    break

            if start_row is None:
                raise ValueError("Tidak ditemukan baris 'DATA PANTAUAN'.")

            df_data = df.iloc[start_row:].reset_index(drop=True)

            # Otomatis deteksi kolom suhu dan tekanan
            suhu_col, tekan_col = None, None
            for col in df_data.columns:
                col_data = pd.to_numeric(df_data[col], errors='coerce')
                if (col_data > 90).sum() > 2:
                    suhu_col = col
                elif (col_data > 0).sum() > 5 and tekan_col is None:
                    tekan_col = col

            if suhu_col is None:
                raise ValueError("Kolom suhu tidak ditemukan.")
            
            suhu = pd.to_numeric(df_data[suhu_col], errors='coerce').dropna().tolist()
            f0 = calculate_f0(suhu)
            st.success(f"✅ Nilai F₀ Total: {f0[-1]:.2f}")
            st.write(f"🌡️ Suhu Maksimum: {max(suhu):.2f}°C")
            st.write(f"📈 Suhu Rata-rata: {np.mean(suhu):.2f}°C")

            # Log file ke CSV server
            log_upload(uploaded_file.name, f0[-1], max(suhu), np.mean(suhu))

            # Plot suhu dan F0
            fig, ax = plt.subplots()
            ax.plot(range(1, len(suhu)+1), suhu, label="Suhu (°C)", marker='o')
            ax.axhline(90, color='red', linestyle='--', label="Ambang F₀")
            ax.set_xlabel("Menit")
            ax.set_ylabel("Suhu (°C)")

            ax2 = ax.twinx()
            ax2.plot(range(1, len(f0)+1), f0, color='orange', label="F₀ Akumulatif", linestyle='--')
            ax2.set_ylabel("F₀")

            ax.legend(loc="upper left")
            ax2.legend(loc="upper right")
            st.pyplot(fig)

            # Plot tekanan (jika tersedia)
            if tekan_col is not None:
                tekanan = pd.to_numeric(df_data[tekan_col], errors='coerce').dropna().tolist()
                st.write("📉 Grafik Tekanan:")
                fig2, ax3 = plt.subplots()
                ax3.plot(range(1, len(tekanan)+1), tekanan, color='blue', label="Tekanan (bar)", marker='x')
                ax3.set_xlabel("Menit")
                ax3.set_ylabel("Tekanan (bar)")
                ax3.legend()
                st.pyplot(fig2)

        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses file: {e}")
