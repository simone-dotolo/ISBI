import numpy as np
import pandas as pd
import streamlit as st
import tabula

from geopy.geocoders import Nominatim
from plotly import express as px

@st.cache_data
def get_data():
  f = 'http://allegati.unina.it/studenti/tirocini/doc/ConvenzioniAttive.pdf'

  columns = [
              'Soggetto ospitante',
              'Stato',
              'Sede legale',
              'Indirizzo',
              'Prov.',
              'CAP',
              'Data stipula',
              'Scadenza'
            ]

  tables = tabula.read_pdf(f, pages='all', pandas_options={'columns' : columns})

  df = pd.concat(tables, axis=0).iloc[2:, :]
  df = df.dropna(axis=1)
  df['Sede legale'][df['Sede legale'] == '*** ESTERO'] = 'Estero'
  df['Data stipula'] = pd.to_datetime(df['Data stipula'], dayfirst=True).dt.date
  df['Scadenza'] = pd.to_datetime(df['Scadenza'], dayfirst=True).dt.date

  return df

st.set_page_config(
  page_title='UNINA Internship Scraper',
  page_icon=':earth-africa:',
  layout='wide'
)

st.title('UNINA Internship Scraper 	:earth_africa:')

with st.spinner('Caricamento dati...'):
    df = get_data()

sedi = df['Sede legale'].unique()

with st.sidebar:
  st.header('Filtri')
  sedi_selezionate = st.multiselect('Seleziona le sedi', sedi, placeholder='Seleziona le sedi',label_visibility='collapsed')

  tutte_le_sedi = st.checkbox('Seleziona tutte le sedi')

  if tutte_le_sedi:
    sedi_selezionate = sedi

  inizio_data_stipula = st.date_input('Inizio data stipula', value=pd.to_datetime(df['Data stipula'].min()).date())
  fine_data_stipula = st.date_input('Fine data stipula', value=pd.to_datetime(df['Data stipula'].max()).date())

  inizio_scadenza = st.date_input('Inizio scadenza', value=pd.to_datetime(df['Scadenza'].min()).date())
  fine_scadenza= st.date_input('Fine scadenza', value=pd.to_datetime(df['Scadenza'].max()).date())

filtered_df = df[(df['Data stipula'] >= inizio_data_stipula) & 
                 (df['Data stipula'] <= fine_data_stipula) &
                 (df['Scadenza'] >= inizio_scadenza) &
                 (df['Scadenza'] <= fine_scadenza) &
                 (df['Sede legale'].isin(sedi_selezionate))]

with st.expander('Mostra dati'):
    filtered_df.insert(0, 'Mostra su mappa', False)

    filtered_df = st.data_editor(
        filtered_df,
        column_config={'Mostra su mappa': st.column_config.CheckboxColumn(required=True)},
        hide_index=True,
        disabled=df.columns,
        use_container_width=True
    )

    sedi_selezionate = filtered_df.loc[filtered_df['Mostra su mappa'] == True]

addresses = [f'{indirizzo} {sede}' if sede != 'Estero' else indirizzo for (sede, indirizzo) in zip(sedi_selezionate['Sede legale'], sedi_selezionate['Indirizzo'])]

loc = Nominatim(user_agent="Geopy Library")

getLoc = [loc.geocode(address) for address in addresses]

map = pd.DataFrame({'lat': [location.latitude for location in getLoc if location is not None],
                    'lon': [location.longitude for location in getLoc if location is not None]})

st.header('Sedi selezionate :airplane_departure:')
st.map(map)

st.header('Locazione dei tirocini per sedi selezionate')

left_column, right_column = st.columns(2)

with left_column:
  chart = px.pie(filtered_df, 'Sede legale')
  st.plotly_chart(chart)

with right_column:
  hist = px.histogram(filtered_df, 'Sede legale')
  st.plotly_chart(hist)
