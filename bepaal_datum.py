from datetime import datetime
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='read-boekh.log', level=logging.INFO, format='%(asctime)s - %(levelname)s ; %(filename)s/%(funcName)s ; regelnr:%(lineno)d ; %(message)s')


def check_datum(imp_date, date_format='%Y-%m-%d %H:%M:%S'):

    try:
        # Probeer de datum te parseren volgens het opgegeven formaat
        datetime.strptime(imp_date, date_format)
        return True
    except ValueError:
        # Als er een ValueError optreedt, is de datum ongeldig
        return False


def convert_short_date(datetime_string):
    # Definieer het formaat van de input string
    input_format = '%Y-%m-%d %H:%M:%S'

    # Definieer het gewenste output formaat
    output_format = '%Y%m%d'  # korte datumnotatie

    # Converteer de string naar een datetime object
    dt_object = datetime.strptime(datetime_string, input_format)

    # Converteer het datetime object naar alleen de datum in het gewenste formaat
    short_date = dt_object.strftime(output_format)

    return short_date


def convert_month(datetime_string):
    # Definieer het formaat van de input string
    input_format = '%Y-%m-%d %H:%M:%S'

    # Definieer het gewenste output formaat
    output_format = '%m'  #%m is maand in nummer

    # Converteer de string naar een datetime object
    dt_object = datetime.strptime(datetime_string, input_format)

    # Converteer het datetime object naar alleen de datum in het gewenste formaat
    monthnr_str = dt_object.strftime(output_format)

    try:
        monthnr = int(monthnr_str)
    except ValueError:
        monthnr = 0

    return monthnr


def convert_month_name(monthnr):

    maanden = [
        "januari",
        "februari",
        "maart",
        "april",
        "mei",
        "juni",
        "juli",
        "augustus",
        "september",
        "oktober",
        "november",
        "december"]

    month_name = maanden[monthnr-1]  #  maand 1 is item 0 in de array "maanden"

    return month_name


def convert_weeknr(datetime_string):
    # Definieer het formaat van de input string
    input_format = '%Y-%m-%d %H:%M:%S'

    # Definieer het gewenste output formaat
    output_format = '%W'   # %W is weeknr

    # Converteer de string naar een datetime object
    dt_object = datetime.strptime(datetime_string, input_format)

    # Converteer het datetime object naar alleen de datum in het gewenste formaat
    weeknr = dt_object.strftime(output_format)

    return weeknr


def convert_jaar(imp_string):
    # Definieer het formaat van de input string
    input_format = '%Y-%m-%d %H:%M:%S'

    # Definieer het gewenste output formaat
    output_format = '%Y'  # korte datumnotatie

    # Converteer de string naar een datetime object
    dt_object = datetime.strptime(imp_string, input_format)

    # Converteer het datetime object naar alleen de datum in het gewenste formaat
    jaar = dt_object.strftime(output_format)

    return jaar


def main(imp_date):

    # eerst de import datum naar een string omzetten
    if not type(imp_date) == str:
        imp_date = str(imp_date)


    if not check_datum(imp_date):
        logger.error("Datum " + imp_date + " is ongeldig")
        exit()

    #  van de gevalideerde datum de veschillende aspecten ophalen
    short_date = convert_short_date(imp_date)
    monthnr = convert_month(imp_date)
    month_name = convert_month_name(monthnr)
    weeknr = convert_weeknr(imp_date)
    jaar = convert_jaar(imp_date)

    #  alle velden van datum vullen
    records_datum = [
        short_date,
        jaar,
        monthnr,
        month_name,
        weeknr]

    return records_datum


if __name__ == '__main__':
    main()
    # end of file