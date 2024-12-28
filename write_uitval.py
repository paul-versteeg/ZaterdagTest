from datetime import datetime
import xml.etree.ElementTree as ET
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='read-boekh.log', level=logging.INFO, format='%(asctime)s - %(levelname)s ; %(filename)s/%(funcName)s ; regelnr:%(lineno)d ; %(message)s')


def write_xml(record):
    today = datetime.today()
    formatted_date = today.strftime("%Y%m%d%H%M%S%f")
    file_path_uitval = ("uitval/uitval-" + formatted_date +".xml")

    root = ET.Element("data")  # Maak de root-element
    # item = ET.SubElement(root, "item"
    item = ET.SubElement(root, "item")

    id_elem = ET.SubElement(item, "datum")
    id_elem.text = str(record[0])
    id_elem = ET.SubElement(item, "bedrag_debet")
    id_elem.text = str(record[1])
    id_elem = ET.SubElement(item, "bedrag_credit")
    id_elem.text = str(record[2])
    id_elem = ET.SubElement(item, "categorie_nr")
    id_elem.text = str(record[3])
    id_elem = ET.SubElement(item, "omschrijving")
    id_elem.text = ""

    try:
        tree = ET.ElementTree(root)
        tree.write(file_path_uitval, encoding='utf-8', xml_declaration=True)
        logger.info("bestand uitval geschreven")
        return True
    except:
        logger.error("Het schrijven van " + file_path_xml + "  is mislukt")
        return False


    def main(record):
        write_xml(record)
        exit()


    if __name__ == '__main__':
        main(record)
        # end of file
