import pandas as pd 
import streamlit as st 
from datetime import datetime
import os
import plotly.graph_objects as go 
from plotly.subplots import make_subplots
import plotly_express as px
import gspread

st.set_page_config(layout='wide')
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

st.write(df.dtypes)


#Option Selection
startDay = st.sidebar.slider('Start Date', value=datetime(2020, 3, 12),format="MM/DD/YY", min_value=datetime(2020, 3, 12), max_value=datetime(2021, 2, 1))
endDay = st.sidebar.slider('End Date', value=datetime(2021, 1, 30),format="MM/DD/YY", min_value=datetime(2020, 3, 13), max_value=datetime(2021, 2, 1) )

#We can switch to these to give us the full range of activities
#startDay = st.sidebar.slider('Start Date', value=datetime(2020, 2, 1),format="MM/DD/YY", min_value=df.head(1)['Activity_Date'].iloc[0].to_pydatetime(), max_value=df.tail(1)['Activity_Date'].iloc[0].to_pydatetime())
#endDay = st.sidebar.slider('End Date', value=datetime(2021, 1, 30),format="MM/DD/YY", min_value=df.head(1)['Activity_Date'].iloc[0].to_pydatetime(), max_value=df.tail(1)['Activity_Date'].iloc[0].to_pydatetime() )

unitChoice = st.sidebar.radio('Units', ['Imperial','Metric'])  #strava backend is metric so at some point we'll need to convert stuff

#Apply our options
filt = df[(df.Activity_Date >= startDay) & (df.Activity_Date <= endDay) & (df.Activity_Type == 'Run')]
filt.sort_values(by='Activity_Date')
if unitChoice == 'Imperial':
    filt['Distance'] = .621371 * filt['Distance'] #km to mi
    filt['Pace'] = 1.60934449789 * filt['Pace'] #min/km to min/mi
    filt['Elevation_Gain'] = 3.28084 * filt['Elevation_Gain']


st.dataframe(filt)

#Collect together options for our line graph
optDict = {'Avg. Cadence':'Average_Cadence','Avg. HR':'Average_Heart_Rate', 'Avg. Pace':'Pace', 'Dist':'Distance', 'Vert':'Elevation_Gain', 'Rel. Effort':'Relative_Effort'}
chartOptions = st.multiselect('What are we looking at?', ['Avg. HR', 'Avg. Pace', 'Dist', 'Vert', 'Rel. Effort', 'Avg. Cadence'], default =['Dist','Avg. Pace'])

#convert them to df column labels
chartCats = ['Activity_Date']
for i in chartOptions:
    chartCats.append(optDict[i])

#build out individual lines based on selected options
#amazing tds post for the px and go mixing to get the nonlinear trendlines I wanted:
#https://towardsdatascience.com/time-series-and-logistic-regression-with-plotly-and-pandas-8b368e76b19f
def makeChart():
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for i in enumerate(chartOptions):
        if (i[1] == 'Vert') or (i[1] == 'Avg. HR'):
            fig.add_trace(go.Scatter(name=i[1], y=filt[optDict[i[1]]], x=filt['Activity_Date']), secondary_y=False)
        else:
            fig.add_trace(go.Scatter(name=i[1], y=filt[optDict[i[1]]], x=filt['Activity_Date']), secondary_y=True)
        trend_fig = px.scatter(filt, x=filt['Activity_Date'], y=filt[optDict[i[1]]], trendline="lowess")
        x_trend = trend_fig["data"][1]['x']
        y_trend = trend_fig["data"][1]['y']
        fig.add_trace(go.Scatter(x=x_trend, y=y_trend, name=i[1]+' trend', line = dict(width=4, dash='dash')))

    #tidy up some display options and display the compiled chart
    colorhelp = 'rgba(0,0,0,0)'
    fig.update_layout(margin_l=10, margin_r=10, margin_t=10, margin_b=10, hovermode='x', showlegend=True, paper_bgcolor=colorhelp, plot_bgcolor=colorhelp)
    return fig

#Let's show the chart....assuming we chose options properly
if filt.empty:
    st.text('Widen the date range to select some activities!')
elif len(chartOptions) == 0:
    st.text('Choose some options to explore!')
else:
    chart = makeChart()
    st.text("Let's throw all those on a simple chart, shall we?")
    st.plotly_chart(chart , use_container_width=True)



