import streamlit as st
import os
from pypdf import PdfReader
from google import genai

# 1. Mengambil API Key dan menyiapkan Client GenAI terbaru
api_key = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=api_key)

# Pastikan nama file PDF sama persis dengan di GitHub
PDF_FILE_PATH = "16_PRT_M_2018.pdf" 

@st.cache_data
def ekstrak_semua_teks():
    st.info("Sedang membaca seluruh halaman dokumen klasifikasi. Mohon tunggu...")
    reader = PdfReader(PDF_FILE_PATH)
    teks_lengkap = ""
    for halaman in reader.pages:
        teks_lengkap += halaman.extract_text() + "\n"
    st.success("Dokumen berhasil dipahami oleh sistem!")
    return teks_lengkap

# --- TAMPILAN WEB ---
st.set_page_config(page_title="Pencari Kode Arsip", page_icon="🗂️")
st.title("🗂️ Asisten Klasifikasi Arsip PUPR")
st.markdown("Ketikkan nama barang atau kegiatan. AI akan mencarikan kode klasifikasinya dari dokumen Permen PUPR No 16/PRT/M/2018.")

# 2. Tarik semua teks PDF
teks_pdf = ekstrak_semua_teks()

user_query = st.text_input("Contoh pencarian: pengadaan semen, cuti sakit, rapat kerja")

if user_query:
    with st.spinner("AI sedang memindai ratusan halaman secara instan untuk Anda..."):
        prompt = f"""Kamu adalah asisten arsiparis profesional di Kementerian PUPR. 
        Gunakan SELURUH TEKS dokumen Permen PUPR No 16/PRT/M/2018 di bawah ini untuk mencari kode klasifikasi arsip yang ditanyakan.
        Sebutkan kodenya, nama klasifikasi, dan alasan singkatnya. Jika tidak ada yang sama persis, berikan saran yang paling mendekati konsepnya.

        TEKS DOKUMEN:
        {teks_pdf}

        PERTANYAAN PENGGUNA: {user_query}

        JAWABAN:"""
        
        # 3. Minta Gemini menjawab menggunakan format SDK terbaru
        try:
            response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
            
            st.markdown("### Hasil Pencarian:")
            st.write(response.text)
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
