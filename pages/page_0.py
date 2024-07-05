import streamlit as st
import plotly.figure_factory as ff
import plotly.express as px
import pandas as pd
import streamlit_authenticator as stauth
from streamlit_extras.stylable_container import stylable_container 
from streamlit_extras.metric_cards import style_metric_cards
import warnings
from streamlit_extras.switch_page_button import switch_page
import plotly.io as pio
import os
import requests
from support import check_and_download_file, client


## Page 1 -  number of offender id and race not maching, all values for county of sentence is not san bernardino, remove nans from cdcr data, add conviction filter to filed charges

# Page config and data
pio.templates.default = 'plotly' 
warnings.filterwarnings('ignore')
st.set_page_config(layout="wide")
color = {'Unknown/Other':'#3a393a', 'Black or African American': '#2993A3', 'White':'#666766', 'Native American':'#f4b780', 'Hispanic':'#a0cd7c', 'Pacific Islander':'#a680ba','Asian':'#f37e85'}

#----------------------------NavBar-------------------------------#
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

if st.session_state.get("logged_in") == False or st.session_state.get("logged_in") == None:
    st.switch_page("app.py")

Pagex = st.container(border=True)
Pagex = stylable_container(key="Pagex", css_styles=[""" {box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 25px; background-color: #3498DB;  position: fixed;
  top: 0%;
  height:60px;z-index: 1000;}"""])

m = st.markdown("""
<style>
div.stButton > button:first-child {
padding: 0;
border: none;
background: none;
color: white;
}
</style>""", unsafe_allow_html=True)

cols = Pagex.columns([0.01, 0.1,0.1, 0.1,0.1,0.1,0.1,0.2,0.09,0.1])

if cols[1].button("Arrest Summary"):
    st.switch_page("pages/page_0.py")
if cols[3].button("Charge By Race"):
    st.switch_page("pages/page_1.py")
if cols[5].button("Download Data"):
    st.switch_page("pages/page_2.py")
if cols[9].button("Logout", key=4):
    #st.session_state['auth'].logout()
    st.switch_page("app.py")

#------------------------------- Metric Cards ------------------------#

file_path = "Population.csv"
check_and_download_file(file_path)

pop = pd.read_csv("Population.csv")
cols = st.columns(2)
cols[0].metric(label="Felony Convicitons for the Population (2015-2023)", value=32979, delta='inc')
v = int(pop.loc[0, pop.columns.str.contains("Black")].values[0]) / int(pop.loc[0, pop.columns.str.contains("White")].values[0])
cols[1].metric(label="Black : White Population ratio", value=str(round(v*100, 2))+"/100", delta = "As per 2020")
style_metric_cards()

#------------------------------- Page 0 ------------------------------#
Page0 = st.container(border=True)
Page0 = stylable_container(key="Page0", css_styles=[""" {box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 25px;}"""])#, """{background-color:white;opacity:0.8;}"""])#, """  {border: 2px solid rgba(49, 51, 63, 0.2); border-radius: 10px;}"""])

cols = Page0.columns([0.5,5.5,0.2,3.3,0.5])
cols[1].header("Most Common Charges Filed in the County", anchor='section-1', help="A Graph to understrand the most commnly charged crimes in the county by racial distribution. The graph gives a yearly estimates of the crimes. You can choose to see the data by Race/Race and see upto top 300.")

cols = Page0.columns([0.5,3, 3,3,0.5])
Race = cols[1].selectbox('Select Race', tuple(color.keys()), index=None)
Dec = cols[2].selectbox('Change Data', tuple(['Filing Data', 'Curently Incarcerated']), index=0)

st.markdown("""
    <style>
    .stSlider [data-baseweb=slider]{
        width: 100%;
    }
    </style>
    """,unsafe_allow_html=True)
timeline = cols[3].slider('Select Timeline for Cases', 1990, 2022, (2015,2021))

cols = Page0.columns([6.5,3.5])

file_path = "Court_appA.csv"
check_and_download_file(file_path)

file_path = "Court_appB.csv"
check_and_download_file(file_path)

file_path = "Incarceration_appA.csv"
check_and_download_file(file_path)

file_path = "Incarceration_appB.csv"
check_and_download_file(file_path)

if Race != None:
    df1 = pd.read_csv("Court_appA.csv") if Dec == 'Filing Data' else pd.read_csv("Incarceration_appA.csv")
    df1 = df1[df1['Race'] == Race]
    df1 = df1[(df1['year'] >= timeline[0]) & (df1['year'] <= timeline[1])]
    df1 = df1[['Charges', 'Race', 'count']].groupby('Charges').agg({'count':'sum'}).reset_index()
    df1['count'] = (df1['count'] / (timeline[1] - timeline[0])) if timeline[1] != timeline[0] else df1['count']
    df1 = df1.sort_values('count')
    fig = px.bar(pd.DataFrame(df1[-40:]), y='Charges', x='count', orientation='h')
    fig.update_traces(marker_color=color[Race])
else:
    df1 = pd.read_csv("Court_appB.csv") if Dec == 'Filing Data' else pd.read_csv("Incarceration_appB.csv")

    df1 = df1[(df1['year'] >= timeline[0]) & (df1['year'] <= timeline[1])]
    df1 = df1[['Charges', 'Race', 'count']].groupby(['Charges','Race']).agg({'count':'sum'}).reset_index()
    df1['count'] = (df1['count'] / (timeline[1] - timeline[0])) if timeline[1] != timeline[0] else df1['count']
    df1 = df1.sort_values(['Charges', 'count'])
    fig = px.bar(df1, y='Charges', x='count', orientation='h', color_discrete_map=color, color='Race')
    fig.update_layout(barmode='stack', yaxis={'categoryorder':'total ascending'})

if Dec == 'Court Data':
  fig.update_layout(width=900, height=900, xaxis = {'side':'top'},title_y=0.99, xaxis_title="Number of Cases Per Year", yaxis_title="Charges")
else:
   fig.update_layout(width=900, height=900, xaxis = {'side':'top'},title_y=0.99, xaxis_title="Total Cases", yaxis_title="Charges")

fig.update_layout(legend=dict(yanchor="top", y=0.7, xanchor="left", x=0.6)) 

cols[0].plotly_chart(fig, theme=None)

# df = pd.read_excel("California Penal Code .xlsx")
# # dfx = pd.read_csv("Court_appB.csv") 
# # df1 = df1[['Charges', 'count']].groupby(['Charges']).agg({'count':'sum'}).reset_index()
# # df1 = df1.sort_values(['Charges', 'count'])

# cols[1].markdown('######')
# cols[1].markdown('####')
# cols[1].dataframe(df, height=760)

# if st.session_state["authentication_status"]:
#   st.session_state.auth.logout()
# else:
#    switch_page('app')
