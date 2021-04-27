import pandas as pd 
import streamlit as st 
import os
from datetime import datetime

pd.options.plotting.backend = "plotly"

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
unitChoice = st.sidebar.radio('Units', ['Imperial','Metric'])

#Apply our options
filt = df[(df.Activity_Date >= startDay) & (df.Activity_Date <= endDay) & (df.Activity_Type == actType)]

st.dataframe(filt)

st.multiselect('What are we looking at?', ['HR', 'Pace', 'Dist', 'Vert', 'Rel Effort'])

#st.dataframe(df.dtypes)
