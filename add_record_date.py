import mysql.connector
from mysql.connector import Error
import xml.etree.ElementTree as ET
import bepaal_datum
import database_names
import retrieve_queries
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='read-boekh.log', level=logging.INFO, format='%(asctime)s - %(levelname)s ; %(filename)s/%(funcName)s ; regelnr:%(lineno)d ; %(message)s')


def inlezen_datums(file_path_xml, records):

    # hier xml lezen en de datums uit xml bestand in het array Records plaatsen
    try:
        # Parse het XML-bestand
        tree = ET.parse(file_path_xml)
        root = tree.getroot()

        # Doorloop elk 'item' element in het XML-bestand en plaats het datum veld ze in het array records
        for item in root.findall('item'):
            datum_xml = item.find('datum').text
            records.append((datum_xml))
        logger.info("Inlezen datums uit " + file_path_xml + " succesvol")
        return records

    except Error as e:
        logger.error("Inlezen datums uit " + file_path_xml + " niet gelukt")
        return False


def insert_datums(database_data, records):

    # eerst de database openen
    try:
        connection = mysql.connector.connect(
            host=database_data[0],
            user=database_data[1],
            password=database_data[2],
            database=database_data[3]
        )
    except:
        logger.error("Geen toegang tot database")
        return False

    cursor = connection.cursor()
    logger.info("Database geopend")

    #  de queries ophalen. Deze staan apart omdat ik ze dan makkelijker terug kan vinden
    select_query_datum = retrieve_queries.main("select_query_datum")
    if not retrieve_queries:
        logger.error("select_query_datum bestaat niet")
        return False  # als de query niet bestaat run False
    else:
        pass

    insert_query_datum = retrieve_queries.main("insert_query_datum")
    if not retrieve_queries:
        logger.error("insert_query_datum bestaat niet")
        return False  # als de query niet bestaat run False
    else:
        pass

    #  inlezen datums uit records. Als niet bestaat dan opvoeren
    #  error_bool boolean om te checken of er iets naar de foutlog is geschreven
    #  error_bool False = geen fout. Wordt op True gezet als er een fout is
    error_bool = False
    count = 0

    for record in records:

        record_datum = bepaal_datum.main(record)  # de short-date, maand, weeknr enz van deze datum ophalen

        try:
            cursor.execute(select_query_datum, (record_datum[0],))    #  kijken of de short-date al is opgevoerd. Short-date is het eerste item uit de array, dus item 0
            row = cursor.fetchall()
            if not row:                                         #  als de row leeg is dan bestaat short-date nog niet
                cursor.execute(insert_query_datum, record_datum)      #  met insert query short-date opvoeren
                count = count +1
            else:
                pass                                            #  short-date ebstat al wel, doorgaan naar volgende datum
        except mysql.connector.Error as err:
            logger.error("Fout lezen database" + "Errorcode: " + err.errno + " sql-state: " + err.sqlstate + " Message: " + err.msg)
            error_bool = True
            break

    logger.info(str(count) + " nieuwe datums opgevoerd")
    connection.commit()
    cursor.close()
    connection.close()

    if bool(error_bool):
        return False
    else:
        return True


def main(file_path_xml):

    records = []  # array records leeg aanmaken
    if not inlezen_datums(file_path_xml, records):
        logger.info("Inlezen datums afgebroken")
        return False
    else:
        # print("inlezen goed")
        # array Records ontdubbelen.
        # geen idee waarom dat hier wel lukt en als het in de functie inlezen_datums
        # wordt gedaan het niet terug wordt gegeven
        records = list(dict.fromkeys(records))  # duplicaten verwijderen uit lijst
        logger.info("Lijst met datums is ontdubbeld")

    database_data = database_names.main()   #  de gegevens van de database ophalen

    if not insert_datums(database_data, records):
        return False
    else:
        return True


if __name__ == '__main__':
    main()
    # end of file

