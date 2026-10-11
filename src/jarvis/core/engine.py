class JarvisEngine:
    """
    Motore principale di J.A.R.V.I.S.
    Gestisce l'avvio e lo stato del sistema.
    """

    def __init__(self):
        self.name = "J.A.R.V.I.S."
        self.status = "offline"

    def start(self):
        self.status = "online"

        print(f"{self.name} is starting...")
        print(f"System status: {self.status}")

    def shutdown(self):
        self.status = "offline"

        print(f"{self.name} shutting down...")
        print(f"System status: {self.status}")

    def get_status(self):
        return self.status