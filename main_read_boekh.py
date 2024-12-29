import add_record_date
import add_record_transaction
import lees_uitval
import pandas as pd
from datetime import datetime
import xml.etree.ElementTree as ET
import sys
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='read-boekh.log', level=logging.INFO, format='%(asctime)s - %(levelname)s ; %(filename)s/%(funcName)s ; regelnr:%(lineno)d ; %(message)s')

def read_maand(file_path_xls, maand, df, columns):

    try:
        df = pd.read_excel(file_path_xls, sheet_name=maand, usecols=columns)
        return df
    except FileNotFoundError:
        logging.error("bestand " + file_path_xls + " niet gevonden")
        return False
    except pd.errors.EmptyDataError:
        logging.error("Geen data gevonden in " + file_path_xls)
        return False
    except pd.errors.ParserError:
        logging.error("parse error in " + file_path_xls)
        return False
    except Exception:
        logging.error("Onbekende fout bij inlezen " + file_path_xls)
        return False


def write_xml(file_path_xml, df):

    # bepaal van elke cell of die leeg is (False) of waarde bevat (True)
    # als de cell in filtered-df false is dan is die cell in DF dus leeg
    # dit dient alleen om bij het inlezen van de dataset te bepalen of een rij gevuld is of leeg
    filtered_df = df.notnull()

    # in de dataset df alle lege velden (NaN) vervangen door de waarde 0
    df = df.fillna(0)
    # df = df.dropna(inplace=False)

    # root element van het xml file aanmaken
    root = ET.Element("data")  # Maak de root-element

    for i in range(12, len(df)):  # ga in de tabel alles langs vanaf de 5e rij tot einde
        if filtered_df.iloc[i, 0] == True:  # de eerste kolom(datum) is niet leeg

            for j in range(0, 5):
                cell_value = df.iloc[i, j]
                if j == 0:
                    datum_xml = cell_value
                elif j == 1:
                    bedrag_debet = cell_value
                elif j == 2:
                    bedrag_credit = cell_value
                elif j == 3:
                    categorie_nr = cell_value
                elif j == 4:
                    omschrijving = cell_value

            # record_xls = []
            record_xls = [
                datum_xml,
                bedrag_debet,
                bedrag_credit,
                categorie_nr,
                omschrijving
            ]

            # item = ET.SubElement(root, "item"
            item = ET.SubElement(root, "item")

            id_elem = ET.SubElement(item, "datum")
            id_elem.text = str(record_xls[0])
            id_elem = ET.SubElement(item, "bedrag_debet")
            id_elem.text = str(record_xls[1])
            id_elem = ET.SubElement(item, "bedrag_credit")
            id_elem.text = str(record_xls[2])
            id_elem = ET.SubElement(item, "categorie_nr")
            id_elem.text = str(record_xls[3])
            id_elem = ET.SubElement(item, "omschrijving")
            id_elem.text = record_xls[4]

        else:
            pass

    try:
        tree = ET.ElementTree(root)
        tree.write(file_path_xml, encoding='utf-8', xml_declaration=True)
        logger.info("Het schrijven van " + file_path_xml + "  is gelukt")
        return True
    except:
        logger.error("Het schrijven van " + file_path_xml + "  is mislukt")
        return False


def process_transactions(columns, jaar, maand, bank):

#    OPZET
#  1.Import JAAR verwerken tot bestandsnaam te lezen XLS
#  2.Controleren of dat bestand en de import MAAND als tabblad bestaan
#  3.Bestandsnaam bepalen van XML bestand waar de records uit de XLS in worden opgeslagen
#  4. XLS inlezen voor ING en het resultaat opslaan in DF
#  5. DF verwerken tot XML bestand
#  6. XML bestand inlezen en in de datums van de transacties opslaan na controles in tabel DATUM
#  7. XML bestand inlezen en transacties opslaan in tabel TRANSACTIE. Als CATEGORIE niet bestaat dan
#  transactie tijdelijk opslaan in xml-bestand UITVAL
#  8. UITVAL xml bestanden inlezen en converteren tot correcte CATEGORIE dan UITVAL bestand verwijderen

