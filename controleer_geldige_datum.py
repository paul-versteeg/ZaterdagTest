from datetime import datetime

def main(datum_string, datum_formaat="%Y-%m-%d %H:%M:%S"):
    try:
        # Probeer de datum te parsen volgens het opgegeven formaat
        datetime.strptime(datum_string, datum_formaat)
        return True
    except ValueError:
        # Als er een ValueError optreedt, is de datum ongeldig
        return False