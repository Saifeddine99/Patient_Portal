from sending import send
from verification import previous_decision

import pymongo as py

from encrypt import encrypt_data
from decrypt import decrypt_data

#-----------------------------------------------------------------------------
myclient=py.MongoClient("mongodb://localhost:27017")
#relating data to "demographic_database"
demographic_data_coll=myclient["Demographic_database"]["Demographic data"]
#-----------------------------------------------------------------------------

import streamlit as st

def consent_decision(phone_number):
    if phone_number:
        #Here, we'll be checking the existence of this phone number on our database.
        encrypted_phone_number=encrypt_data(phone_number)
        demog_data=demographic_data_coll.find_one({"phone number": encrypted_phone_number})

        if demog_data:
            #Here, it means that the phone number really exists! So, we'll be extracting some data.
            uuid = demog_data["uuid"]
            phone_number_db = decrypt_data(demog_data["phone number"])

            patient_name = decrypt_data(demog_data["demographic data"]["identities"][0]["details"]["items"][0]["value"]["value"])
            patient_surname = decrypt_data(demog_data["demographic data"]["identities"][0]["details"]["items"][1]["value"]["value"])
            gender="Mrs"
            patient_gender = decrypt_data(demog_data["demographic data"]["details"]["items"][0]["items"][4]["value"]["value"])
            if patient_gender=="MALE":
                gender="Mr"

            st.write("#")
            st.success(f"Hello {gender} {patient_name} {patient_surname}!")

            st.write("#")
            
            a,b,c=st.columns([8,0.5,1.5])
            with a:
                st.write("Do you accept to use your demographic & clinical data for research purposes?")
            with c:
                decision=st.radio("s",
                                ["YES","NO"],
                                label_visibility="collapsed"
                                )
            
            st.write("#")
            st.write("#")

            #Adding a button to store decision once clicked.
            cola, colb, colc = st.columns([4,2,3])
            with colb:
                done = st.button('Submit')

            if done:
                prev_decision=previous_decision(patient_name,uuid)

                if decision=="YES":
                    if prev_decision=="YES":
                        st.info("You're already sharing your data!")
                    else:
                        #Here there is an update in decision. So, we'll be sending the new decision to BlockChain.
                        st.success(" : Your data will be shared!",icon="✅")
                        send(patient_name,uuid,decision)
                        
                else:
                    if prev_decision=="NO":
                        st.info("You're already not sharing your data!")
                    else:
                        #Here there is an update in decision. So, we'll be sending the new decision to BlockChain.
                        st.success(" : Your data will not be shared",icon="✅")
                        send(patient_name,uuid,decision)
                        


        else:
            #Here, we're in the case of invalid phone number. So the user can't submit any decision
            st.write("#")
            st.warning(": Invalid phone number",icon="⛔")

    else:
        st.write("#")
        st.warning(": You must enter your phone number",icon="⛔")