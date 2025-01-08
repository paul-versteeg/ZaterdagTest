import numpy as np
import pandas as pd
from datetime import datetime
import check_mysql_connectie
import mysql.connector
from mysql.connector import Error
import xml.etree.ElementTree as ET
import database_names
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='read-boekh.log', level=logging.INFO, format='%(asctime)s - %(levelname)s ; %(filename)s/%(funcName)s ; regelnr:%(lineno)d ; %(message)s')


def db_online(database_data):

    # controleren of de database werkelijk bestaat en online is
    if check_mysql_connectie.test_connection(database_data[0], database_data[1], database_data[2], database_data[3]):
        return True
    else:
        return False


def bepaal_file_path_xml(var_path):
    today = datetime.today()
    formatted_date = today.strftime("%Y%m%d%H%M")
    var_path = ("xml" + '/' + formatted_date + ".xml")
    return (var_path)


def read_xls(file_path_xls, file_path_xml):

    try:
        df = pd.read_excel(file_path_xls, sheet_name='stuurkaart', usecols=[1, 2])
    except FileNotFoundError:
        logger.error("File not found")
        return False
    except pd.errors.EmptyDataError:
        logger.error("File is empty")
        return False
    except pd.errors.ParserError:
        logger.error("File is not a valid Excel file")
        return False
    except Exception:
        logger.error("An error occurred while reading the file")
        return False

    filtered_df = df.notnull()  # bepaal van elke cell of die leeg is (False) of waarde bevat (True)

    # schrijf xml bestand
    root = ET.Element("data")  # Maak de root-element

    for i in range(5, len(df)):   # ga in de tabel alles langs vanaf de 5e rij tot einde
        if filtered_df.iloc[i,0] == True and filtered_df.iloc[i,1] == True:
            cell_value1 = df.iloc[i, 0]
            cell_value2 = str(df.iloc[i, 1])
            item = ET.SubElement(root, "item")
            id_elem = ET.SubElement(item, "omschrijving")
            id_elem.text = cell_value1
            code_elem = ET.SubElement(item, "code")
            code_elem.text = cell_value2

        tree = ET.ElementTree(root)
        tree.write(file_path_xml, encoding='utf-8', xml_declaration=True)

    return True


def lees_xml(file_path_xml, records):

    try:
        # Parse het XML-bestand
        tree = ET.parse(file_path_xml)
        root = tree.getroot()

        # Doorloop elk 'item' element in het XML-bestand en plaats ze in het array records
        for item in root.findall('item'):
            cat_omschrijving = item.find('omschrijving').text
            cat_nr = item.find('code').text
            soort_cat = "leeg"
            records.append((cat_nr, cat_omschrijving, soort_cat))

        return records

    except Error as e:
        logger.error("Error %d: %s", e.args[0], e.args[1])
        return False


def add_records_db(records, database_data):

    connection = mysql.connector.connect(
        host=database_data[0],
        user=database_data[1],  
        password=database_data[2], 
        database=database_data[3]
    )
    if connection.is_connected():
        cursor = connection.cursor()
        pass
    else:
        logger.error("Geen toegang tot database")
        return False

    insert_query = """INSERT INTO `finance`.`categorie` (`idcategorie`, `omschrijving`, `soort`) VALUES (%s, %s,%s)"""
    for record in records:
        try:
            cursor.execute(insert_query, record)

        except mysql.connector.Error as err:
            if err.args[0] == 1062:
                logger.error("Er is een fout: {}".format(err))
            else:
                logger.error("Er is een andere fout")
            return False

    connection.commit()
    logger.info(f"{cursor.rowcount} records succesvol ingevoegd.")
    cursor.close()
    connection.close()
    logger.info("Database gesloten")
    return True


def main():
    # de variabelen definieren voordat ze gebruikt worden in aanroepen
    var_path = ""
    file_path_xml = bepaal_file_path_xml(var_path)
    file_path_xls = 'xls/boekhouding2024.xlsx'
    test_value = ""
    records = []
    database_data = []

    database_data = database_names.main()

    if not db_online(database_data):  # testen of de database wel bereikbaar is
        logger.error("Database is niet bereikbaar")
        exit()

    if not read_xls(file_path_xls, file_path_xml):  # het spreadsheet inlezen en wegschrijven naar xml
        logger.error("Fout bij inlezen xls file")
        exit()

    if not lees_xml(file_path_xml, records):  # het xml bestand inlezen en inhoud opslaan in array Records
        logger.error("Fout bij inlezen xml file")
        exit()

    if not add_records_db(records, database_data):
        exit()


if __name__ == '__main__':
    main()
    # end of file