import streamlit as st
from PIL import Image
import pandas as pd
from utilisateur import Utilisateur
from resultat import Resultat
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

image = Image.open("Image1.png")
st.image(image,width=690)

st.title("Asset's Rating")

listGerant = Resultat()
actif = ""

SCOPE = "https://www.googleapis.com/auth/spreadsheets"
SPREADSHEET_ID = "1XqZ3ipVFRnqVB8Rf4wCoz1GObfY5EKCHSzlM559lghA"
SHEET_NAME = "Database"
GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"

def connect_to_gsheet():
    # Create a connection object.
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[SCOPE],
    )

    service = build("sheets", "v4", credentials=credentials)
    gsheet_connector = service.spreadsheets()
    return gsheet_connector

def get_data(gsheet_connector) -> pd.DataFrame:
    values = (
        gsheet_connector.values()
        .get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:F",
        )
        .execute()
    )
    df = pd.DataFrame(values["values"])
    df.columns = df.iloc[0]
    df = df[1:]
    col = ["FirstName", "LastName", "Opinion", "Variation", "Note", "Asset"]
    df = df[col]
    return df

def delete_data(gsheet_connector) -> pd.DataFrame:
    values = (
        gsheet_connector.values()
        .clear(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A2:F100",
        )
        .execute()
    )
    st.success("The rating data base is ready for a new rating.")

def add_row_to_gsheet(gsheet_connector, row) -> None:
    values = (
        gsheet_connector.values()
        .append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:F",
            body=dict(values=row),
            valueInputOption="USER_ENTERED",
        )
        .execute()
    )

def Select_Actif_NbGerant():
    
    actif = st.text_input("Pick an Asset : ")

    col1, col2, col3 = st.columns(3)
    with col2:
        save = st.checkbox("Register")

    return actif, save

def NewGerant(actif,gsheet_connector):

    st.header("New Rating")

    with st.form("New Portfolio Manager",clear_on_submit=True):

        col1, col2, col3 = st.columns(3)
        with col1:
            FirstName = st.text_input("First Name : ")
        with col2:
            LastName = st.text_input("Last Name : ")

        gerant = Utilisateur(FirstName,LastName)

        gerant.setAvis(st.select_slider("Opinion :",["Ultra-short","Short", "Neutre", "Long","Ultra-long"], value="Neutre"))
        nombre = range(-10,11)
        gerant.setVariation(st.select_slider("Variation :",nombre, value=0))
        gerant.setCommentaire(st.text_area("Note :"))
        gerant.setActif(actif)

        Opinion = gerant.getAvis()
        Variation = gerant.getVariation()
        Note = gerant.getCommentaire()
        Asset = gerant.getActif()

        col1, col2, col3 = st.columns(3)
        with col2:
            soumettre = st.form_submit_button("Register")
            if soumettre:
                listGerant.listUtilisateur.append(gerant)
                add_row_to_gsheet(gsheet_connector, [[FirstName, LastName, Opinion, Variation, Note, Asset]])
        if (gerant.getFirstName()!="" and gerant.getLastName()!=""):
            if soumettre:
                st.success("The rating of the portfolio manager, {} {}, has been successfully registered.".format(gerant.getFirstName(),gerant.getLastName()))
        else:
            st.warning("Please complete the form before sending.")

def meanVariation(gsheet_connector):
    st.subheader("Variation")
    df = get_data(gsheet_connector)
    somme, moyenne = 0, 0
    if len(df)!=0:
        for i in df.index:
            somme += int(df["Variation"][i])

        moyenne = round(float(somme / len(df)),2)

    st.write("The average of the variation is : {}".format(moyenne))

def countAvis(gsheet_connector):
    st.subheader("Opinion")
    countShort, countNeutre, countLong, countUltraShort, countUltraLong, total = 0, 0, 0, 0, 0, 0
    df = get_data(gsheet_connector)
    for i in df.index:
        if(df["Opinion"][i] == "Short"):
            countShort += 1
        elif(df["Opinion"][i] == "Neutre"):
            countNeutre += 1
        elif(df["Opinion"][i] == "Long"):
            countLong += 1
        elif(df["Opinion"][i] == "Ultra-short"):
            countUltraShort += 1
        elif(df["Opinion"][i] == "Ultra-long"):
            countUltraLong += 1
    total = countShort + countNeutre + countLong + countUltraShort + countUltraLong
    pourcentageUltraShort, pourcentageShort, pourcentageNeutre, pourcentageLong, pourcentageUltraLong = round((countUltraShort/total)*100,2), round((countShort/total)*100,2), round((countNeutre/total)*100,2), round((countLong/total)*100,2), round((countUltraLong/total)*100,2)
    st.write("Ultra-short : {} | Percentage : {} %".format(countUltraShort,pourcentageUltraShort))
    st.write("Short : {} | Percentage : {} %".format(countShort,pourcentageShort))
    st.write("Neutre : {} | Percentage : {} %".format(countNeutre,pourcentageNeutre))
    st.write("Long : {} | Percentage : {} %".format(countLong,pourcentageLong))
    st.write("Ultra-long : {} | Percentage : {} %".format(countUltraLong,pourcentageUltraLong))

def AffCommentaire(gsheet_connector):
    st.subheader("Note")
    df = get_data(gsheet_connector)
    for i in df.index:
        st.write(df["FirstName"][i] + " " + df["LastName"][i] + " commented : " + df["Note"][i])

def Reporting(gsheet_connector):

    st.header("Scoring Result")
    meanVariation(gsheet_connector)
    countAvis(gsheet_connector)
    AffCommentaire(gsheet_connector)
    with st.expander("Ratings DataBase"):
        st.write(f"Open original [Google Sheet]({GSHEET_URL})")
        st.dataframe(get_data(gsheet_connector))

def Main():

    gsheet_connector = connect_to_gsheet()

    actif = ""

    df = get_data(gsheet_connector)

    if df.empty:
        actif, save = Select_Actif_NbGerant()
        df = get_data(gsheet_connector)
    else:
        actif = str(df["Asset"][1])
        save = True

    if(save==True):
        st.success("The Asset is {}.".format(actif))
        NewGerant(actif,gsheet_connector)
        selected = st.checkbox("View Report")

        if(selected):
            Reporting(gsheet_connector)
            removeBBD = st.checkbox("Reset")
            if(removeBBD):
                delete_data(gsheet_connector)
                
Main()
