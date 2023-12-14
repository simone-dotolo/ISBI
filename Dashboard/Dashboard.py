import pandas as pd
import streamlit as st
from plotly import express as px

@st.cache_data
def get_data(sheet=0):
    f = 'temp_humid_data.xlsx'
    df = pd.read_excel(f, sheet_name=sheet)
    date = 'time' if sheet == 0 else 'Date'
    df = df.rename(columns={date: 'Date', 'no. of Adult males': 'parasite_count'})
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df

st.set_page_config(
  page_title='Agritech Dashboard',
  page_icon=':corn:',
  layout='wide'
)

st.title(':corn: Agritech Dashboard	:corn:')

left_column, right_column = st.columns(2)

with left_column:
    with st.spinner('Caricamento dati...'):
        df_left = get_data()

with right_column:
    with st.spinner('Caricamento dati...'):
        df_right = get_data(sheet=1)

with st.sidebar:
    st.header('Filtri')

    st.subheader('Prima colonna')
    data_iniziale_left = st.date_input('Data iniziale', value=pd.to_datetime(df_left['Date'].min()).date())
    data_finale_left = st.date_input('Data finale', value=pd.to_datetime(df_left['Date'].max()).date())

    range_temp_left = st.slider('Range temperatura', df_left['temperature_mean'].min(), df_left['temperature_mean'].max(), (df_left['temperature_mean'].min(), df_left['temperature_mean'].max()))
    range_umid_left = st.slider('Range umidità', df_left['relativehumidity_mean'].min(), df_left['relativehumidity_mean'].max(), (df_left['relativehumidity_mean'].min(), df_left['relativehumidity_mean'].max()))

    st.subheader('Seconda colonna')
    data_iniziale_right = st.date_input('Data iniziale', value=pd.to_datetime(df_right['Date'].min()).date())
    data_finale_right = st.date_input('Data finale', value=pd.to_datetime(df_right['Date'].max()).date())

    range_temp_right = st.slider('Range temperatura', df_right['temperature_mean'].min(), df_right['temperature_mean'].max(), (df_right['temperature_mean'].min(), df_right['temperature_mean'].max()))
    range_umid_right = st.slider('Range umidità', df_right['relativehumidity_mean'].min(), df_right['relativehumidity_mean'].max(), (df_right['relativehumidity_mean'].min(), df_right['relativehumidity_mean'].max()))

filtered_df_left = df_left[(df_left['Date'] >= data_iniziale_left) & 
                           (df_left['Date'] <= data_finale_left) &
                           (df_left['temperature_mean'] >= range_temp_left[0]) &
                           (df_left['temperature_mean'] <= range_temp_left[1]) &
                           (df_left['relativehumidity_mean'] >= range_umid_left[0]) &
                           (df_left['relativehumidity_mean'] <= range_umid_left[1])
                          ]

filtered_df_right = df_right[(df_right['Date'] >= data_iniziale_right) & 
                             (df_right['Date'] <= data_finale_right) &
                             (df_right['temperature_mean'] >= range_temp_right[0]) &
                             (df_right['temperature_mean'] <= range_temp_right[1]) &
                             (df_right['relativehumidity_mean'] >= range_umid_right[0]) &
                             (df_right['relativehumidity_mean'] <= range_umid_right[1])
                            ]
                            
