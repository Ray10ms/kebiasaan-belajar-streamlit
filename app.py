import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import time
import re
from datetime import date

# ------------- KONEKSI KE GOOGLE SHEETS -------------
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials dari Streamlit Secrets
creds = Credentials.from_service_account_info(st.secrets["GCP_SERVICE_ACCOUNT"], scopes=SCOPE)
gc = gspread.authorize(creds)

#ID spreadsheet
SPREADSHEET_ID = "1pr8y98ZEeA3LXEg59e-QYRbYec9F8fJAzCHVNZXiQ1k"
sheet = gc.open_by_key(SPREADSHEET_ID).sheet1

# === CSS SETUP ===
st.set_page_config(page_title="Dashboard Kebiasaan Belajar", page_icon="📚", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f4f6fb; }
    .stButton > button {
        background: linear-gradient(90deg, #355C7D 0%, #6C5B7B 100%);
        color: white; font-weight: bold; border-radius: 8px; border: none;
        padding: 0.5em 2em; margin-bottom: 1em;
    }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    h1, h2, h3, h4 { font-family: 'Montserrat', sans-serif; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


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
        if str(row[0]) == str(id_to_update):  # Cek ID 
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
def parse_jam_belajar(s):
    jam = 0
    menit = 0
    if "jam" in s:
        match = re.search(r'(\d+)\s*jam', s)
        if match:
            jam = int(match.group(1))
    if "menit" in s:
        match = re.search(r'(\d+)\s*menit', s)
        if match:
            menit = int(match.group(1))
    return jam + menit / 60
def split_jam_menit(jam_belajar_str):
    jam = 0
    menit = 0
    if "jam" in jam_belajar_str:
        match = re.search(r'(\d+)\s*jam', jam_belajar_str)
        if match:
            jam = int(match.group(1))
    if "menit" in jam_belajar_str:
        match = re.search(r'(\d+)\s*menit', jam_belajar_str)
        if match:
            menit = int(match.group(1))
    return jam, menit

# ---------------- STREAMLIT UI -----------------------

st.set_page_config(page_title="Dashboard Kebiasaan Belajar", layout="wide")
st.title("📚 Dashboard Kebiasaan Belajar Mahasiswa")

menu = st.sidebar.selectbox("Menu", ["Lihat Data", "Tambah Data", "Edit Data", "Hapus Data", "Visualisasi"])
df = get_data()
df["JamBelajarFloat"] = df["Jam Belajar"].astype(str).apply(parse_jam_belajar)

## === UI MODERN ===
# === HEADER DASHBOARD ===
st.markdown("<h1 style='text-align: center;'>📚 Dashboard Kebiasaan Belajar Mahasiswa</h1>", unsafe_allow_html=True)
st.markdown("#### 🎯 <span style='color:#6C5B7B'>Data & Insight Kebiasaan Belajar</span>", unsafe_allow_html=True)
st.markdown("---")

# === STATISTIK CEPAT (Cards) ===
col1, col2, col3 = st.columns(3)
col1.metric("👥 Jumlah Siswa", df["Nama"].nunique())
col2.metric("📅 Jumlah Hari", df["Tanggal"].nunique())
col3.metric("⏰ Total Jam Belajar", f"{df['JamBelajarFloat'].sum():.1f} jam")

st.markdown("---")

# === TABEL DATA UTAMA ===
st.markdown("### 🗂️ Data Tabel")
st.dataframe(df.drop(columns=["JamBelajarFloat"]).reset_index(drop=True), use_container_width=True)

st.markdown("---")

# === VISUALISASI ALTAR MODERN ===
st.markdown("### 📈 Grafik Line Total Jam Belajar per Tanggal")
line_chart = alt.Chart(df).mark_line(point=alt.OverlayMarkDef(color="#6C5B7B")).encode(
    x=alt.X('Tanggal:T', title='Tanggal'),
    y=alt.Y('JamBelajarFloat:Q', title='Total Jam Belajar (jam)'),
    tooltip=['Tanggal', alt.Tooltip('JamBelajarFloat', format=".2f")]
).properties(width=900, height=350)
st.altair_chart(line_chart, use_container_width=True)

st.markdown("### 🎨 Pie Chart Distribusi Materi")
materi_counts = df["Materi"].value_counts().reset_index()
materi_counts.columns = ["Materi", "Jumlah"]
pie = alt.Chart(materi_counts).mark_arc(innerRadius=60).encode(
    theta=alt.Theta(field="Jumlah", type="quantitative"),
    color=alt.Color(field="Materi", type="nominal"),
    tooltip=["Materi", "Jumlah"]
)
st.altair_chart(pie, use_container_width=True)

# === BONUS: Visualisasi Suasana ===
st.markdown("### 👥 Distribusi Suasana Belajar")
suasana_counts = df["Suasana"].value_counts().reset_index()
suasana_counts.columns = ["Suasana", "Jumlah"]
bar = alt.Chart(suasana_counts).mark_bar(size=50, cornerRadiusTopLeft=10, cornerRadiusTopRight=10).encode(
    x=alt.X('Suasana', sort=None),
    y='Jumlah',
    color='Suasana',
    tooltip=['Suasana', 'Jumlah']
)
st.altair_chart(bar, use_container_width=True)

st.markdown("---")
st.markdown("<center><sub>Made with 💜 by Em Rayi </sub></center>", unsafe_allow_html=True)

if menu == "Lihat Data":
    st.subheader("Data Kebiasaan Belajar")
    st.dataframe(df.reset_index(drop=True))


elif menu == "Tambah Data":
    st.subheader("Tambah Data Baru")
    nama = st.text_input("Nama")
    tanggal = st.date_input("Tanggal")
    jam = st.number_input("Jam", min_value=0, max_value=12, step=1)
    menit = st.number_input("Menit", min_value=0, max_value=59, step=1)
    materi = st.selectbox("Materi", ["Matematika", "Fisika", "Kimia", "Biologi", "Bahasa Inggris"])
    suasana = st.selectbox("Suasana", ["Sendiri", "Berkelompok"])

    if st.button("Tambah"):
        if not nama:
            st.warning("Nama tidak boleh kosong!")
        elif jam == 0 and menit == 0:
            st.warning("Minimal harus isi jam atau menit!")
        else:
            if jam > 0 and menit > 0:
                jam_belajar_str = f"{int(jam)} jam {int(menit)} menit"
            elif jam > 0:
                jam_belajar_str = f"{int(jam)} jam"
            elif menit > 0:
                jam_belajar_str = f"{int(menit)} menit"
            else:
                jam_belajar_str = "0 menit"

            tanggal_str = tanggal.strftime('%Y-%m-%d') if hasattr(tanggal, 'strftime') else str(tanggal)
            
            if "ID" in df.columns and not df.empty:
                try:
                    new_id = int(df["ID"].astype(int).max()) + 1
                except Exception:
                    new_id = 1
            else:
                new_id = 1

            st.write(f"ID Baru: {new_id}")
            
            new_row = [
                int(new_id),
                str(nama),
                tanggal_str,
                jam_belajar_str,
                str(materi),
                str(suasana)
            ]
            add_data(new_row)
            st.success("Data berhasil ditambahkan!")
            time.sleep(2)
            st.rerun()
elif menu == "Edit Data":
    st.subheader("Edit Data")
    if not df.empty:
        selected_id = st.selectbox("Pilih ID Data yang Mau Diedit", df["ID"])
        row = df[df["ID"] == selected_id].iloc[0]
        nama = st.text_input("Nama", row["Nama"])
        tanggal = st.date_input("Tanggal", pd.to_datetime(row["Tanggal"]))

        # Ambil jam & menit dari string di kolom 'Jam Belajar'
        jam_lama, menit_lama = split_jam_menit(str(row["Jam Belajar"]))

        jam = st.number_input("Jam", min_value=0, max_value=12, step=1, value=jam_lama)
        menit = st.number_input("Menit", min_value=0, max_value=59, step=1, value=menit_lama)
        materi = st.selectbox("Materi", ["Matematika", "Fisika", "Kimia", "Biologi", "Bahasa Inggris"],
                              index=["Matematika", "Fisika", "Kimia", "Biologi", "Bahasa Inggris"].index(row["Materi"]))
        suasana = st.selectbox("Suasana", ["Sendiri", "Berkelompok"],
                               index=["Sendiri", "Berkelompok"].index(row["Suasana"]))

        if st.button("Update"):
            if not nama:
                st.warning("Nama tidak boleh kosong!")
            elif jam == 0 and menit == 0:
                st.warning("Minimal harus isi jam atau menit!")
            else:
                # Gabungkan jam & menit jadi string
                if jam > 0 and menit > 0:
                    jam_belajar_str = f"{int(jam)} jam {int(menit)} menit"
                elif jam > 0:
                    jam_belajar_str = f"{int(jam)} jam"
                elif menit > 0:
                    jam_belajar_str = f"{int(menit)} menit"
                else:
                    jam_belajar_str = "0 menit"

                new_row = [selected_id, nama, str(tanggal), jam_belajar_str, materi, suasana]
                update_data(selected_id, new_row)
                st.success("Data berhasil diupdate!")
                time.sleep(2)
                st.rerun()
    else:
        st.info("Data masih kosong.")

elif menu == "Hapus Data":
    st.subheader("Hapus Data")
    if not df.empty:
        selected_id = st.selectbox("Pilih ID Data yang Mau Dihapus", df["ID"])
        if st.button("Hapus"):
            delete_data(selected_id)
            st.success("Data berhasil dihapus!")
            time.sleep(5)    # Tampilkan notifikasi selama 5 detik
            st.rerun()       # Refresh halaman
    else:
        st.info("Data masih kosong.")


elif menu == "Visualisasi":
    st.subheader("Visualisasi Data Kebiasaan Belajar")
    if not df.empty:
        df["JamBelajarFloat"] = df["Jam Belajar"].astype(str).apply(parse_jam_belajar)
        st.write("Total Jam Belajar per Tanggal:")
        st.line_chart(df.groupby("Tanggal")["JamBelajarFloat"].sum())

        st.write("Distribusi Materi:")
        st.line_chart(df["Materi"].value_counts())

        st.write("Suasana Belajar:")
        st.line_chart(df["Suasana"].value_counts())
    else:
        st.info("Data belum ada, silakan tambah data dulu.")

