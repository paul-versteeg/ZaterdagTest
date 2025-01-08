import mysql.connector
from mysql.connector import Error
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='read-boekh.log', level=logging.INFO, format='%(asctime)s - %(levelname)s ; %(filename)s/%(funcName)s ; regelnr:%(lineno)d ; %(message)s')



def test_connection(imp_host, imp_user, imp_password, imp_database):
    try:
        # Verbinding maken met de MySQL database
        connection = mysql.connector.connect(
            host = imp_host,
            user = imp_user,
            password = imp_password,
            database = imp_database,
            # vervang 'your_database' door de naam van je database, of laat leeg voor alleen verbinding
        )

        if connection.is_connected():
            db_info = connection.get_server_info()
            logging.info(f"Succesvol verbonden met MySQL server versie {db_info}")
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            logging.info(f"Verbonden met database: {record}")

    except Error as e:
        logging.error(f"Fout bij verbinding met MySQL: {e}")
        return False

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            return True
            logging.info("MySQL verbinding is gesloten")


def main():
    imp_host = 'localhost'  # vervang 'your_host' door het adres van je MySQL server, bijv. 'localhost'
    imp_user = 'root'  # vervang 'your_username' door je MySQL gebruikersnaam
    imp_password = 'babylon'  # vervang 'your_password' door je MySQL wachtwoord
    imp_database = 'test_db_01'  # laat leeg als je zonder bepaalde databse wilt testen
    # Roep de functie aan om de verbinding te testen
    test_connection(imp_host, imp_user, imp_password, imp_database)


if __name__ == '__main__':
    main()