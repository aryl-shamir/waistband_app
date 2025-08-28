# I like to emphasis that this code was made gradually after encounting some errors on deployement. 

import streamlit as st 
import math 
import os 
from datetime import datetime
import joblib
import pandas as pd 
import numpy as np
from sklearn.preprocessing import StandardScaler, FunctionTransformer
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.compose import ColumnTransformer

from streamlit_gsheets import GSheetsConnection
from oauth2client.service_account import ServiceAccountCredentials
import gspread

def bmi(X:pd.DataFrame) -> float:
    '''
    Compute the BMI from dataframe of weight(kg) and hieght(m) columns
    
    parameters:
    X(pd.DataFrame): Dataframe containing weight in the first column and height in the second column.
    
    return: 
    float: BMI value.
    
    '''
    X = np.array(X)
    return X[:, [0]] / (X[:, [1]]**2) 

#Custom features name out 
def column_name(function_transformer, feature_names_in):
    '''
    Generate feature names after transformation
    
    parameters:
        function_transformer: The function transformer instance 
        feature_names_in: list of features names
    
    return:
        list of output features names.
    '''
    return['value'] #feature name out.

def bmi_pipeline():
    return make_pipeline(
        FunctionTransformer(bmi, feature_names_out=column_name),
        StandardScaler())
    
def custom_round_up(number):
    """Rounds a number up only if its fractional part is greater than 0.5.
    Otherwise, it rounds down to the nearest whole number."""
    
    fractional_part = number - math.floor(number)
    if fractional_part > 0.5:
        return math.ceil(number)
    else:
        return math.floor(number)
    
#loading the model 

# The os.join.path helps to have access to the relative path.
model_path = os.path.join('notebooks', 'models', 'my_waistband_model.pkl')
model = joblib.load(open(model_path, "rb"))

def waist_and_hip_size_pred(input_data:np.array) -> float:
    
    #changing the input_data into a dataframe
    input_data_as_df = pd.DataFrame(input_data,
                            columns=['sex', 'age', 'height(m)', 'weight(kg)'])
    
    # The model predicts two out out_put eg. ([[97, 73]]). one row , two columns. 
    hip_size = float(round(model.predict(input_data_as_df)[0, 0], 2))# index for the rows, columns. 
    waist_size = float(round(model.predict(input_data_as_df)[0, 1], 2))
    waist_size_inch = custom_round_up(waist_size / 2.54)
    hip_size_inch = custom_round_up(hip_size / 2.54)
    
    return waist_size, hip_size, waist_size_inch,  hip_size_inch


# Defining the entry point: The starting point of the code that starts the primary task of the script. 