#  1 --- Import JAAR verwerken tot bestandsnaam te lezen XLS
#  bepalen welk jaar en welke maand ingelezen moeten worden en hoe
#  het in te lezen xls bestand heet en het te schrijven xml bestand gaat heten
    file_path_xls = 'xls/boekhouding' + jaar + '.xlsx'


# 2. controleren of het XLS met het tabblad bestaat
#  Als XLS niet is gevonden dan loggen en afbreken.
#  Anders verder gaan met verwerking
    try:
        xdf = pd.read_excel(file_path_xls, sheet_name=maand)
        pass
    except:
        logger.error("bestand " + file_path_xls + " niet gevonden")
        exit()

#  3. de naam van het xml bestand bepalen waar de ingelezen xls regels
#  in worden geplaatst. Bestandsnaam is geformatteerd in YYYYMMDDHHMM
    today = datetime.today()
    formatted_date = today.strftime("%Y%m%d%H%M%S")
    file_path_xml = ("xml" + '/' + formatted_date + ".xml")

#  4. de kolommen ophalen in het xls bestand en in array df plaatsen
#  Als de inlezen mislukt dan loggen en afbreken
    df = []  # list DF eerst leeg initialiseren
    df = read_maand(file_path_xls, maand, df, columns)

    try:  # als er toch een fout is opgetreden dan is df leeg, hier stoppen
        if not df:
            logger.error("Het inlezen van " + file_path_xls + " in DEF READ_MAAND is mislukt")
            logger.info('Finished')
            return False
        else:
            pass
    except:  # inlezen XLS gelukt. Verder met verwerking
        logger.info("Inlezen van " + file_path_xls + " in DEF READ_MAAND succesvol")
        pass

#  5. de inhoud van het XLS staat in DF. Deze wegschrijven in XMl bestand
#   Als de schrijven mislukt dan loggen en afbreken
    if not write_xml(file_path_xml, df):
        logger.info('Terminated')
        return False
    else:
        pass

#  6. XML bestand inlezen en de DATUMS OPSLAAN IN de database tabel DATUM
#   Als het inlezen mislukt dan loggen en afbreken
    if not add_record_date.main(file_path_xml):
        logger.info("Terminated")
        return False
    else:
        logger.info("Opvoeren nieuwe datums  succesvol")
        pass

#  7. XML bestand inlezen en DE TRANSACTIES OPSLAAN IN de database tabel TRANSACTIE
#   Als het inlezen mislukt dan loggen en afbreken.
    if not add_record_transaction.main(file_path_xml, bank):
        logger.info("Terminated")
        return False
    else:
        logger.info("Opvoeren nieuwe transacties succesvol")
        pass

#  8. XML bestand inlezen en DE UITVAL OPSLAAN IN de database tabel UITVAL
#   Als het inlezen mislukt dan loggen en afbreken
    directory_uitval = "uitval/"
    if not lees_uitval.main(directory_uitval, bank):
        logger.info("Terminated")
        return False
    else:
        pass

    return True


def main(jaar, maand):

    columns_ing=[8, 9, 10, 12, 13, 14]
    columns_asn=[0, 1, 2, 4, 5, 6]
    if not process_transactions(columns_ing, jaar, maand, bank="ING"):
        logger.error("Verwerking transacties ING mislukt")
        return False
    elif not process_transactions(columns_asn, jaar, maand, bank="ASN"):
        logger.error("Verwerking transacties ASN mislukt")
        return False
    else:
        pass

    return True


if __name__ == '__main__':

    logger.info("-" * 40)       #  regel met - 40 keer zodat het makkelijker leesbaar is
    logger.info('Started')      #  loggen dat het script gestart is

    if len(sys.argv) == 3:       #  testen of er wel command line argumenten zijn
        jaar = sys.argv[1]      #  eerste command line argument is JAAR
        maand = sys.argv[2]     #  tweede command line argument is MAAND
    else:
        logger.error("Jaar en Maand niet correct opgegeven opgegeven")
        exit(1)

    if not main(jaar, maand):
        logger.info("closed met fouten")
        exit(1)                 #  de logica in MAIN aanroepen

    logger.info("closed")       #  het script afsluiten
    exit(0)
    # end of file

