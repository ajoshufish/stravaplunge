import pandas as pd 
import streamlit as st 
import os
from datetime import datetime
import plotly.express as px

#pd.options.plotting.backend = "plotly"

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
df['Activity_Date'] = pd.to_datetime(df['Activity_Date'])

#Option Selection
actType = st.sidebar.radio('Activity Type',['Run','Bike'])
startDay = st.sidebar.slider('Start Date', value=datetime(2020, 7, 30),format="MM/DD/YY", min_value=datetime(2020,3,1), max_value=datetime(2021,2,2))
endDay = st.sidebar.slider('End Date', value=datetime(2020, 10, 30),format="MM/DD/YY", min_value=datetime(2020,3,1), max_value=datetime(2021,2,3))
#unitChoice = st.sidebar.radio('Units', ['Imperial','Metric'])

#Apply our options
filt = df[(df.Activity_Date >= startDay) & (df.Activity_Date <= endDay) & (df.Activity_Type == actType)]
st.dataframe(filt)

#Collect together options for our line graph
optDict = {'Avg. HR':'Average_Heart_Rate', 'Avg. Pace':'Average_Speed', 'Dist':'Distance', 'Vert':'Elevation_Gain', 'Rel. Effort':'Relative_Effort'}
chartOptions = st.multiselect('What are we looking at?', ['Avg. HR', 'Avg. Pace', 'Dist', 'Vert', 'Rel. Effort'], default =['Dist','Avg. Pace'])

#convert them to df column labels
chartCats = []
for i in chartOptions:
    chartCats.append(optDict[i])

fig = px.line(filt[chartCats])
st.plotly_chart(fig)
#st.line_chart(filt[chartCats])
#st.dataframe(df.dtypes)