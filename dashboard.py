import pymongo as py

from encrypt import encrypt_data
from decrypt import decrypt_data

from plots import test_results_time_series, medications_list_table

#-----------------------------------------------------------------------------
myclient=py.MongoClient("mongodb://localhost:27017")
#Relating data to "clinical_data"
medical_data_coll=myclient["Clinical_database"]["Medical data"]
medical_hist_coll=myclient["Clinical_database"]["Medical history"]

#relating data to "demographic_database"
demographic_data_coll=myclient["Demographic_database"]["Demographic data"]
#-----------------------------------------------------------------------------

import streamlit as st

def dashboard_interface(phone_number):
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
            
            occurence=medical_data_coll.count_documents({"uuid": uuid})
            if occurence>0:
                
                st.info(f": Your total number of clinical documents stored in database is {occurence}", icon="🚨")
    #------------------------------------------------------------------------------------------------------------            
                cursor_med_data = medical_data_coll.find({"uuid": uuid})
                medication_list=[]
                problem_lists=[]

                for cursor in cursor_med_data:
                    #Here we put in a dictionary the list of recommended drugs for each time.
                    drugs_dict={}
                    try:
                        for drug_json_file in cursor["medication list"]:
                            drug=decrypt_data(drug_json_file["content"][0]["items"][0]["description"]["items"][0]["value"]["value"])
                            dose=decrypt_data(drug_json_file["content"][0]["items"][0]["description"]["items"][2]["items"][3]["value"]["value"])
                            drugs_dict[drug]=dose
                    except:
                        pass

                    medication_list.append(drugs_dict)

                    #Here we put in a list the list of clinical diseases this patient is suffering from each time.
                    problem_list=[]
                    try:
                        for problem_cursor in cursor["problem list"]:
                            problem=decrypt_data(problem_cursor["content"][0]["items"][0]["data"]["items"][0]["value"]["value"])
                            problem_list.append(problem)
                    except:
                        pass

                    problem_lists.append(problem_list)

    #------------------------------------------------------------------------------------------------------------
                cursor_med_hist = medical_hist_coll.find({"uuid": uuid})

                storage_dates_med_hist=[]
                hba1c_results_dict={}
                bmi_values_dict={}
                for cursor in cursor_med_hist:

                    #Here we'll be extracting the date of storage of each document.
                    try:
                        decrypted_date=decrypt_data(cursor["check date"])
                    except:
                        decrypted_date=decrypt_data(cursor["saving date"])
                    storage_dates_med_hist.append(decrypted_date)

                    if len(cursor["analytics"][0]):
                        #Here we'll be creting a list containing all the HbA1c records stored in Mongo.
                        for test in cursor["analytics"][0]:
                            test_name = decrypt_data(test["content"][0]["data"]["events"][0]["data"]["items"][0]["value"]["value"])
                            if test_name == "HBA1C":
                                try:
                                    test_value=float(decrypt_data(test["content"][0]["data"]["events"][0]["data"]["items"][6]["items"][2]["value"]["magnitude"]))
                                    hba1c_results_dict[decrypted_date] = test_value
                                    break

                                except:
                                    pass
                    try:                      
                        if len(cursor["analytics"][1]):
                            #Here we'll be creting a list containing all the BMI values stored in Mongo.
                            
                            bmi_value=float(decrypt_data(cursor["analytics"][1]["content"][2]["data"]["events"][0]["data"]["items"][0]["value"]["magnitude"]))
                            bmi_values_dict[decrypted_date] = bmi_value
                    except:
                        pass

    #------------------------------------------------------------------------------------------------------------          
                st.write(storage_dates_med_hist)
                test_results_time_series(hba1c_results_dict,"HbA1c")
                test_results_time_series(bmi_values_dict,"BMI")
                medications_list_table(medication_list, storage_dates_med_hist)
    #------------------------------------------------------------------------------------------------------------
            else:

                st.error(": You don't have any clinical data stored in database", icon="😕")

        else:
            #Here, we're in the case of invalid phone number. So the user can't submit any decision
            st.write("#")
            st.warning(": Invalid phone number",icon="⛔")

    else:
        st.write("#")
        st.warning(": You must enter your phone number",icon="⛔")