import streamlit as st 
from plotly.subplots import make_subplots
import plotly.graph_objects as go 
import plotly_express as px


#convert them to df column labels


#build out individual lines based on selected options
#amazing tds post for the px and go mixing to get the nonlinear trendlines I wanted:
#https://towardsdatascience.com/time-series-and-logistic-regression-with-plotly-and-pandas-8b368e76b19f
def multiChart(filt, chartOptions, optDict):
    chartCats = ['Activity_Date']
    for i in chartOptions:
        chartCats.append(optDict[i])

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

    if filt.empty:
        st.text('Widen the date range to select some activities!')
    elif len(chartOptions) == 0:
        st.text('Choose some options to explore!')
    else:
        st.text("Let's throw all those on a simple chart, shall we?")
        st.plotly_chart(fig , use_container_width=True)



#build chart that compares two units over time
def buildComp(unitChoice, diminfo, df, dims):
    fig = make_subplots()
    unit1 = diminfo[diminfo['Name'] == dims[0]]['Unit-I'].values[0] if unitChoice == 'Imperial' else diminfo[diminfo['Name'] == dims[0]]['Unit-M'].values[0]
    unit2 = diminfo[diminfo['Name'] == dims[1]]['Unit-I'].values[0] if unitChoice == 'Imperial' else diminfo[diminfo['Name'] == dims[1]]['Unit-M'].values[0]
    dim1 = diminfo[diminfo['Name'] == dims[0]]['Dimension'].values[0]
    dim2 = diminfo[diminfo['Name'] == dims[1]]['Dimension'].values[0]


    #hovertemplate='%{x:.1f} ' +hovUnit+' at %{y:.1f} min/'+hovUnit+'<br>On: %{text}', text=df['Activity_Date'].dt.strftime('%b %d, %Y')  ))
    fig.add_trace(go.Scatter(name='', y=df[dim2], x=df[dim1], mode='markers', hovertemplate='%{x:.1f} '+unit1+' vs %{y:.1f} '+unit2+'<br>On: %{text}', text=df['Activity_Date'].dt.strftime('%b %d, %Y')  ))

    #ud
    trend_fig = px.scatter(df, x=df[dim1], y=df[dim2], trendline="lowess")
    x_trend = trend_fig["data"][1]['x']
    y_trend = trend_fig["data"][1]['y']

    #ud
    fig.add_trace(go.Scatter(x=x_trend, y=y_trend, name=dims[0]+ ' vs '+dims[1]+ ' trend', line = dict(width=4, dash='dash'), hovertemplate='Trend: %{x:.1f} '+unit1+ ' vs %{y:.1f} '+unit2))
    colorhelp = 'rgba(0,0,0,0)'
    
    #ud
    fig.update_layout(xaxis_title=dims[0], yaxis_title=dims[1], yaxis=dict(showspikes=True, spikemode = 'marker+toaxis', spikesnap = 'cursor'), xaxis=dict(showspikes=True, spikemode = 'marker+toaxis', spikesnap = 'cursor'), margin_l=10, margin_r=10, margin_t=10, margin_b=10, hovermode='closest', showlegend=False, paper_bgcolor=colorhelp, plot_bgcolor=colorhelp)
    st.plotly_chart(fig , use_container_width=True)
