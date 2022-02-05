import streamlit as st
from PIL import Image
import pyodbc
import pandas as pd
from utilisateur import Utilisateur
from access import Access
from resultat import Resultat
import os

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

def Select_Actif_NbGerant():
    
    actif = st.text_input("Pick an Asset : ")

    col1, col2, col3 = st.columns(3)
    with col2:
        save = st.checkbox("Register")

    return actif, save

def NewGerant(actif):

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
                compteur = len(listGerant.getListUtilisateur())
                try:
                    writeDataBase = Access(con_string2)
                    requete = """INSERT INTO utilisateur(firstName, lastName, avis, variation, commentaire, actif) VALUES (?,?,?,?,?,?)"""
                    data = (gerant.getFirstName(), gerant.getLastName(), gerant.getAvis(), gerant.getVariation(), gerant.getCommentaire(), gerant.getActif())
                    writeDataBase.insert(requete,data)
                    writeDataBase.commit()
                    writeDataBase.close()
                except pyodbc.Error as e:
                    print("Error in connection")
        if (gerant.getFirstName()!="" and gerant.getLastName()!=""):
            if soumettre:
                st.success("The rating of the portfolio manager, {} {}, has been successfully registered.".format(gerant.getFirstName(),gerant.getLastName()))
        else:
            st.warning("Please complete the form before sending.")

def ReadDB():
    df = pd.DataFrame()
    try: 
        readDataBase = Access(con_string2)
        utilisateur = 'utilisateur'
        requete = "SELECT * FROM {}".format(utilisateur)
        data = readDataBase.query(requete)
        df = pd.DataFrame((tuple(t) for t in data)) 
        readDataBase.close()
    except pyodbc.Error as e:
        print("Error in connection")
    
    return df

def meanVariation():
    st.subheader("Variation")
    mean = 0
    try: 
        readDataBase = Access(con_string2)
        utilisateur = 'utilisateur'
        requete = "SELECT variation FROM {}".format(utilisateur)
        data = readDataBase.query(requete)
        mean = round(float(pd.DataFrame((tuple(t) for t in data)).mean()),2)
        readDataBase.close()
    except pyodbc.Error as e:
        print("Error in connection")
    st.write("The average of the variation is : {}".format(mean))

def countAvis():
    st.subheader("Opinion")
    countShort, countNeutre, countLong, total = 0, 0, 0, 0
    try:
        readDataBase = Access(con_string2)
        utilisateur = 'utilisateur'
        requete = "SELECT * FROM {}".format(utilisateur)
        data = readDataBase.query(requete)
        df = pd.DataFrame((tuple(t) for t in data)) 
        readDataBase.close()
    except pyodbc.Error as e:
        print("Error in connection")
    for i in df.index :
        if(df[i][2] == "Short"):
            countShort += 1
        elif(df[i][2] == "Neutre"):
            countNeutre += 1
        elif(df[i][2] == "Long"):
            countLong += 1
    total = countShort + countNeutre + countLong
    pourcentageShort, pourcentageNeutre, pourcentageLong = round((countShort/total)*100,2), round((countNeutre/total)*100,2), round((countLong/total)*100,2)
    st.write("Short : {} | Percentage : {} %".format(countShort,pourcentageShort))
    st.write("Neutre : {} | Percentage : {} %".format(countNeutre,pourcentageNeutre))
    st.write("Long : {} | Percentage : {} %".format(countLong,pourcentageLong))


def AffCommentaire():
    st.subheader("Note")
    try:
        readDataBase = Access(con_string2)
        utilisateur = 'utilisateur'
        requete = "SELECT * FROM {}".format(utilisateur)
        data = readDataBase.query(requete)
        df = pd.DataFrame((tuple(t) for t in data)) 
        readDataBase.close()
    except pyodbc.Error as e:
        print("Error in connection")
    for i in df.index:
        st.write(df[0][i] + " " + df[1][i] + " commented : " + df[4][i])


def Reporting():

    st.header("Scoring Result")
    meanVariation()
    countAvis()
    AffCommentaire()
    with st.expander("Ratings DataBase"):
        try: 
            readDataBase = Access(con_string2)
            utilisateur = 'utilisateur'
            requete = "SELECT * FROM {}".format(utilisateur)
            data = readDataBase.query(requete)
            dfDB = pd.DataFrame((tuple(t) for t in data),columns = ["FirstName","LastName","Opinion","Variation","Note","Asset"])
            st.dataframe(dfDB) 
            readDataBase.close()
        except pyodbc.Error as e:
            print("Error in connection")

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

    actif = ""
    df = ReadDB()
 
    if(df.empty):
        actif, save = Select_Actif_NbGerant()
    else:
        actif = str(df[5][0])
        save = True

    if(save==True):
        st.success("The Asset is {}.".format(actif))
        NewGerant(actif)
        selected = st.checkbox("View Report")

        if(selected):
            Reporting()
            removeBBD = st.checkbox("Reset")
            if(removeBBD):
                RemoveBDD()
                
Main()
