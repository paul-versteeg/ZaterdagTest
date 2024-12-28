import os
import xml.etree.ElementTree as ET
import bepaal_datum
import add_record_transaction
import database_names
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='read-boekh.log', level=logging.INFO, format='%(asctime)s - %(levelname)s ; %(filename)s/%(funcName)s ; regelnr:%(lineno)d ; %(message)s')

def inlezen_uitval_files(directory_uitval: object, uitval_files, database_data, bank) -> object:

    records = []    # array records leeg aanmaken. Records wordt gevuld met aangepaste records

    for bestand in uitval_files:  #  alle files met uitval 1 voor 1 doorlopen

        uitval_bestand = os.path.join(directory_uitval, bestand)  # directorynaam ervoor plaatsen

        try:
            # Parse het XML-bestand
            tree = ET.parse(uitval_bestand)
            root = tree.getroot()
            for item in root.findall('item'):
                datum = item.find('datum')
                bedrag_debet = item.find('bedrag_debet')
                bedrag_credit = item.find('bedrag_credit')
                categorie_nr = item.find('categorie_nr')
                omschrijving = item.find('omschrijving')

                # Controleer of elk element aanwezig is
                datum = datum.text if datum is not None else "Onbekend"
                bedrag_debet = float(bedrag_debet.text) if bedrag_debet is not None else 0.0
                bedrag_credit = float(bedrag_credit.text) if bedrag_credit is not None else 0.0
                categorie_nr = int(categorie_nr.text) if categorie_nr is not None else 0
                omschrijving = omschrijving.text if omschrijving is not None else "Onbekend"

                try:
                    jaar = bepaal_datum.convert_jaar(datum)
                    if jaar is None:
                        logger.error("Jaar is Leeg")
                        exit()
                    elif (jaar == "2023" or jaar == "2022" or jaar == "2021"):
                        if categorie_nr == 10:
                            categorie_nr = 27
                            logger.info("categorie_nr veranderd naar: " + str(categorie_nr) + " bij: " + uitval_bestand)
                        elif categorie_nr == 15:
                            categorie_nr = 28
                    else:
                        logger.warning("Voor dit {jaar} geen categorie gedefineerd: " + uitval_bestand)

                except Exception as e:
                    logger.error(f"An error occurred: {e}")

                record_data = [
                    datum,
                    bedrag_debet,
                    bedrag_credit,
                    categorie_nr
                ]
                # Append the dictionary to the records list
                records.append(record_data)

        except Exception as e:
            logger.info(f"An error occurred: {e}")
            pass

    if not add_record_transaction.insert_transaction(database_data, records, bank):
        logger.error("de uitvalbestanden werden niet opgevoerd")
        return False
    else:
        logger.info("de uitvalbestanden werden succesvol opgevoerd")
        return True


def remove_files(directory_uitval, file_list_uitval):

    for bestand in file_list_uitval:  #  alle files met uitval 1 voor 1 doorlopen

        uitval_bestand = os.path.join(directory_uitval, bestand)  # directorynaam ervoor plaatsen

        try:
            # Verwijder het bestand
            os.remove(uitval_bestand)
            logger.info(f"Bestand '{uitval_bestand}' is succesvol verwijderd.")
        except FileNotFoundError:
            logger.info(f"Bestand '{uitval_bestand}' bestaat niet.")
            return False
        except PermissionError:
            logger.info(f"Geen toestemming om het bestand '{uitval_bestand}' te verwijderen.")
            return False
        except Exception as e:
            logger.info(f"Er is een fout opgetreden bij het verwijderen van de uitvalbbestanden: {e}")
            return False

    return True

def main(directory_uitval, bank):

    logger.info("Start inlezen uitval bestanden in: " + directory_uitval)

    file_list_uitval = []

    try:
        file_list_uitval=os.listdir(directory_uitval)

        if (len(file_list_uitval)) > 0:
            logger.info(f"Uitvalbestanden gevonden in {directory_uitval}")
            pass
        else:
            #  er zijn geen uitval bestanden. het is niet nodig ze in te lezen en te verwijderen.
            #  de uitval-routine kan verlaten worden
            logger.info(f"Er zijn voor {bank} geen uitvalbestanden gevonden in {directory_uitval}")
            exit()
    except Exception as e:
        #  het inlezen zelf is niet gelukt. Dit is een error
        logger.error("Er is een fout opgetreden bij het lezen van de uitvalbestanden: {e}")
        return False

    database_data = database_names.main()
    if not inlezen_uitval_files(directory_uitval, file_list_uitval, database_data, bank):
        logger.error("Verwerking uitvalbestanden gestopt")
        return False
    else:
        pass

    if not remove_files(directory_uitval, file_list_uitval):
        logger.error("Bestanden niet verwijderd")
        return False
    else:
        return True


if __name__ == '__main__':
    directory_uitval="uitval/"
    main(directory_uitval, bank)