with left_column:
    st.subheader('Anno 2022 :calendar:')

    st.write(f'**:thermometer: Temperatura massima: {filtered_df_left['temperature_mean'].max():.2f}°C** | **Temperatura minima: {filtered_df_left['temperature_mean'].min():.2f}°C** | **Temperatura media: {filtered_df_left['temperature_mean'].mean():.2f}°C**')
    st.write(f'**:droplet: Umidità massima: {filtered_df_left['relativehumidity_mean'].max()}%** | **Umidità minima: {filtered_df_left['relativehumidity_mean'].min()}%** | **Umidità media: {filtered_df_left['relativehumidity_mean'].mean():.0f}%**')

    with st.expander('Mostra i dati grezzi'):
        st.dataframe(filtered_df_left, hide_index=True, use_container_width=True)

    st.subheader('Andamento della temperatura media :thermometer:')
    st.line_chart(filtered_df_left.reset_index(), x='Date', y='temperature_mean', color=(120,50,50))

    st.subheader('Andamento dell\'umidità media :droplet:')
    st.line_chart(filtered_df_left.reset_index(), x='Date', y='relativehumidity_mean', color=(50,120,50))

    temp_names = ['0-5', '5-10', '10-15', '15-20', '20-25', '25-30', '30-35']
    temp_values = []

    for temp_name in temp_names:
        min_temp, max_temp = temp_name.split('-')
        temp_values.append(len(filtered_df_left[(filtered_df_left['temperature_mean']>int(min_temp)) & (filtered_df_left['temperature_mean']<=int(max_temp))]))
    temp_chart = px.pie(names=temp_names, values=temp_values)
    st.write(f'**Grafico a torta della temperatura :thermometer:**')
    st.plotly_chart(temp_chart)

    humidity_names = ['0-10', '10-20', '20-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90-100']
    humidity_values = []

    for humidity_name in humidity_names:
        min_humidity, max_humidity = humidity_name.split('-')
        humidity_values.append(len(filtered_df_left[(filtered_df_left['relativehumidity_mean']>int(min_humidity)) & (filtered_df_left['relativehumidity_mean']<=int(max_humidity))]))
    humidity_chart = px.pie(names=humidity_names, values=humidity_values)
    st.write(f'**Grafico a torta dell\' umidità :droplet:**')
    st.plotly_chart(humidity_chart)

with right_column:
    st.subheader('Anno 2023 :calendar:')

    st.write(f'**:thermometer: Temperatura massima: {filtered_df_right['temperature_mean'].max():.2f}°C** | **Temperatura minima: {filtered_df_right['temperature_mean'].min():.2f}°C** | **Temperatura media: {filtered_df_right['temperature_mean'].mean():.2f}°C**')
    st.write(f'**:droplet: Umidità massima: {filtered_df_right['relativehumidity_mean'].max()}%** | **Umidità minima: {filtered_df_right['relativehumidity_mean'].min()}%** | **Umidità media: {filtered_df_right['relativehumidity_mean'].mean():.0f}%**')

    with st.expander('Mostra i dati grezzi'):
        st.dataframe(filtered_df_right, hide_index=True, use_container_width=True)

    st.subheader('Andamento della temperatura media :thermometer:')
    st.line_chart(filtered_df_right.reset_index(), x='Date', y='temperature_mean', color=(120,50,50))

    st.subheader('Andamento dell\'umidità media :droplet:')
    st.line_chart(filtered_df_right.reset_index(), x='Date', y='relativehumidity_mean', color=(50,120,50))

    temp_names = ['0-5', '5-10', '10-15', '15-20', '20-25', '25-30', '30-35']
    temp_values = []

    for temp_name in temp_names:
        min_temp, max_temp = temp_name.split('-')
        temp_values.append(len(filtered_df_right[(filtered_df_right['temperature_mean']>int(min_temp)) & (filtered_df_right['temperature_mean']<=int(max_temp))]))
    temp_chart = px.pie(names=temp_names, values=temp_values)
    st.write(f'**Grafico a torta della temperatura :thermometer:**')
    st.plotly_chart(temp_chart)

    humidity_names = ['0-10', '10-20', '20-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90-100']
    humidity_values = []

    for humidity_name in humidity_names:
        min_humidity, max_humidity = humidity_name.split('-')
        humidity_values.append(len(filtered_df_right[(filtered_df_right['relativehumidity_mean']>int(min_humidity)) & (filtered_df_right['relativehumidity_mean']<=int(max_humidity))]))
    humidity_chart = px.pie(names=humidity_names, values=humidity_values)
    st.write(f'**Grafico a torta dell\' umidità :droplet:**')
    st.plotly_chart(humidity_chart)

st.subheader('Andamento dei parassiti anno 2023 :cockroach:')
st.bar_chart(filtered_df_right.reset_index(), x='Date', y='parasite_count')