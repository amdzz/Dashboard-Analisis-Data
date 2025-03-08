import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob

st.title("Analisis Polusi Udara dengan Streamlit")
st.write(
    "Analisis variasi polusi sepanjang hari dan dampak hujan terhadap polusi."
)

@st.cache_data
def load_data():
    file_list = glob.glob("./data/PRSA_Data_*.csv")

    df_list = []
    for file in file_list:
        temp_df = pd.read_csv(file)
        temp_df["station"] = file.split("_")[2]
        df_list.append(temp_df)

    df = pd.concat(df_list, ignore_index=True)
    colsToFill = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']

    for col in colsToFill:
        df[col] = df[col].fillna(df[col].mean())
    df = df.dropna(subset=['TEMP', 'PRES', 'DEWP', 'RAIN', 'wd', 'WSPM'])

    df["datetime"] = pd.to_datetime(df[["year", "month", "day"]])
    return df

df = load_data()

min_date = df["datetime"].min().date()
max_date = df["datetime"].max().date()

with st.sidebar:
    st.image("airquality.png")

    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date] 
    )

df_filtered = df[(df["datetime"] >= pd.to_datetime(start_date)) & 
                 (df["datetime"] <= pd.to_datetime(end_date))]

st.subheader("Rata-rata PM2.5 dan PM10 pada Setiap Jam")

df_hourly = df_filtered.groupby("hour")[['PM2.5', 'PM10']].mean()

fig, ax = plt.subplots(figsize=(10, 5))
df_hourly.plot(marker="o", ax=ax)
ax.set_title("Rata-rata PM2.5 dan PM10 pada Setiap Jam")
ax.set_xlabel("Jam (0-23)")
ax.set_ylabel("Konsentrasi (µg/m³)")
ax.legend(["PM2.5", "PM10"])
ax.grid()
st.pyplot(fig)

st.subheader("Rata-rata Gas Polutan Berdasarkan Kondisi Hujan")

df_filtered["Rain Category"] = df_filtered["RAIN"].apply(lambda x: "Hujan" if x > 0 else "Tidak Hujan")

df_rain = df_filtered.groupby("Rain Category")[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']].mean()

fig, ax = plt.subplots(figsize=(8, 5))
df_rain.plot(kind="bar", rot=0, ax=ax)
ax.set_title("Rata-rata Gas Polutan Berdasarkan Kondisi Hujan")
ax.set_xlabel("Kondisi Cuaca")
ax.set_ylabel("Konsentrasi (µg/m³)")
ax.legend(title="Gas Polutan")
ax.grid(axis="y")
st.pyplot(fig)

st.subheader("Korelasi antara Polutan dan Cuaca")
corr_columns = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'WSPM']
df_corr = df_filtered[corr_columns].corr()
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(df_corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, ax=ax)

st.pyplot(fig)

st.subheader("Tren Harian Polusi Tertinggi")

df_daily = df_filtered.groupby("datetime")[['PM2.5', 'PM10']].mean()

df_filtered["datetime"] = pd.to_datetime(df_filtered[["year", "month", "day", "hour"]])

df_daily = df_filtered.groupby(df_filtered["datetime"].dt.date)[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']].mean()
fig, ax = plt.subplots(figsize=(10, 5))
df_daily.plot(ax=ax, marker="o")

ax.set_title("Tren Rata-rata Harian Gas Polutan")
ax.set_xlabel("Tanggal")
ax.set_ylabel("Konsentrasi (µg/m³)")
ax.legend(["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"])
ax.grid()
plt.xticks(rotation=45)

st.pyplot(fig)


