import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ------------- KONEKSI KE GOOGLE SHEETS -------------
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials dari Streamlit Secrets
creds = Credentials.from_service_account_info(st.secrets["GCP_SERVICE_ACCOUNT"], scopes=SCOPE)
gc = gspread.authorize(creds)

# Ganti dengan ID spreadsheet kamu (contoh: '1x2y3zA4B5C6D7E8F9G0H...')
SPREADSHEET_ID = "1pr8y98ZEeA3LXEg59e-QYRbYec9F8fJAzCHVNZXiQ1k"
sheet = gc.open_by_key(SPREADSHEET_ID).sheet1

# --------- FUNGSI-FUNGSI PENGOLAHAN DATA --------------

def get_data():
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

def add_data(row):
    sheet.append_row(row)

def update_data(id_to_update, new_row):
    all_values = sheet.get_all_values()
    for i, row in enumerate(all_values):
        if str(row[0]) == str(id_to_update):  # Cek ID (kolom pertama)
            sheet.update(f'A{i+1}:F{i+1}', [new_row])
            return True
    return False

def delete_data(id_to_delete):
    all_values = sheet.get_all_values()
    for i, row in enumerate(all_values):
        if str(row[0]) == str(id_to_delete):
            sheet.delete_rows(i+1)
            return True
    return False

# ---------------- STREAMLIT UI -----------------------

st.set_page_config(page_title="Dashboard Kebiasaan Belajar", layout="wide")
st.title("📚 Dashboard Kebiasaan Belajar Mahasiswa")

menu = st.sidebar.selectbox("Menu", ["Lihat Data", "Tambah Data", "Edit Data", "Hapus Data", "Visualisasi"])
df = get_data()

if menu == "Lihat Data":
    st.subheader("Data Kebiasaan Belajar")
    st.dataframe(df)

elif menu == "Tambah Data":
    st.subheader("Tambah Data Baru")
    nama = st.text_input("Nama")
    tanggal = st.date_input("Tanggal")
    jam_belajar = st.number_input("Jam Belajar", min_value=0.5, step=0.5)
    materi = st.selectbox("Materi", ["Matematika", "Fisika", "Kimia", "Biologi", "Bahasa Inggris"])
    suasana = st.selectbox("Suasana", ["Sendiri", "Berkelompok"])

    if st.button("Tambah"):
        if not nama:
            st.warning("Nama tidak boleh kosong!")
        else:
            # Generate ID baru
            if not df.empty:
                new_id = int(df["ID"].max()) + 1
            else:
                new_id = 1
            new_row = [new_id, nama, str(tanggal), jam_belajar, materi, suasana]
            add_data(new_row)
            st.success("Data berhasil ditambahkan!")
            st.experimental_rerun()

elif menu == "Edit Data":
    st.subheader("Edit Data")
    if not df.empty:
        selected_id = st.selectbox("Pilih ID Data yang Mau Diedit", df["ID"])
        row = df[df["ID"] == selected_id].iloc[0]
        nama = st.text_input("Nama", row["Nama"])
        tanggal = st.date_input("Tanggal", pd.to_datetime(row["Tanggal"]))
        jam_belajar = st.number_input("Jam Belajar", min_value=0.5, value=float(row["Jam Belajar"]), step=0.5)
        materi = st.selectbox("Materi", ["Matematika", "Fisika", "Kimia", "Biologi", "Bahasa Inggris"], index=["Matematika", "Fisika", "Kimia", "Biologi", "Bahasa Inggris"].index(row["Materi"]))
        suasana = st.selectbox("Suasana", ["Sendiri", "Berkelompok"], index=["Sendiri", "Berkelompok"].index(row["Suasana"]))
        if st.button("Update"):
            new_row = [selected_id, nama, str(tanggal), jam_belajar, materi, suasana]
            update_data(selected_id, new_row)
            st.success("Data berhasil diupdate!")
            st.experimental_rerun()
    else:
        st.info("Data masih kosong.")

elif menu == "Hapus Data":
    st.subheader("Hapus Data")
    if not df.empty:
        selected_id = st.selectbox("Pilih ID Data yang Mau Dihapus", df["ID"])
        if st.button("Hapus"):
            delete_data(selected_id)
            st.success("Data berhasil dihapus!")
            st.experimental_rerun()
    else:
        st.info("Data masih kosong.")

elif menu == "Visualisasi":
    st.subheader("Visualisasi Data Kebiasaan Belajar")
    if not df.empty:
        st.write("Total Jam Belajar per Tanggal:")
        st.bar_chart(df.groupby("Tanggal")["Jam Belajar"].sum())

        st.write("Distribusi Materi:")
        st.bar_chart(df["Materi"].value_counts())

        st.write("Suasana Belajar:")
        st.bar_chart(df["Suasana"].value_counts())
    else:
        st.info("Data belum ada, silakan tambah data dulu.")

