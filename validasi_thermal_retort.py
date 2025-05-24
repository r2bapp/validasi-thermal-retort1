import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Validasi Thermal Retort", layout="wide")
st.title("🔥 Validasi Thermal Proses Sterilisasi - PT Rumah Retort Bersama")

st.markdown("""
Aplikasi ini menghitung nilai **F₀ (F-nol)** dari data suhu per menit selama proses sterilisasi.
Gunakan input manual atau upload file Excel berisi suhu tiap menit.
""")

# Fungsi hitung F₀
def calculate_f0(temps, T_ref=121.1, z=10):
    f0_values = []
    for T in temps:
        if T < 90:
            f0_values.append(0)
        else:
            f0_values.append(10 ** ((T - T_ref) / z))
    return np.cumsum(f0_values)

# Fungsi ekstraksi suhu dari file Excel UMKM
def extract_suhu_from_umkm_excel(file):
    try:
        xls = pd.ExcelFile(file)
        df_raw = xls.parse('Sheet1', header=None)

        # Cari baris tempat data suhu dimulai
        start_row = None
        for i, row in df_raw.iterrows():
            if row.astype(str).str.contains("DATA PANTAUAN", case=False, na=False).any():
                start_row = i + 1
                break

        if start_row is None:
            raise ValueError("Baris 'DATA PANTAUAN' tidak ditemukan.")

        df_data = df_raw.iloc[start_row:].reset_index(drop=True)

        suhu_col = None
        for col in df_data.columns:
            numeric_col = pd.to_numeric(df_data[col], errors='coerce')
            if (numeric_col > 90).sum() > 2:
                suhu_col = col
                break

        if suhu_col is None:
            raise ValueError("Kolom suhu tidak ditemukan.")

        suhu = pd.to_numeric(df_data[suhu_col], errors='coerce').dropna().tolist()
        return suhu

    except Exception as e:
        st.error(f"❌ Gagal ekstrak suhu dari file: {e}")
        return []

# Fungsi cek suhu minimal 121.1°C selama ≥3 menit
def check_minimum_holding_time(temps, min_temp=121.1, min_duration=3):
    holding_minutes = 0
    for t in temps:
        if t >= min_temp:
            holding_minutes += 1
            if holding_minutes >= min_duration:
                return True
        else:
            holding_minutes = 0
    return False

# Pilihan metode input
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

        if check_minimum_holding_time(temps):
            st.success("✅ Suhu ≥121.1°C tercapai minimal selama 3 menit")
        else:
            st.warning("⚠️ Suhu ≥121.1°C belum tercapai selama 3 menit")

        fig, ax = plt.subplots()
        ax.plot(range(1, len(temps)+1), temps, label="Suhu (°C)", marker='o')
        ax.axhline(90, color='red', linestyle='--', label="Ambang F₀ (90°C)")
        ax.axhline(121.1, color='green', linestyle='--', label="Target BPOM (121.1°C)")
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

            if check_minimum_holding_time(temps):
                st.success("✅ Suhu ≥121.1°C tercapai minimal selama 3 menit")
            else:
                st.warning("⚠️ Suhu ≥121.1°C belum tercapai selama 3 menit")

            fig, ax = plt.subplots()
            ax.plot(range(1, len(temps)+1), temps, label="Suhu (°C)", marker='o')
            ax.axhline(90, color='red', linestyle='--', label="Ambang F₀ (90°C)")
            ax.axhline(121.1, color='green', linestyle='--', label="Target BPOM (121.1°C)")
            ax.set_xlabel("Menit")
            ax.set_ylabel("Suhu (°C)")

            ax2 = ax.twinx()
            ax2.plot(range(1, len(f0)+1), f0, color='orange', label="F₀ Akumulatif", linestyle='--')
            ax2.set_ylabel("F₀")

            ax.legend(loc="upper left")
            ax2.legend(loc="upper right")
            st.pyplot(fig)
