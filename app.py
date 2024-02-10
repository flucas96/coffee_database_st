import streamlit as st
import pandas as pd
import connectors
import streamlit_antd_components as sac

st.set_page_config(page_title="Kaffee Datenbank", page_icon="☕", layout="wide")

# Load data

st.header("Unsere Kaffee Datenbank!")
df = connectors.download_data("test_db_fl")

st.write(df)
with st.expander("**Neuen Kaffee hinzufügen**"):
    with st.form(key="new_coffee"):

        col_left, mid, col_right = st.columns([1,1,1])

        #Name
        with col_left:
            image = st.file_uploader("Bild", type=["jpg", "jpeg", "png"])
            name = st.text_input("Name")
            st.markdown("<br>", unsafe_allow_html=True)
            mahlgrad = st.text_input("Mahlgrad")
        with col_right:
              #Händler
            haendler = st.text_input("Händler")
            preis = st.text_input("Preis")

        #Bewertung
        bewertung = st.slider("Bewertung", 0, 10,1)
        #Kommentar
        kommentar = st.text_area("Kommentar")

        new_coffee_submit = st.form_submit_button("Hinzufügen", use_container_width=True, type="primary")

        if new_coffee_submit:
            #check if all fields are filled
            if name and haendler and preis and mahlgrad and bewertung and kommentar:
                #add new coffee to database
                new_coffee = pd.DataFrame({
                    "Name": [name],
                    "Händler": [haendler],
                    "Preis": [preis],
                    "Mahlgrad": [mahlgrad],
                    "Bewertung": [bewertung],
                    "Kommentar": [kommentar]
                })
                connectors.add_coffee(new_coffee)
            else:
                st.toast("Bitte falle Felder ausfüllen :)")
                st.error("Bitte falle Felder ausfüllen :)")
      
      


st.header("Alle Einträge:")
if len(df) == 0:

    sac.alert(label='<b>Noch keine Einträge :)<b>', size='lg', banner=True, icon=True, closable=True)

else:
    pass
    #Daten anzeigen