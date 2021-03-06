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
import numpy.polynomial.polynomial as poly
import numpy as np

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

dimcols = ['Dimension', 'Name', 'Unit-I', 'Unit-M']
dims = [['Distance', 'Dist', 'mi', 'km'], ['Pace', 'Pace', 'min/mi', 'min/km'], ['Elevation_Gain', 'Vert', 'ft', 'm'], 
['Average_Heart_Rate', 'Avg. HR', 'bpm', 'bpm'], ['Relative_Effort', 'Rel. Effort', '', ''], ['Average_Cadence', 'Avg. Cadence', 'spm', 'spm']]
dimensions = pd.DataFrame(data = dims, columns=dimcols)

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

#now a couple of specific comparison charts
col1, col2 = st.beta_columns(2)

col1.text('Choose two dimensions to compare to each other:')
compdims1 = col1.multiselect('What are we looking at?', ['Avg. HR', 'Pace', 'Dist', 'Vert', 'Rel. Effort', 'Avg. Cadence'], default =['Dist','Pace'], key='compCharts1')
if len(compdims1) !=2:
  col1.text('Choose precisely two options')
else:
  with col1: charting.buildComp(unitChoice, dimensions, filt, compdims1)


col2.text('Choose two dimensions to compare to each other:')
compdims2 = col2.multiselect('What are we looking at?', ['Avg. HR', 'Pace', 'Dist', 'Vert', 'Rel. Effort', 'Avg. Cadence'], default =['Vert','Pace'], key='compCharts2')
if len(compdims2) !=2:
  col2.text('Choose precisely two options')
else:
  with col2: charting.buildComp(unitChoice, dimensions, filt, compdims2)

#build pace vs. vert
