import pandas as pd
import streamlit as st
from plotly import express as px
from prophet import Prophet

# Caricamento dati
@st.cache_data
def get_data(sheet=0):
    f = 'temp_humid_data.xlsx'
    df = pd.read_excel(f, sheet_name=sheet)
    date = 'time' if sheet == 0 else 'Date'
    df = df.rename(columns={date: 'Date', 'no. of Adult males': 'parasite_count'})
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df

st.set_page_config(
  page_title='Agritech Forecasting',
  page_icon=':chart_with_upwards_trend:',
  layout='wide'
)

st.title(':chart_with_upwards_trend: Agritech Forecasting :chart_with_upwards_trend:')

# Colonna sinista: Dati Anno 2022
# Colonna destra: Dati Anno 2023
left_column, right_column = st.columns(2)

with left_column:
    with st.spinner('Caricamento dati...'):
        df_left = get_data()

with right_column:
    with st.spinner('Caricamento dati...'):
        df_right = get_data(sheet=1)

# Sidebar
with st.sidebar:
    # Selezione anno per forecasting
    anno = st.selectbox(label='Seleziona un anno', options=['2022', '2023'])

    # Selezione variabile per le previsioni
    y = st.selectbox(label='Selezionare la variabile da predirre', options=['Temperatura', 'Umidità'])

    # Parametri Prophet
    st.header('Parametri Prophet')

    # Orizzonte temporale della previsione
    orizzonte = st.slider('Orizzonte della previsione (giorni)', min_value=1, max_value=365, value=90)
    # Tipologia crescita Prophet (lineare o logistica)
    crescita = st.radio(label='Crescita', options=['Lineare', 'Logistica'])
    cap_percentage = 1

    # Carrying Capacity per crescita logistica (saturazione)
    if crescita == 'Logistica' and y == 'Temperatura':
        st.info('Configura la Constant Carrying Capacity come percentuale della temperatura massima registrata')
        cap_percentage = st.slider('Constant carrying capacity', min_value=1.0, max_value=1.5, value=1.2)

    # Stagionalità
    stagionalità = st.radio(label='Stagionalità', options=['Additiva', 'Moltiplicativa'])
    
    with st.expander('Componenti stagionalità'):
        stag_settimanale = st.checkbox('Settimanale')
        stag_mensile = st.checkbox('Mensile', value=True)
        stag_annuale = st.checkbox('Annuale', value=True)

with left_column:
    st.subheader('Anno 2022 :calendar:')

    with st.expander('Mostra i dati grezzi'):
        st.dataframe(df_left, hide_index=True, use_container_width=True)

with right_column:
    st.subheader('Anno 2023 :calendar:')

    with st.expander('Mostra i dati grezzi'):
        st.dataframe(df_right, hide_index=True, use_container_width=True)

df = df_left.copy() if anno == '2022' else df_right.copy()

# Fitting del modello
with st.spinner('Model fitting..'):
    prophet_df = df.rename(columns={'Date': 'ds', 'temperature_mean' if y == 'Temperatura' else 'relativehumidity_mean': 'y'})
    model = Prophet(
                        seasonality_mode='additive' if stagionalità == 'Additiva' else 'multiplicative',
                        weekly_seasonality=stag_settimanale,
                        yearly_seasonality=stag_annuale,
                        growth='logistic' if crescita == 'Logistica' else 'linear',
                    )     
    if stag_mensile:
        model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
    if crescita == 'Logistica':
        prophet_df['cap'] = cap_percentage * df['temperature_mean' if y == 'Temperatura' else 'relativehumidity_mean'].max()
    model.fit(prophet_df)

# Previsioni
with st.spinner('Making predictions..'):
    future = model.make_future_dataframe(periods=orizzonte, freq='D')
    if crescita == 'Logistica':
        future['cap'] = cap_percentage * df['temperature_mean' if y == 'Temperatura' else 'relativehumidity_mean'].max()
    forecast = model.predict(future)

    # Clipping umidità (no umidità > 100%)
    if y == 'Umidità':
        forecast['yhat'] = forecast['yhat'].clip(upper=100)
        forecast['yhat_lower'] = forecast['yhat_lower'].clip(upper=100)
        forecast['yhat_upper'] = forecast['yhat_upper'].clip(upper=100)

# Plot del forecast
st.subheader(f'Forecasting {y} anno {anno}')

fig = px.scatter(prophet_df, x='ds', y='y', labels={'ds': 'Day', 'y': y})
fig.add_scatter(x=forecast['ds'], y=forecast['yhat'], name='yhat')
fig.add_scatter(x=forecast['ds'], y=forecast['yhat_lower'], name='yhat_lower')
fig.add_scatter(x=forecast['ds'], y=forecast['yhat_upper'], name='yhat_upper')
st.plotly_chart(fig, use_container_width=True)
