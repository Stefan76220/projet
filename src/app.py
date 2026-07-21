from src.interface import InterfacePrincipale


class GenerateurFichesApp:

    def __init__(self):
        self.interface = InterfacePrincipale()

    def lancer(self):
        self.interface.lancer()