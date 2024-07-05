import streamlit as st
import plotly.express as px
import pandas as pd
from streamlit_extras.stylable_container import stylable_container 
from streamlit_extras.metric_cards import style_metric_cards
import pickle
from support import check_and_download_file
import re
import numpy as np
# Page config and data
st.set_page_config(layout="wide")
color = {'Black or African American': '#2993A3', 'White':'#666766', 'Native American':'#f4b780', 'Hispanic':'#a0cd7c', 'Pacific Islander':'#a680ba', 'Unknown/Other':'#3a393a','Asian':'#f37e85'}

#----------------------------NavBar-------------------------#
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
    st.switch_page("app.py")

#---------------------------- Page 1 ----------------------------#
cols = st.columns(2)

Page1 = stylable_container(key="Page1", css_styles=""" {box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 15px;}""")
cols = Page1.columns([4,3,3])
cols[1].header("Charges By Race", anchor = 'section-2', help = 'Understanding Disparity at different stages of a criminal proceeding (i.e. Arrest, Charging and Sentencing). If the ratio value increase from one stage to another it means that disparity originated at that point in the case proceedings. Even if the ratio doesnt increase, disparity can still exist but needs to be measured in more detail.')

with open("list_of_charges.pkl", "rb") as fp:   # Unpickling
  charges = pickle.load(fp)

with open('list_of_charges_detailed.pkl',"rb")as fp:
    chargesC = pickle.load(fp)

col = Page1.columns([0.5, 9, 0.5])
PC = col[1].multiselect('Select Type of Charge', list(dict.fromkeys(list(charges) + list(chargesC))), default='459')
print(PC)

file_path = "Population.csv"
check_and_download_file(file_path)

# Reading and Processing Data
pop = pd.read_csv("Population.csv")

file_path = "Arrest_page1.csv"
check_and_download_file(file_path)
df = pd.read_csv("Arrest_page1.csv")

file_path = "Court_page1.csv"
check_and_download_file(file_path)
dfr = pd.read_csv("Court_page1.csv")

file_path = "Sentence_page1.csv"
check_and_download_file(file_path)
dfd = pd.read_csv("Sentence_page1.csv")

cols = Page1.columns([0.5,2.25,2.25,0.5,2.5,1.5,0.5])

st.markdown("""
    <style>
    .stSlider [data-baseweb=slider]{
        width: 100%;
    }
    </style>
    """,unsafe_allow_html=True)
timeline = cols[2].slider('Select Timeline for Cases', 1990, 2024, (2015,2023))
perCap = cols[1].selectbox("Display Graph Per Capita", ("No", "Yes"), index=1)
cols[4].subheader("Charge Percentage Ratio")

c1, c2, c3, c4, c5 = Page1.columns([4.5, 0.5, 0.5, 4, 0.5])
with c1:
    df = pd.concat([dfd, dfr, df], ignore_index=True, axis=0)
    df = df[df['Charges'].isin(PC)]
    df = df[(df['year'] >= timeline[0]) & (df['year'] <= timeline[1])]
    df = df[df['Race'] != 'Unknown/Other']
    
    df = df[['Charge Type', 'Race', 'Charges', 'count', 'normalized_vals']].groupby(['Charge Type','Race']).agg({'count':'sum', 'normalized_vals':'sum'}).reset_index()
    custom_dict = {'Booking Charge': 0, 'Filed Charge': 1, 'Conviction Charge': 2} 
    
    df = df.sort_values(by=['Charge Type'], key=lambda x: x.map(custom_dict), ascending=False)
    xaxs = 'count' if perCap == "No" else "normalized_vals"
    fig = px.bar(df, y='Charge Type', x=xaxs,color_discrete_map=color, color='Race', orientation='h')
    fig.update_layout(width=700, height=600,)
    fig.update_layout(xaxis_title="Number of Cases", yaxis_title="")
    fig.update_layout(legend=dict(yanchor="bottom", y=1.0, xanchor="left", x=-0.17, orientation='h', entrywidth=150)) 
    fig.update_layout(font=dict(family="Myriad Pro",size=14))
    fig.update_yaxes(tickangle=270, automargin= True)
    st.plotly_chart(fig, theme=None)

with c4:
    sel_col = 'count' if perCap == "No" else "normalized_vals"
    cc1, cc2 = st.columns(2)
    with cc1:
        PCRace = st.selectbox('Select Race to Compare with', tuple(set(list(df['Race'].unique()) + list(dfr['Race'].unique()))))
    with cc2:
        st.header(" / White")
    r1 = df[(df['Race'] == PCRace) & (df['Charge Type'] == 'Booking Charge')][sel_col].sum()*(10000000)
    r2 = df[(df['Race'] == 'White') & (df['Charge Type'] == 'Booking Charge')][sel_col].sum()*(10000000)

    if r2 != 0:
        val = '%0.2f'%(r1/r2)+'/1'
    else:
        val = '%0.2f'%(r1)+'/'+str(r2)
    new_title = '<p style="font-family:Myriad Pro; color:Black; font-size: 20px;display: inline;vertical-align: top;">'+PCRace+' rate of arrests by the white rate of arrests:  '+val+'</p>'
   
    st.metric(label= PCRace+' rate of arrests by the white rate of arrests:' , value=val, delta=None)
    style_metric_cards()


    r1 = df[(df['Race'] == PCRace) & (df['Charge Type'] == 'Filed Charge')][sel_col].sum()*(10000000)
    r2 = df[(df['Race'] == 'White') & (df['Charge Type'] == 'Filed Charge')][sel_col].sum()*(10000000) 

    if r2 != 0:
        val = '%0.2f'%(r1/r2)+'/1'
    else:
        val = '%0.2f'%(r1)+'/'+str(r2)
    new_title = '<p style="font-family:Myriad Pro; color:Black; font-size: 20px;display: inline;vertical-align: top;">'+PCRace+' rate of charging by the white rate of charging is:  '+val+'</p>'
    st.metric(label=PCRace+' rate of charging by the white rate of charging is:  ', value=val, delta=None)
    style_metric_cards()

    r1 = (df[(df['Race'] == PCRace) & (df['Charge Type'] == 'Conviction Charge')][sel_col].sum()*(10000000))
    r2 = (df[(df['Race'] == 'White') & (df['Charge Type'] == 'Conviction Charge')][sel_col].sum()*(10000000))

    if r2 != 0:
        val = '%0.2f'%(r1/r2)+'/1'
    else:
        val = '%0.2f'%(r1)+'/'+str(r2)
    new_title = '<p style="font-family:Myriad Pro; color:Black; font-size: 20px;display: inline;vertical-align: top;">'+PCRace+' rate of being sentenced by the white rate of being sentenced is:  '+val+'</p>'
    st.metric(label=PCRace+' rate of being sentenced by the white rate of being sentenced is:  ', value=val, delta=None)
    style_metric_cards()






