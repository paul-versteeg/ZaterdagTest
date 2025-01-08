

def main():

    imp_host = 'localhost'  # vervang 'your_host' door het adres van je MySQL server, bijv. 'localhost'
    imp_user = 'root'  # vervang 'your_username' door je MySQL gebruikersnaam
    imp_password = 'babylon'  # vervang 'your_password' door je MySQL wachtwoord
    imp_database = 'finance'  # laat leeg als je zonder bepaalde databse wilt testen

    database_data = [
        imp_host,
        imp_user,
        imp_password,
        imp_database
    ]

    return database_data

if __name__ == '__main__':
    main()
    # end of file


