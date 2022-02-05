import pandas as pd
import streamlit as st

class Resultat:
    def __init__(self,listUtilisateur = list()):
        self.listUtilisateur = listUtilisateur
        
    def getListUtilisateur(self):
        return self.listUtilisateur

    def showInfoResult(self):
        listInfo = list()
        for i in self.listUtilisateur:
            listInfo.append(i.showInfo())
        df = pd.DataFrame(listInfo,columns = ["Name","LastName","Opinion","Variation","Note","Asset"])
        st.dataframe(df)

