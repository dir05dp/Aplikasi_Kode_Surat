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
    for i, halaman in enumerate(reader.pages):
        nomor_halaman = i + 1 # Menghitung nomor halaman sesungguhnya
        # Menyisipkan penanda halaman rahasia agar AI tahu posisi halamannya
        teks_lengkap += f"\n\n--- [INFO UNTUK AI: TEKS DI BAWAH INI BERADA DI HALAMAN {nomor_halaman}] ---\n\n"
        
        teks_ekstrak = halaman.extract_text()
        if teks_ekstrak:
            teks_lengkap += teks_ekstrak + "\n"
            
    st.success("Dokumen berhasil dipahami oleh sistem!")
    return teks_lengkap

# --- TAMPILAN WEB ---
st.set_page_config(page_title="Pencari Kode Arsip", page_icon="🗂️")
st.title("🗂️ Asisten Klasifikasi Arsip PUPR")
st.markdown("Ketikkan nama barang atau kegiatan. AI akan mencarikan kode klasifikasinya beserta halamannya dari dokumen Permen PUPR No 16/PRT/M/2018.")

# 2. Tarik semua teks PDF beserta penanda halamannya
teks_pdf = ekstrak_semua_teks()

user_query = st.text_input("Contoh pencarian: pengadaan semen, cuti sakit, rapat kerja")

if user_query:
    with st.spinner("AI sedang memindai ratusan halaman secara instan untuk Anda..."):
        prompt = f"""Kamu adalah asisten arsiparis ahli di Kementerian PUPR. 
        Tugasmu adalah menganalisis pertanyaan pengguna dan mencari kode klasifikasi arsip yang paling tepat berdasarkan SELURUH TEKS dokumen Permen PUPR No 16/PRT/M/2018 di bawah ini.

        IKUTI FORMAT, LOGIKA, DAN GAYA BAHASA PENJAWABAN BERIKUT SECARA KETAT:
        1. Analisis Awal: Jika kata kunci spesifik tidak disebutkan secara eksplisit di dalam klasifikasi, nyatakan hal tersebut di paragraf pertama. Kemudian, kelompokkan kata tersebut secara konseptual.
        2. Opsi Berdasarkan Konteks: Berikan beberapa pilihan kode klasifikasi yang bergantung pada TUJUAN atau KONTEKS surat/permintaan tersebut.
        3. Struktur Angka: Gunakan penomoran (1, 2, 3) untuk membedakan setiap konteks tersebut.
        4. Struktur Bullet Point: Gunakan bullet point di bawah setiap nomor urut untuk menyebutkan kodenya.
        5. Format Teks Wajib & Halaman: Kode dan nama klasifikasi HARUS ditebalkan (bold). Di akhir penjelasan pada bullet point tersebut, kamu WAJIB menyebutkan di halaman berapa kode tersebut ditemukan secara akurat.
        Contoh penulisan: **[KODE] ([Nama Klasifikasi])**: [Penjelasan detail]. *(Ditemukan di Halaman X)*.

        TEKS DOKUMEN (Terdapat penanda halaman di dalamnya):
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
