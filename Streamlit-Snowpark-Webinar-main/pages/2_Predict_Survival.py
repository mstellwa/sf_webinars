import snowflake.snowpark.functions as F
import streamlit as st


@st.experimental_memo(show_spinner=False)
def predict(embarked: str, sex: str, pclass: int, age: int, fare: int):
    session = st.session_state['snowpark_session']
    columns = ["EMBARKED", "SEX", "PCLASS", "AGE", "FARE"]
    embarked = embarked[0:1]
    titanic_df = session.create_dataframe([[embarked, sex, pclass, age, fare]], schema=columns)
    survived_df = titanic_df.select(F.call_udf("survived", F.object_construct('*')).as_("predicted"))

    return survived_df.to_pandas()


st.title("Titanic Survival Prediction")

with st.sidebar:
    with st.form(key="input_pred_form"):
        selected_sex = st.selectbox("Select Gender", ('female', 'male'))
        selected_age = st.slider('Age', 0, 90, 1)
        selected_class = st.selectbox("Select Class", (1,2,3))
        selected_fare = st.slider("Fare (in 1912 $) :", 15, 500, 40)
        ports_range = ('Queesntown, Ireland', 'Southampton, U.K.', ' Cherbourg, France')
        embarked_selected = st.radio('Port of departure', ports_range)
        st.session_state.pred_clicked = st.form_submit_button(label="Predict survival")

if st.session_state.pred_clicked:
    with st.spinner('Predicting survival...'):
        survived_pd = predict(embarked_selected, selected_sex, selected_class, selected_age, selected_fare)
        if survived_pd["PREDICTED"].values[0] == 1.0:
            st.write("### Congrats, you will probably survive!")
            st.snow()
        else:
            st.write("### Oh no, the stars is not aligned in your favour!")
else:
    st.write("**Choose your parameters to the left and see if you will survive!**")
