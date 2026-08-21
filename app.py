import streamlit as st
import os
from pypdf import PdfReader
from google import genai

# 1. Mengambil API Key dan menyiapkan Client GenAI terbaru
api_key = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=api_key)

PDF_FILE_PATH = "16_PRT_M_2018.pdf" 

@st.cache_data
def ekstrak_semua_teks():
    st.info("Sedang membaca seluruh halaman dokumen klasifikasi. Mohon tunggu...")
    reader = PdfReader(PDF_FILE_PATH)
    teks_lengkap = ""
    for i, halaman in enumerate(reader.pages):
        nomor_halaman = i + 1 
        # Penanda halaman ini dibuat sangat MENCOLOK agar AI tidak kelewatan
        teks_lengkap += f"\n\n======================================================\n"
        teks_lengkap += f"--- [INFO UNTUK AI: TEKS DI BAWAH INI ADALAH HALAMAN {nomor_halaman}] ---\n"
        teks_lengkap += f"======================================================\n\n"
        
        teks_ekstrak = halaman.extract_text()
        if teks_ekstrak:
            teks_lengkap += teks_ekstrak + "\n"
            
    st.success("Dokumen berhasil dipahami oleh sistem!")
    return teks_lengkap

# --- TAMPILAN WEB ---
st.set_page_config(page_title="Pencari Kode Arsip", page_icon="🗂️")
st.title("🗂️ Asisten Klasifikasi Arsip PUPR")
st.markdown("Ketikkan nama barang atau kegiatan. AI akan mencarikan kode klasifikasinya beserta halamannya dari dokumen Permen PUPR No 16/PRT/M/2018.")

teks_pdf = ekstrak_semua_teks()

user_query = st.text_input("Contoh pencarian: pengadaan semen, pelelangan aset, cuti sakit")

if user_query:
    with st.spinner("AI sedang memindai ratusan halaman secara instan untuk Anda..."):
        # Instruksi (Prompt) ini diperketat untuk menghindari halusinasi
        prompt = f"""Kamu adalah asisten arsiparis ahli dan sangat teliti di Kementerian PUPR. 
        Tugasmu mencari kode klasifikasi arsip berdasarkan SELURUH TEKS dokumen Permen PUPR No 16/PRT/M/2018. Teks ini merupakan hasil ekstraksi PDF, jadi tabel mungkin terbaca sebagai teks biasa yang terpisah-pisah.

        ATURAN WAJIB (HARUS DITAATI, JANGAN DILANGGAR):
        1. JANGAN MENGARANG KODE ATAU HALAMAN. Ini adalah dokumen hukum.
        2. CARI SECARA MENDALAM & GUNAKAN SINONIM: Jika pengguna mencari "pelelangan aset", kamu WAJIB mencari kata terkait seperti "lelang", "pemindahtanganan", "penghapusan", "Barang Milik Negara", "BMN" (Contoh: periksa kelompok kode PS atau Pengelolaan Barang Milik Negara seperti PS.05.01). Jangan mudah menyerah!
        3. NOMOR HALAMAN HARUS AKURAT: Cari penanda `--- [INFO UNTUK AI: TEKS DI BAWAH INI ADALAH HALAMAN X] ---` yang PALING DEKAT DI ATAS teks yang kamu temukan. Gunakan angka X tersebut. (Ingat, klasifikasi arsip biasanya baru dimulai di atas halaman 25, jadi mustahil kodenya ada di halaman 10 atau 12).
        
        FORMAT JAWABAN:
        1. Analisis Awal: Jelaskan hasil pencarianmu (termasuk sinonim yang kamu gunakan jika kata aslinya tidak ada).
        2. Berikan pilihan berdasarkan konteks, gunakan nomor (1, 2, 3).
        3. Gunakan bullet point di bawah angka.
        4. Wajib gunakan format: **[KODE] ([Nama Klasifikasi])**: [Penjelasan]. *(Ditemukan persis di Halaman X)*.

        TEKS DOKUMEN:
        {teks_pdf}

        PERTANYAAN PENGGUNA: {user_query}

        JAWABAN:"""
        
        try:
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt
            )
            st.markdown("### Hasil Pencarian:")
            st.write(response.text)
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
