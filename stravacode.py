import pandas as pd 
import streamlit as st 
from datetime import datetime
import os
import plotly.graph_objects as go 
from plotly.subplots import make_subplots
import plotly_express as px

st.set_page_config(layout='wide')
st.title('Strava Data Analysis -- one user: me!')

#Load up all our data
@st.cache(allow_output_mutation=True)
def load_dataset():
    filefold = os.path.dirname(os.path.abspath(__file__))
    datapath = os.path.join(filefold, 'activities.csv')
    return pd.read_csv(datapath)
df = load_dataset()

#tidy up column info
df.columns = df.columns.str.replace(' ', '_')
df = df.sort_values(by='Activity_Date')
df['Activity_Date'] = pd.to_datetime(df['Activity_Date'])
df['Average_Speed'] = df['Distance.1']/df['Moving_Time']

#Option Selection
startDay = st.sidebar.slider('Start Date', value=datetime(2020, 7, 30),format="MM/DD/YY", min_value=df.head(1)['Activity_Date'].iloc[0].to_pydatetime(), max_value=df.tail(1)['Activity_Date'].iloc[0].to_pydatetime())
endDay = st.sidebar.slider('End Date', value=datetime(2020, 10, 30),format="MM/DD/YY", min_value=df.head(1)['Activity_Date'].iloc[0].to_pydatetime(), max_value=df.tail(1)['Activity_Date'].iloc[0].to_pydatetime() )
#unitChoice = st.sidebar.radio('Units', ['Imperial','Metric'])  #strava backend is metric so at some point we'll need to convert stuff

#Apply our options
filt = df[(df.Activity_Date >= startDay) & (df.Activity_Date <= endDay) & (df.Activity_Type == 'Run')]
filt.sort_values(by='Activity_Date')
st.dataframe(filt)

#Collect together options for our line graph
optDict = {'Avg. HR':'Average_Heart_Rate', 'Avg. Pace':'Average_Speed', 'Dist':'Distance', 'Vert':'Elevation_Gain', 'Rel. Effort':'Relative_Effort'}
chartOptions = st.multiselect('What are we looking at?', ['Avg. HR', 'Avg. Pace', 'Dist', 'Vert', 'Rel. Effort'], default =['Dist','Avg. Pace'])

#convert them to df column labels
chartCats = ['Activity_Date']
for i in chartOptions:
    chartCats.append(optDict[i])

fig = make_subplots(specs=[[{"secondary_y": True}]])

#build out individual lines based on selected options
#amazing tds post for the px and go mixing to get the nonlinear trendlines I wanted:
#https://towardsdatascience.com/time-series-and-logistic-regression-with-plotly-and-pandas-8b368e76b19f

for i in enumerate(chartOptions):
    if i[1] == 'Vert':
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
st.text("Let's throw all those on a simple chart, shall we?")
st.plotly_chart(fig , use_container_width=True)

#st.line_chart(filt[chartCats[1:]])
#st.dataframe(df.dtypes)
