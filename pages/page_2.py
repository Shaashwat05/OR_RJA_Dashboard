import streamlit as st
import numpy as np
import plotly.figure_factory as ff
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from streamlit_extras.stylable_container import stylable_container 
import pickle
import ast
import os
import requests
from support import check_and_download_file
import ast

st.set_page_config(layout="wide")
color = {'Black or African American': '#ff7eb6', 'White':'#be95ff', 'Native American':'#0f62fe', 'Hispanic':'#dface6', 'Pacific Islander':'#3ddbd9', 'Unkown/Other':'#c1c7cd','Asian':'#82cfff',}

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

#----------------------------Page 2-------------------------#
Page2 = stylable_container(key="Page2", css_styles=""" {box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 15px;} """)
Page2.header("Download Data", anchor = 'section-3', help  = 'Download data relevant to your case. Use the filters to Determine what data do you need.')
selected_point = []
#loc = "DA_referrals_2022(1).csv"

Charge = Page2.selectbox('Select Type of Charge', ('Booking Charge', 'Filed Charge', 'CDCR'))
file_path = "Referral_page2.csv"
check_and_download_file(file_path)

file_path = "Court_page2.csv"
check_and_download_file(file_path)

file_path = "Sentence_page2.csv"
check_and_download_file(file_path)

# Setting Page Control filters
loc = "Referral_page2.csv" if Charge == 'Booking Charge' else "Court_page2.csv" if Charge == 'Filed Charge' else "Sentence_page2.csv"
df = pd.read_csv(loc)
df = df.drop(columns='Unnamed: 0')
uid = 'UID' if Charge == 'Booking Charge' else 'Case Number'
filename = "list_of_charges.pkl" if Charge == 'Booking Charge' else "list_of_charges_detailed.pkl" if Charge == 'Filed Charge' else "list_of_charges_CDCR.pkl"
with open(filename, "rb") as fp:   # Unpickling
  charges = pickle.load(fp)

charges = [str(charge).strip() for charge in charges]

cols = Page2.columns(4)
Filtera = cols[0].multiselect('Select Charges', tuple(charges), help='Select Charges relevant to your case and client')
Filterb = cols[2].multiselect('Select Ethnicity', tuple(color.keys()), help='Select relevant Ethnicity')
Filterc = cols[1].selectbox('Select Function - Charges', ("AND", "OR"), help="AND - All Clients charged with all chosen charges \n\n OR - All Clients charged with atleast one of the chosen charges")
cols_list = df.columns.tolist()
cols_list.remove('Charges')
cols_list.remove('Race') 
cols_list.remove(uid)
Filterd = cols[3].multiselect('Select Additional Columns to View', tuple(cols_list), help="1. UID - Unique case iD for arrests \n\n 2. Age / Gender - Age / Gender of the perpetrator \n\n 3. Arrested For - Penal Code and Description of Crimes \n\n 4. Arrest Location - Partial or Complete location of arrest \n\n 5. County of Arrest - County in which the defendant was arrested. * All values are not San Bernardino \n\n 6. Source - Arresting Police Agency \n\n 7. Year - Year of Arrest for Booking charge / Year of Charging for Filed Charge or Sentenced For \n\n 8. dispostion - Final decision for the case \n\n 9. Offense Date (start, end) - The date of offense in court data, usually start and end values are the same \n\n 10. DOB - Date of Birth of the defendant \n\n 11. Sentence Type - The nature of degree of sentence, ex DSL, condemed, second striker, etc  \n\n 12. Aggregate Sentence in months - Number of months of sentencing \n\n 13. Offender ID - Unique defandant identifer as opposed to case number that can have multiple defandants")


disp_cols = [uid, 'Charges', 'Race'] + Filterd
df = df[disp_cols]

for i in df.columns[1:]:
  if i != "people_count":
    df[i] = df[i].str.strip('[]').str.split(',')
    #df[i] = df[i].apply(ast.literal_eval) if pd.api.types.is_string_dtype(df[i]) else df[i].str.strip('[]').str.split(',')
    def remove_single_quotes(lst): 
      return [s.strip().replace("'", "") for s in lst]
    df[i] = df[i].apply(remove_single_quotes)

#print(df[df['Case Number'] == 'FVI20001621']['Charges'].values)
#print(df[df['Charges'].apply(lambda x: all(value in x for value in ['PC211-213(a)(1)(A)-F']))])
if len(Filtera) > 0:
  print(Filtera)
  if Filterc == 'AND':
    df = df[df['Charges'].apply(lambda x: all(value in x for value in Filtera))]
  else:
    df = df[df['Charges'].apply(lambda x: any(value in x for value in Filtera))]
  print(df)

if len(Filterb) > 0:
  df = df[df['Race'].apply(lambda x: any(value in x for value in Filterb))]


df[uid] = df[uid].map(str)
Page2.dataframe(df[disp_cols],width=1300)



