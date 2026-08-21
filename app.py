import streamlit as st
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS

# Mengambil API Key dari brankas rahasia Streamlit Cloud
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

DB_FAISS_PATH = "vectorstore/db_faiss"
# Pastikan nama file PDF sama persis dengan di GitHub!
PDF_FILE_PATH = "16_PRT_M_2018.pdf" 

@st.cache_resource
def load_or_create_database():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    if os.path.exists(DB_FAISS_PATH):
        db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
        return db
    else:
        st.info("Sedang membaca PDF dan membangun database arsip. Mohon tunggu beberapa saat...")
        loader = PyPDFLoader(PDF_FILE_PATH)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.split_documents(documents)
        
        db = FAISS.from_documents(docs, embeddings)
        db.save_local(DB_FAISS_PATH)
        st.success("Database berhasil dibangun!")
        return db

st.set_page_config(page_title="Pencari Kode Arsip", page_icon="🗂️")
st.title("🗂️ Asisten Klasifikasi Arsip PUPR")
st.markdown("Ketikkan nama barang atau kegiatan. AI akan mencarikan kode klasifikasinya dari dokumen Permen PUPR No 16/PRT/M/2018.")

# 1. Muat Database & AI
db = load_or_create_database()
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

user_query = st.text_input("Contoh pencarian: pengadaan semen, cuti sakit, rapat kerja")

if user_query:
    with st.spinner("Mencari di dalam dokumen klasifikasi..."):
        # 2. Cari bagian PDF yang paling relevan secara manual (tanpa 'chains')
        docs = db.similarity_search(user_query, k=3)
        context_teks = "\n\n".join([doc.page_content for doc in docs])
        
        # 3. Buat instruksi langsung untuk Gemini
        prompt_manual = f"""Kamu adalah asisten arsiparis profesional di Kementerian PUPR. 
        Gunakan konteks berikut untuk mencari kode klasifikasi arsip yang ditanyakan.
        Sebutkan kodenya, nama klasifikasi, dan alasan singkatnya. Jika tidak ada yang sama persis, berikan saran yang paling mendekati konsepnya.

        Konteks PDF:
        {context_teks}

        Pertanyaan Pengguna: {user_query}

        Jawaban:"""
        
        # 4. Minta Gemini menjawab
        response = llm.invoke(prompt_manual)
        
        st.markdown("### Hasil Pencarian:")
        st.write(response.content)
