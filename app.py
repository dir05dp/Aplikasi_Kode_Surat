import streamlit as st
import os
from pypdf import PdfReader
from langchain_google_genai import ChatGoogleGenerativeAI

# Mengambil API Key dari brankas rahasia Streamlit Cloud
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

# Pastikan nama file PDF sama persis dengan di GitHub
PDF_FILE_PATH = "16_PRT_M_2018.pdf" 

# Fungsi super simpel untuk membaca semua teks PDF sekaligus
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
st.title("🗂️ Aplikasi Asisten Membantu Mencari Kode Klasifikasi Surat")
st.markdown("Ketikkan perihal surat/kegiatan. AI akan mencarikan kode klasifikasinya dari dokumen Permen PUPR No 16/PRT/M/2018.")

# 1. Tarik semua teks PDF
teks_pdf = ekstrak_semua_teks()

# 2. Siapkan Otak Gemini 1.5 Flash
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)

user_query = st.text_input("Silahkan perihal surat/kegiatan")

if user_query:
    with st.spinner("AI sedang memindai Permen No 16/PRT/M/2018 untuk Anda..."):
        # 3. Masukkan seluruh teks PDF dan pertanyaan ke dalam satu instruksi
        prompt = f"""Kamu adalah asisten arsiparis profesional di Kementerian PUPR. 
        Gunakan SELURUH TEKS dokumen Permen PUPR No 16/PRT/M/2018 di bawah ini untuk mencari kode klasifikasi arsip yang ditanyakan.
        Sebutkan kodenya, nama klasifikasi, dan alasan singkatnya. Jika tidak ada yang sama persis, berikan saran yang paling mendekati konsepnya.

        TEKS DOKUMEN:
        {teks_pdf}

        PERTANYAAN PENGGUNA: {user_query}

        JAWABAN:"""
        
        # 4. Minta Gemini menjawab
        response = llm.invoke(prompt)
        
        st.markdown("### Hasil Pencarian:")
        st.write(response.content)
