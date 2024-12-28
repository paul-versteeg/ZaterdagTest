import mysql.connector
from mysql.connector import Error
import xml.etree.ElementTree as ET
from decimal import Decimal
import bepaal_datum
import database_names
import retrieve_queries
import write_uitval
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='read-boekh.log', level=logging.INFO, format='%(asctime)s - %(levelname)s ; %(filename)s/%(funcName)s ; regelnr:%(lineno)d ; %(message)s')


def inlezen_transaction(file_path_xml, records):

    # hier xml lezen en de datums uit xml bestand in het array Records plaatsen
    """
    Lees een XML-bestand en plaats de datums uit het XML-bestand in het array Records

    Args:
        file_path_xml (str): Pad naar het XML-bestand
        records (list): Array om de leesresultaten in op te slaan

    Returns:
        bool: True als het inlezen is gelukt, anders False
    """
    try:
        # Parse het XML-bestand
        tree = ET.parse(file_path_xml)
        root = tree.getroot()

        # Doorloop elk 'item' element in het XML-bestand
        for item in root.findall('item'):
            # Extract data from each element within 'record'
            datum = item.find('datum').text
            bedrag_debet = item.find('bedrag_debet').text
            bedrag_credit = item.find('bedrag_credit').text
            categorie_nr = item.find('categorie_nr').text

            # Create a dictionary for the record
            record_data = [
                datum,
                bedrag_debet,
                bedrag_credit,
                categorie_nr
            ]

            # Append the dictionary to the records list
            records.append(record_data)

        logger.info("Inlezen transacties uit " + file_path_xml + " succesvol")
        return records

    except Error as e:
        logger.error("Inlezen datums uit " + file_path_xml + " niet gelukt")
        return False


def insert_transaction(database_data, records, bank):

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

    cursor = connection.cursor()        #  database openen
    logger.info("Database geopend")

    #  de queries ophalen. Deze staan apart omdat ik ze dan makkelijker terug kan vinden
    select_query_datum = retrieve_queries.main("select_query_datum")
    if not retrieve_queries:
        logger.error("select_query_datum bestaat niet")
        return False    #  als de query niet bestaat run False
    else:
        pass

    select_query_categorie = retrieve_queries.main("select_query_categorie")
    if not retrieve_queries:
        logger.error("select_query_categorie bestaat niet")
        return False    #  als de query niet bestaat run False
    else:
        pass

    insert_query_transaction = retrieve_queries.main("insert_query_transaction")
    if not retrieve_queries:
        logger.error("insert_query_transaction bestaat niet")
        return False    #  als de query niet bestaat run False
    else:
        pass


    count = 0       #  handmatige teller voor aantal opgevoerde records

    for record in records:      #  in records staan alle ingelezen mutaties. 1 voor 1 opvoeren
        error_bool = False
        zoek_datum = bepaal_datum.convert_short_date(record[0])   #  de datum eerst converteren naar YYYMMMDD
        #  het is onmogelijk dat de datum niet wordt gevonden. Deze wordt opgevoerd in ADD_RECORD_DATE
        #  maar voor de zekerheid toch maar even checken
        try:
            cursor.execute(select_query_datum, (zoek_datum,))    #  kijken of de short-date al is opgevoerd. Short-date is het eerste item uit de array, dus item 0
            row = cursor.fetchall()
            if not row:                                         #  als de row leeg is dan bestaat short-date nog niet
                error_bool = True
                logger.error("de datum " + zoek_datum + " is niet gevonden")
                if not write_uitval.write_xml(record):      #  datum bestaat niet. Dit had niet mogen gebeuren
                    return False                            #  de data wegschrijven in een uitval bestand
                    break
            else:
                pass                                            #  short-date bestaat al wel, doorgaan naar volgende datum
        except mysql.connector.Error as err:
            logger.error("Fout lezen database" + "Message: " + err.msg)
            break

        zoek_categorie = record[3]     #  de STR omzetten in INT om in databse op dit type te kunnen zoeken
        try:
            cursor.execute(select_query_categorie, (zoek_categorie,))  # kijken of de categorie al is opgevoerd. Short-date is het eerste item uit de array, dus item 0
            row = cursor.fetchall()
            if not row:  # als de row leeg is dan bestaat de categorie nog niet
                logger.warning("categorie " + str(zoek_categorie) + " is niet gevonden")
                error_bool = True
                if not write_uitval.write_xml(record):
                    return False
                    break
            else:
                pass  # het record kan nu opgevoerd worden
        except mysql.connector.Error as err:
            logger.error("Fout lezen database" + "Message: " + err.msg)
            break

        if not error_bool:          # er is geen fout in inlezen datum of categorie gevonden

            fk_datum = bepaal_datum.convert_short_date(record[0])

            if float(record[1]) != 0:
                soort_transactie = "D"
                bedrag = Decimal(record[1])
            elif float(record[2]) != 0:
                soort_transactie = "C"
                bedrag = Decimal(record[2])
            else:
                logger.error("transactie met datum " + str(zoek_datum) + " heeft geen bedrag. Bank:"  + bank)
                cursor.close()
                connection.close()
                return False

            fk_categorie = zoek_categorie

            if bank == "ING":
               fk_bank = "1"
            elif bank == "ASN":
               fk_bank = "2"
            else:
                logger.error("bank " + bank + " niet gevonden")
                cursor.close()
                connection.close()
                return False

            record_transactie = [
                fk_datum,
                soort_transactie,
                bedrag,
                fk_categorie,
                fk_bank
            ]
            try:
                cursor.execute(insert_query_transaction, record_transactie)
                logger.info("transactie met datum " + str(zoek_datum) + " opgevoerd")
            except mysql.connector.Error as err:
                logger.error("Fout bij opvoeren transactie met " + str(zoek_datum) + " Errorcode: " + str(err.errno) + " sql-state: " + str(err.sqlstate) + " Message: " + err.msg)

            count+=1

    logger.info(str(count) + " transacties opgevoerd")
    connection.commit()
    cursor.close()
    connection.close()
    logger.info("Database gesloten")
    return True


def main(file_path_xml, bank):

    records = []  # array records leeg aanmaken

    if not inlezen_transaction(file_path_xml, records):
        return False
    else:
        pass

    database_data = database_names.main()   #  de gegevens van de database ophalen

    if not insert_transaction(database_data, records, bank):
        return False
        exit()
    else:
        return True
        pass

if __name__ == '__main__':
    main()
    # end of file

