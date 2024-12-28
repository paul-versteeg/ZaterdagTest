import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='read-boekh.log', level=logging.INFO, format='%(asctime)s - %(levelname)s ; %(filename)s/%(funcName)s ; regelnr:%(lineno)d ; %(message)s')



def main(var_import):

    if var_import == "select_query_datum":
        select_query_datum = """SELECT * FROM finance.datum where iddatum = (%s);"""
        return(select_query_datum)
    elif var_import == "select_query_categorie":
        select_query_categorie = """SELECT * FROM finance.categorie where idcategorie = (%s);"""
        return(select_query_categorie)
    elif var_import == "insert_query_transaction":
        insert_query_transaction = """INSERT INTO `finance`.`transactie` (`fk_datum`, `soort_transactie`, `bedrag`, `fk_categorie`, `fk_bank`) VALUES (%s, %s, %s, %s, %s);"""
        return(insert_query_transaction)
    elif var_import =="insert_query_datum":
        insert_query_datum = """INSERT INTO `finance`.`datum` (`iddatum`, `jaar`, `maand_nr`, `maand_naam`, `week_nr`) VALUES (%s, %s, %s, %s, %s);"""
        return(insert_query_datum)
    else:
        return False


if __name__ == '__main__':
    main()
    # end of file


