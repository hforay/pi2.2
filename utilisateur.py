class Utilisateur:
    def __init__(self,firstName,lastName, avis = "", variation = 0, commentaire = "", actif = ""):
        self.firstName = firstName
        self.lastName = lastName
        self.avis = avis
        self.variation = variation
        self.commentaire = commentaire
        self.actif = actif
    
    def getFirstName(self):
        return self.firstName
    
    def getLastName(self):
        return self.lastName
    
    def getVariation(self):
        return self.variation
    
    def getAvis(self):
        return self.avis
    
    def getCommentaire(self):
        return self.commentaire

    def getActif(self):
        return self.actif
        
    def setAvis(self, value):
        self.avis = value
        
    def setVariation(self, value):
        self.variation = value
        
    def setCommentaire(self, value):
        self.commentaire = value

    def setActif(self,value):
        self.actif = value
    
    def showInfo(self):
        listData = list()
        listData.append(self.firstName)
        listData.append(self.lastName)
        listData.append(self.avis)
        listData.append(self.variation)
        listData.append(self.commentaire)
        listData.append(self.actif)
        return listData