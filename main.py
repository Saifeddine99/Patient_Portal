import streamlit as st 
from streamlit_option_menu import option_menu

from PIL import Image
img=Image.open('page_icon.png')

st.set_page_config(page_title = "Patient Portal", page_icon = img, layout = "centered")

from dashboard import dashboard_interface
from consents import consent_decision

selected=option_menu(
    menu_title=None,
    options=["DASHBOARD","CONSENTS MANAGEMENT"],
    icons=["speedometer2","eye-slash"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
                "container": {"margin": "0px !important","padding": "0!important", "align-items": "stretch", "background-color": "#fafafa"},
                "icon": {"color": "orange", "font-size": "25px"},
                "nav-link": {
                    "font-size": "18px",
                    "text-align": "center",
                    "margin": "0px",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {"background-color": "green"},
            },
)


#-----------------------------------------------------------------------------
import pymongo as py

myclient=py.MongoClient("mongodb://localhost:27017")
#Relating data to "clinical_data"
medical_data_coll=myclient["Clinical_database"]["Medical data"]
medical_hist_coll=myclient["Clinical_database"]["Medical history"]

#relating data to "demographic_database"
demographic_data_coll=myclient["Demographic_database"]["Demographic data"]
#-----------------------------------------------------------------------------
st.write("#")
st.write("#")

#Use phone number for identification:
col1,col2,col3= st.columns([4,0.1,4])
with col1:
    st.header("Phone Number:")
with col3:
    phone_number=st.text_input("enter your phone number here:", )

if selected=="DASHBOARD":
    dashboard_interface(phone_number)

if selected=="CONSENTS MANAGEMENT":
    consent_decision(phone_number)