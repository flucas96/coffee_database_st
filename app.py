import streamlit as st
import pandas as pd
import connectors
import streamlit_antd_components as sac
from st_mui_table import st_mui_table
import base64
from PIL import Image
import io

def convert_image_to_base64(image):
    """
    Converts a PIL Image to a base64 encoded string, including the necessary HTML format prefix.

    Parameters:
    - image: PIL.Image - The image to be converted.

    Returns:
    - str: A complete HTML string that displays the base64 encoded image.
    """
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")  # You can change format to JPEG or other types if needed
    img_str = base64.b64encode(buffered.getvalue()).decode()
    # Create the HTML string with the base64 encoded image
    html_img_str = f'<img src="data:image/png;base64,{img_str}" style="max-height: 200px;" />'
    return html_img_str

st.set_page_config(page_title="Kaffee Datenbank", page_icon="☕", layout="wide")

# Load data

st.header("Unsere Kaffee Datenbank!")
df = connectors.download_data("test_db_fl")

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
            if name and haendler and preis and mahlgrad and bewertung and kommentar and image:
                #add new coffee to database
                image = Image.open(image)
                image = convert_image_to_base64(image)

                new_coffee = pd.DataFrame({
                    "Name": [name],
                    "Händler": [haendler],
                    "Preis": [preis],
                    "Mahlgrad": [mahlgrad],
                    "Bewertung": [bewertung],
                    "Kommentar": [kommentar],
                    "Bild": [image]
                })
                connectors.add_coffee(new_coffee)
                st.rerun()
            else:
                st.toast("Bitte falle Felder ausfüllen :)")
                st.error("Bitte falle Felder ausfüllen :)")
      
      

st.header("Alle Einträge:")
if len(df) == 0:

    sac.alert(label='<b>Noch keine Einträge :)<b>', size='lg', banner=True, icon=True, closable=True)

else:
    df["Hinzugefügt"] = df["Hinzugefügt"].dt.strftime("%d.%m.%Y %H:%M:%S")
    for col in df.columns:
        df.rename(columns={col: f"<b>{col}<b>"}, inplace=True)

    clicked_coffee = st_mui_table(
    df,  return_clicked_cell=True
)
    st.write(clicked_coffee)

    if clicked_coffee:
        #clicked row
        row = clicked_coffee["row"]
        clicked_coffee = df.iloc[[row]]
        clicked_coffee.columns = [col.replace("<b>", "").replace("</b>", "") for col in clicked_coffee.columns]
    #Daten anzeigen
        with st.form(key="show_coffee"):
            col_left, mid, col_right = st.columns([1,1,1])
            with col_left:
                name = st.text_input("Name", value=clicked_coffee["Name"].values[0])
                st.markdown("<br>", unsafe_allow_html=True)
                mahlgrad = st.text_input("Mahlgrad", value=clicked_coffee["Mahlgrad"].values[0])
            with col_right:
                haendler = st.text_input("Händler", value=clicked_coffee["Händler"].values[0])
                preis = st.text_input("Preis", value=clicked_coffee["Preis"].values[0])

            bewertung = st.slider("Bewertung", 0, 10, int(clicked_coffee["Bewertung"].values[0]))
            kommentar = st.text_area("Kommentar", value=clicked_coffee["Kommentar"].values[0])
            st.markdown("<br>", unsafe_allow_html=True)
            _,middle,_ = st.columns([1,5,1])
            middle.markdown("<center>" + clicked_coffee["Bild"].values[0] + "</center>", unsafe_allow_html=True)
            col1,col2 = st.columns([1,1])
            with col1:
                save_btn = st.form_submit_button("Speichern", use_container_width=True, type="primary")
            with col2:
                del_btn = st.form_submit_button("Löschen", use_container_width=True)

            if save_btn:
                #save changes
                #Make da dictionary of all changes
                changes = {
                }
                if name != clicked_coffee["Name"].values[0]:
                    changes["Name"] = name
                if haendler != clicked_coffee["Händler"].values[0]:
                    changes["Händler"] = haendler
                if preis != clicked_coffee["Preis"].values[0]:
                    changes["Preis"] = preis
                if mahlgrad != clicked_coffee["Mahlgrad"].values[0]:
                    changes["Mahlgrad"] = mahlgrad
                if bewertung != clicked_coffee["Bewertung"].values[0]:
                    changes["Bewertung"] = bewertung
                if kommentar != clicked_coffee["Kommentar"].values[0]:
                    changes["Kommentar"] = kommentar
                if changes:
                    connectors.update_coffee(clicked_coffee["id"].values[0], changes)
                    st.rerun()

            if del_btn:
                connectors.delete_coffee(clicked_coffee["id"].values[0])
                st.rerun()