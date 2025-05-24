import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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

def extract_suhu_from_umkm_excel(file):
    try:
        xls = pd.ExcelFile(file)
        df_raw = xls.parse('Sheet1', header=None)

        # Cari baris tempat suhu mulai muncul
        start_row = None
        for i, row in df_raw.iterrows():
            if row.astype(str).str.contains("DATA PANTAUAN", case=False).any():
                start_row = i + 1  # data biasanya mulai 1 baris setelah label
                break

        if start_row is None:
            raise ValueError("Baris data suhu tidak ditemukan.")

        # Ambil data dari baris start_row ke bawah
        df_data = df_raw.iloc[start_row:].reset_index(drop=True)

        # Deteksi kolom suhu
        suhu_col = None
        for col in df_data.columns:
            if df_data[col].astype(str).str.contains("suhu", case=False).any():
                suhu_col = col
                break

        if suhu_col is None:
            # fallback: ambil kolom ke-2
            suhu_col = 1

        temps = pd.to_numeric(df_data[suhu_col], errors='coerce').dropna().tolist()

        return temps

    except Exception as e:
        st.error(f"Gagal ekstrak suhu dari file: {e}")
        return []

st.set_page_config(page_title="Validasi Thermal Retort", layout="wide")
st.title("🔥 Validasi Thermal Proses Sterilisasi - PT Rumah Retort Bersama")

st.markdown("""
Aplikasi ini menghitung nilai **F₀ (F-nol)** dari data suhu per menit selama proses sterilisasi.
Gunakan input manual atau upload file Excel berisi suhu tiap menit.
""")

def calculate_f0(temps, T_ref=121.1, z=10):
    """Menghitung akumulasi nilai F₀ berdasarkan suhu tiap menit."""
    f0_values = []
    for T in temps:
        if T < 90:
            f0_values.append(0)
        else:
            f0_values.append(10 ** ((T - T_ref) / z))
    return np.cumsum(f0_values)

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
        fig, ax = plt.subplots()
        ax.plot(range(1, len(temps)+1), temps, label="Suhu (°C)", marker='o')
        ax.set_xlabel("Menit")
        ax.set_ylabel("Suhu (°C)")
        ax2 = ax.twinx()
        ax2.plot(range(1, len(f0)+1), f0, color='orange', label="F₀ Akumulatif", linestyle='--')
        ax2.set_ylabel("F₀")
        st.pyplot(fig)

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
