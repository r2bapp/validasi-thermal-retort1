import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Validasi Thermal Retort", layout="wide")
st.title("🔍 Validasi Thermal Proses Sterilisasi - PT Rumah Retort Bersama")

st.markdown("Masukkan data suhu per menit untuk menghitung nilai **F₀** proses sterilisasi.")

def calculate_f0(temps, T_ref=121.1, z=10):
    f0_values = []
    for T in temps:
        if T < 90:
            f0_values.append(0)
        else:
            f0_values.append(10 ** ((T - T_ref) / z))
    return np.cumsum(f0_values)

input_method = st.radio("Pilih Metode Input", ["Manual", "Upload Excel"])

if input_method == "Manual":
    st.subheader("Input Manual Suhu per Menit")
    waktu = st.number_input("Jumlah menit", min_value=1, max_value=120, value=10)
    temps = []
    for i in range(waktu):
        temp = st.number_input(f"Menit ke-{i+1}: Suhu (°C)", value=25.0, step=0.1)
        temps.append(temp)

    if st.button("Hitung F₀"):
        f0 = calculate_f0(temps)
        st.success(f"Nilai F₀ Total: {f0[-1]:.2f}")
        fig, ax = plt.subplots()
        ax.plot(range(1, len(temps)+1), temps, label="Suhu (°C)")
        ax.set_xlabel("Menit")
        ax.set_ylabel("Suhu (°C)")
        ax2 = ax.twinx()
        ax2.plot(range(1, len(f0)+1), f0, color='orange', label="F₀ Akumulatif")
        ax2.set_ylabel("F₀")
        st.pyplot(fig)

elif input_method == "Upload Excel":
    st.subheader("Upload File Excel")
    uploaded_file = st.file_uploader("Pilih file Excel (.xlsx)", type=["xlsx"])
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            st.write("Preview Data:", df.head())
            suhu_col = st.selectbox("Pilih kolom suhu (°C):", df.columns)
            temps = df[suhu_col].dropna().tolist()
            f0 = calculate_f0(temps)
            st.success(f"Nilai F₀ Total: {f0[-1]:.2f}")
            fig, ax = plt.subplots()
            ax.plot(range(1, len(temps)+1), temps, label="Suhu (°C)")
            ax.set_xlabel("Menit")
            ax.set_ylabel("Suhu (°C)")
            ax2 = ax.twinx()
            ax2.plot(range(1, len(f0)+1), f0, color='orange', label="F₀ Akumulatif")
            ax2.set_ylabel("F₀")
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Gagal membaca file: {e}")
