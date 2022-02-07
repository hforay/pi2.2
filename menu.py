import streamlit as st
from PIL import Image
import pyodbc
import pandas as pd
from utilisateur import Utilisateur
from access import Access
from resultat import Resultat
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

image = Image.open("Image1.png")
st.image(image,width=500)

st.title("Asset's Rating")

first_string='Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='
second_string=os.getcwd()
third_string ='\data\Base_Start.accdb;'
third_stringBis='\Gerant.accdb;'
       
con_string = r''+first_string+second_string+third_string
con_string2= r''+first_string+second_string+third_stringBis


listGerant = Resultat()
actif = ""

#st.title("Connect to Google Sheets")
#gsheet_url = "https://docs.google.com/spreadsheets/d/1HV0rvdZ0Jmu-5z7cGTLuhXC5VGYI3m9qscZt5Slo0Qo/edit?usp=sharing"
#conn = connect()
#rows = conn.execute(f'SELECT * FROM "{gsheet_url}"')
#df_gsheet = pd.DataFrame(rows)
#st.write(df_gsheet)


SCOPE = "https://www.googleapis.com/auth/spreadsheets"
SPREADSHEET_ID = "1QlPTiVvfRM82snGN6LELpNkOwVI1_Mp9J9xeJe-QoaA"
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
            range=f"{SHEET_NAME}!A:E",
        )
        .execute()
    )

    df = pd.DataFrame(values["values"])
    df.columns = df.iloc[0]
    df = df[1:]
    return df


def add_row_to_gsheet(gsheet_connector, row) -> None:
    values = (
        gsheet_connector.values()
        .append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:E",
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
            firstName = st.text_input("First Name : ")
        with col2:
            lastName = st.text_input("Last Name : ")

        gerant = Utilisateur(firstName,lastName)

        gerant.setAvis(st.select_slider("Opinion :",["Short", "Neutre", "Long"], value="Neutre"))
        nombre = range(-10,11)
        gerant.setVariation(st.select_slider("Variation :",nombre, value=0))
        gerant.setCommentaire(st.text_area("Note :"))
        gerant.setActif(actif)

        col1, col2, col3 = st.columns(3)
        with col2:
            soumettre = st.form_submit_button("Register")
            if soumettre:
                listGerant.listUtilisateur.append(gerant)
                add_row_to_gsheet(gsheet_connector, [[firstName, lastName, gerant.getAvis(), gerant.getVariation(), gerant.getCommentaire(),gerant.getActif()]])
        if (gerant.getFirstName()!="" and gerant.getLastName()!=""):
            if soumettre:
                st.success("The rating of the portfolio manager, {} {}, has been successfully registered.".format(gerant.getFirstName(),gerant.getLastName()))
        else:
            st.warning("Please complete the form before sending.")

def ReadDB(gsheet_connector):
    st.dataframe(get_data(gsheet_connector))

def meanVariation(gsheet_connector):
    st.subheader("Variation")
    df = get_data(gsheet_connector)
    mean = round(float(pd.DataFrame((tuple(t) for t in df[3])).mean()),2)
    st.write("The average of the variation is : {}".format(mean))

def countAvis(gsheet_connector):
    st.subheader("Opinion")
    countShort, countNeutre, countLong, total = 0, 0, 0, 0
    df = get_data(gsheet_connector)
    for i in df[2]:
        if(i == "Short"):
            countShort += 1
        elif(i == "Neutre"):
            countNeutre += 1
        elif(i == "Long"):
            countLong += 1
    total = countShort + countNeutre + countLong
    pourcentageShort, pourcentageNeutre, pourcentageLong = round((countShort/total)*100,2), round((countNeutre/total)*100,2), round((countLong/total)*100,2)
    st.write("Short : {} | Percentage : {} %".format(countShort,pourcentageShort))
    st.write("Neutre : {} | Percentage : {} %".format(countNeutre,pourcentageNeutre))
    st.write("Long : {} | Percentage : {} %".format(countLong,pourcentageLong))


def AffCommentaire(gsheet_connector):
    st.subheader("Note")
    df = get_data(gsheet_connector)
    for i in df.index:
        st.write(df[0][i] + " " + df[1][i] + " commented : " + df[4][i])


def Reporting(gsheet_connector):

    st.header("Scoring Result")
    meanVariation(gsheet_connector)
    countAvis(gsheet_connector)
    AffCommentaire(gsheet_connector)
    with st.expander("Ratings DataBase"):
        st.write(f"Open original [Google Sheet]({GSHEET_URL})")
        st.dataframe(get_data(gsheet_connector))

def RemoveBDD():
    try: 
        readDataBase = Access(con_string2)
        utilisateur = 'utilisateur'
        requete = "DELETE FROM {};".format(utilisateur)
        data = readDataBase.execute(requete)
        readDataBase.commit()
        readDataBase.close()
    except pyodbc.Error as e:
        print("Error in connection")
    
    st.success("The rating data base is ready for a new rating.")

def Main():

    gsheet_connector = connect_to_gsheet()


    actif = ""
    df = get_data(gsheet_connector)
 
    if(df.empty):
        actif, save = Select_Actif_NbGerant(gsheet_connector)
    else:
        actif = str(df[5][0])
        save = True

    if(save==True):
        st.success("The Asset is {}.".format(actif))
        NewGerant(actif,gsheet_connector)
        selected = st.checkbox("View Report")

        if(selected):
            Reporting(gsheet_connector)
            removeBBD = st.checkbox("Reset")
            if(removeBBD):
                RemoveBDD(gsheet_connector)
                
Main()
