from datetime import datetime


class SystemModule:
    def get_time(self) -> str:
        current_time = datetime.now().strftime("%H:%M")
        return f"Sono le {current_time}."

    def get_date(self) -> str:
        current_date = datetime.now().strftime("%d/%m/%Y")
        return f"Oggi è il {current_date}."

    def get_status(self) -> str:
        return "Tutti i sistemi sono operativi."