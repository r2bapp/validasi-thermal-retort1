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
            if row.astype(str).str.contains("DATA PANTAUAN", case=False, na=False).any():
                start_row = i + 1
                break

        if start_row is None:
            raise ValueError("Baris 'DATA PANTAUAN' tidak ditemukan.")

        # Ambil data setelah baris 'DATA PANTAUAN'
        df_data = df_raw.iloc[start_row:].reset_index(drop=True)

        # Cari kolom yang paling mungkin berisi data suhu
        suhu_col = None
        for col in df_data.columns:
            numeric_col = pd.to_numeric(df_data[col], errors='coerce')
            if (numeric_col > 90).sum() > 2:  # asumsi suhu makanan > 90°C
                suhu_col = col
                break

        if suhu_col is None:
            raise ValueError("Kolom suhu tidak ditemukan.")

        # Ambil data suhu dan buang NaN
        suhu = pd.to_numeric(df_data[suhu_col], errors='coerce').dropna().tolist()
        return suhu

    except Exception as e:
        st.error(f"❌ Gagal ekstrak suhu dari file: {e}")
        return []

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
