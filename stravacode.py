import pandas as pd 
import streamlit as st 
from datetime import datetime
import os
import gspread
st.set_page_config(layout='wide')
import charting
from plotly.subplots import make_subplots
import plotly.graph_objects as go 
import plotly_express as px

st.title('Strava Aggregated Data Analysis -- one user: me!')

#setup data load config based on streamlit secrets
credentials = {
  "type": st.secrets["type"],
  "project_id": st.secrets["project_id"],
  "private_key_id": st.secrets["private_key_id"],
  "private_key": st.secrets["private_key"],
  "client_email": st.secrets["client_email"],
  "client_id": st.secrets["client_id"],
  "auth_uri": st.secrets["auth_uri"],
  "token_uri": st.secrets["token_uri"],
  "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
  "client_x509_cert_url": st.secrets["client_x509_cert_url"]
  }
sheetKey = st.secrets["worksheet_key"]
dbSheet = st.secrets["sheet"]

#Load up all our data
@st.cache(allow_output_mutation=True)
def load_dataset():
   gc = gspread.service_account_from_dict(credentials)
   ws = gc.open_by_key(sheetKey).worksheet(dbSheet)
   return ws.get_all_records()

data = load_dataset()
headers = data.pop(0)
df = pd.DataFrame(data, columns=headers)

#tidy up column info
df.columns = df.columns.str.replace(' ', '_')
df = df.convert_dtypes()
df['Activity_Date'] = pd.to_datetime(df['Activity_Date'])
df = df.sort_values(by='Activity_Date')
df['Distance'] = pd.to_numeric(df['Distance'])
df['Elapsed_Time'] = pd.to_numeric(df['Elapsed_Time'])
df['Elevation_Gain'] = pd.to_numeric(df['Elevation_Gain'])
df['Relative_Effort'] = pd.to_numeric(df['Relative_Effort'])
df['Average_Heart_Rate'] = pd.to_numeric(df['Average_Heart_Rate'])
df['Average_Cadence'] = pd.to_numeric(df['Average_Cadence'])
df['Elapsed_Time'] = df['Elapsed_Time'] /60 #convert s to min
df['Average_Speed'] = df['Distance']/df['Elapsed_Time'] #fill in blanks
df['Distance'] = df['Distance'] / 1000 #convert m to km
df['Pace'] = df['Elapsed_Time']/df['Distance'] #min/km

#st.write(df.dtypes)


#Option Selection
startDay = st.sidebar.slider('Start Date', value=datetime(2020, 3, 12),format="MM/DD/YY", min_value=datetime(2020, 3, 12), max_value=datetime(2021, 2, 1))
endDay = st.sidebar.slider('End Date', value=datetime(2021, 1, 30),format="MM/DD/YY", min_value=datetime(2020, 3, 13), max_value=datetime(2021, 2, 1) )
unitChoice = st.sidebar.radio('Units', ['Imperial','Metric'])  #strava backend is metric so at some point we'll need to convert stuff

#We can switch to these to give us the full range of activities
#startDay = st.sidebar.slider('Start Date', value=datetime(2020, 2, 1),format="MM/DD/YY", min_value=df.head(1)['Activity_Date'].iloc[0].to_pydatetime(), max_value=df.tail(1)['Activity_Date'].iloc[0].to_pydatetime())
#endDay = st.sidebar.slider('End Date', value=datetime(2021, 1, 30),format="MM/DD/YY", min_value=df.head(1)['Activity_Date'].iloc[0].to_pydatetime(), max_value=df.tail(1)['Activity_Date'].iloc[0].to_pydatetime() )


#Apply our options
filt = df[(df.Activity_Date >= startDay) & (df.Activity_Date <= endDay) & (df.Activity_Type == 'Run')]
filt.sort_values(by='Activity_Date')
if unitChoice == 'Imperial':
    filt['Distance'] = .621371 * filt['Distance'] #km to mi
    filt['Pace'] = 1.60934449789 * filt['Pace'] #min/km to min/mi
    filt['Elevation_Gain'] = 3.28084 * filt['Elevation_Gain']

optDict = {'Avg. Cadence':'Average_Cadence','Avg. HR':'Average_Heart_Rate', 'Avg. Pace':'Pace', 'Dist':'Distance', 'Vert':'Elevation_Gain', 'Rel. Effort':'Relative_Effort'}
chartOptions = st.multiselect('What are we looking at?', ['Avg. HR', 'Avg. Pace', 'Dist', 'Vert', 'Rel. Effort', 'Avg. Cadence'], default =['Dist','Avg. Pace'])

#call our chart, passing in options
charting.multiChart(filt, chartOptions, optDict)

col1, col2 = st.beta_columns(2)

#build pace vs. distance
fig = make_subplots()
fig.add_trace(go.Scatter(name='', y=filt['Pace'], x=filt['Distance'], mode='markers', hovertemplate='%{x:.1f} mi at %{y:.1f} min/mi<br>On: %{text}', text=filt['Activity_Date'].dt.strftime('%b %d, %Y')  ))

trend_fig = px.scatter(filt, x=filt['Distance'], y=filt['Pace'], trendline="lowess")
x_trend = trend_fig["data"][1]['x']
y_trend = trend_fig["data"][1]['y']

fig.add_trace(go.Scatter(x=x_trend, y=y_trend, name='Pace'+ ' trend', line = dict(width=4, dash='dash'), hovertemplate='Trend: %{y:.1f} min/mi for %{x:.1f} mi'))
colorhelp = 'rgba(0,0,0,0)'
fig.update_layout(xaxis_title="Distance (mi)", yaxis_title='Pace (min/mi)', yaxis=dict(showspikes=True, spikemode = 'marker+toaxis', spikesnap = 'cursor'), xaxis=dict(showspikes=True, spikemode = 'marker+toaxis', spikesnap = 'cursor'), margin_l=10, margin_r=10, margin_t=10, margin_b=10, hovermode='closest', showlegend=False, paper_bgcolor=colorhelp, plot_bgcolor=colorhelp)

col1.text('For these data, how does distance translate to pace? \nAnything below the trend line beats the average (good!).')
col1.plotly_chart(fig , use_container_width=True)

#build pace vs. vert
fig = make_subplots()
fig.add_trace(go.Scatter(name='', y=filt['Pace'], x=filt['Elevation_Gain'], mode='markers', hovertemplate='%{x} ft at %{y:.1f} min/mi<br>On: %{text}', text=filt['Activity_Date'].dt.strftime('%b %d, %Y')  ))

trend_fig = px.scatter(filt, x=filt['Elevation_Gain'], y=filt['Pace'], trendline="lowess")
x_trend = trend_fig["data"][1]['x']
y_trend = trend_fig["data"][1]['y']

fig.add_trace(go.Scatter(x=x_trend, y=y_trend, name='Pace'+ ' trend', line = dict(width=4, dash='dash'), hovertemplate='Trend: %{y:.1f} min/mi for %{x} ft'))
colorhelp = 'rgba(0,0,0,0)'
fig.update_layout(xaxis_title="Vert (ft)", yaxis_title='Pace (min/mi)', yaxis=dict(showspikes=True, spikemode = 'marker+toaxis', spikesnap = 'cursor'), xaxis=dict(showspikes=True, spikemode = 'marker+toaxis', spikesnap = 'cursor'), margin_l=10, margin_r=10, margin_t=10, margin_b=10, hovermode='closest', showlegend=False, paper_bgcolor=colorhelp, plot_bgcolor=colorhelp)

col2.text('For these data, how does elevation gain translate to pace? \nAnything below the trend line beats the average (good!).')
col2.plotly_chart(fig , use_container_width=True)