def main():
    st.title('Waistband & Hip size App')

    # Uploading the image from the static directory to the app using the os module and, getcwd.
    st.image(os.path.join(os.getcwd(), 'static', 'waist_image.jpg' ))
    st.markdown('**We would like to estimate your hip size and waistband size based on your gender, age, height and weight**')
    
    # Establishing a connection between the streamlit app and the google sheet. 
    def load_data():
        conn = st.connection("gsheets", type=GSheetsConnection)
    
    # fetch existing data 
        existing_data = conn.read(worksheet="sheet1", usecols=list(range(6)), ttl=500)
        #explicitly define the desired column order to ensure the operations preserve the original order.
        existing_data.columns = ["gender", "age", "height (m)", "weight (kg)","hipsize (cm)", "waistband (cm)"]
        return conn, existing_data
    conn, existing_data = load_data()
    
    # setting a session_state for the user_informations, so as to store values within thesame session 
    
    if "user_infos" not in st.session_state:
        st.session_state.user_infos = {
        "gender": None,
        "age": None, 
        "height": None, 
        "weight": None
    }
    
    # setting a session_state for the user right dimension after our app would have make a prediction.
    if "right_dim" not in st.session_state:
        st.session_state.right_dim = {
            "waistband": None,
            "hip_size": None, 
        }
        
    #Getting information from the user 
    st.session_state.user_infos["gender"] = st.selectbox('Gender', ["Male", "Female"], key="gender")
    st.session_state.user_infos["age"] = st.number_input("Enter your age: ", min_value=18, max_value= 67, key="age") # the ages of the people ranged from 18 to 67
    st.session_state.user_infos["height"] = st.number_input("Enter your height (cm): ", key="height")
    st.session_state.user_infos["weight"] = st.number_input("Enter your weight (cm): ", step= 0.1, key="weight")
        
    if st.session_state.user_infos["gender"] == "Male":
        st.session_state.user_infos["gender"] = 1
    elif st.session_state.user_infos["gender"] == "Female":
        st.session_state.user_infos["gender"] = 0
        
    #Code for prediction
    
    # creatung a predict button session so as to store it value, and keep it result on the screen when
    # clicking another button 
    # creating a session_state to store the state and result of the predict button
    if "predict_button" not in st.session_state:
        st.session_state.predict_button = False
    if "predict_button_result" not in st.session_state:
        st.session_state.predict_button_result = None 
        
    # creating a session_state to store the state and result of the feedback button
    if "feedback_button" not in st.session_state:
        st.session_state.feedback_button = False
    
    # Creating a call back function for the predict button   
    def on_click_predict_button():
        """Update the session state variable of the predict buttton to True, and store the result 
         in the session state predict result. """
         
        st.session_state.predict_button = True
        
        # create a list of values found in the st.session_state.user_infos dictionary
        list_info = list(st.session_state.user_infos.values())
        waist_size, hip_size, waist_size_inch,  hip_size_inch = waist_and_hip_size_pred([[list_info[0], list_info[1], list_info[2], list_info[3]]])
        # store the result in the session state predict button result. 
        st.session_state.predict_button_result = waist_size, hip_size, waist_size_inch,  hip_size_inch 
    
    # Creating a call back function for the feedback button   
    def on_click_feedback_button():
        ''' update the session state variable of the feedback button True'''
        st.session_state.feedback_button = True
        
    # creating the predict button
    st.button('predict', on_click=on_click_predict_button) # On click, it will trigger the on_click_predict_button fucntion
        
    #ckeck the session state variable using the if conditiaml statement. 
    if st.session_state.predict_button: # This is True you click on the predict button
        if not all(st.session_state.user_infos.values()):
            st.warning("Please enter all the informations")
        else:
            col1, col2, col3 = st.columns([1, 1, 1]) # making the second column more wider
            col1.subheader('Predicted result')
            col2.subheader('In cm')
            col2.write(f"**waist**: {st.session_state.predict_button_result[0]}cm")
            col2.write(f"**hip**:{st.session_state.predict_button_result[1]}cm")
            col3.subheader('In Inch')
            col3.write(f'**waist**: {st.session_state.predict_button_result[2]}"')
            col3.write(f'**hip**:{st.session_state.predict_button_result[3]}"')
        
    # Creating the feedback loop
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.write('')  
    with col1:
        st.write('') 
    with col1:
        st.write('') 
    with col4:
        feedback_box = st.selectbox('Was our prediction correct?', ['Yes', 'No'])
        feedback_button = st.button('feedback', on_click=on_click_feedback_button)
        
    st.write(' ')
    st.write(' ')
    st.write(' ')
    
    if st.session_state.feedback_button: # Turns True if click on the feedback button. 
        if feedback_box == "Yes":
            col1, col2, col3 = st.columns([1, 3, 1]) # making the second column more wider
            col2.subheader('Thank you for Trying our App')
            col2.image(os.path.join(os.getcwd(), 'static', 'giphy-2.gif' ))
            # st.subheader('Thank you for Trying our App')
        else:
           
            st.session_state.right_dim["waistband"] = st.number_input("Please enter the right waistband(cm): ", key="waistband")
            st.session_state.right_dim["hip_size"] = st.number_input("Please enter the right hip_size(cm): ", step= 0.1, key="hip_size")
            submit_button = st.button('submit')
            
            if st.session_state.user_infos["gender"] == "Male":
                st.session_state.user_infos["gender"] = 1
            elif st.session_state.user_infos["gender"] == "Female":
                st.session_state.user_infos["gender"] = 0 
            
            # converting user entries into a new row(dataframe)
            new_data = pd.DataFrame([{
                "gender": st.session_state.user_infos["gender"],
                "age": st.session_state.user_infos["age"],
                "height (m)" : st.session_state.user_infos["height"],
                "weight (cm)": st.session_state.user_infos["weight"],
                "hipsize (cm)": st.session_state.right_dim["hip_size"],
                "waistband (cm)": st.session_state.right_dim["waistband"]
                }])
            
            #Append the new_data to the existing data frame
            updated_df = pd.concat([existing_data, new_data], ignore_index=True, )
            
            # Write updated dataframe back to Google Sheets
            conn.update(worksheet="sheet1", data=updated_df)
            
if __name__ == "__main__":
    main()
    
    