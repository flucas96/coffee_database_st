from sshtunnel import SSHTunnelForwarder
from sqlalchemy import create_engine
import pandas as pd
import paramiko
from paramiko import SSHClient
import pymysql.cursors
from time import sleep
import os
from sys import platform
import streamlit as st
import io


def add_coffee(df):
    coffee_table = "test_db_fl"
    upload_data(df,coffee_table)

def upload_data(df,table,if_exists='append',index=False):
    """
    df: hochzuladener df
    table: dashboard_id als str oder int. Zu finden in Projekteinstellungen unter Daten (ab der Zahl)
    if_exists: aus pd.to_sql.
    index: Übergabe vom Index
    """
    # Definitionen
    try_again = True
    while try_again == True:
        try:
        # Zugangsdaten
            user = st.secrets["db_user"]
            password = st.secrets["db_pass"]
            ip = st.secrets["db_ip"]
            port = 3306
            db = st.secrets["db_name"]
            ssh_user = st.secrets["ssh_user"]
            ssh_password= st.secrets["ssh_pass"]

            key = io.StringIO(st.secrets["ssh_key"])
            key = paramiko.RSAKey.from_private_key(key, password=ssh_password)
             
            # DF erstellen
            
            # SSH Tunnel aufbauen
            server = SSHTunnelForwarder(
                ip,
                ssh_username=ssh_user,
                ssh_password=ssh_password,
                remote_bind_address=('127.0.0.1', port),
                ssh_pkey=key,
            )
            
            server.start()
            
            #print(server.local_bind_port)  # show assigned local port
            # Ab hier besteht die Verbindung und wir können auf die Datenbank zugreifen
            
            engine = create_engine('mysql+pymysql://'+user+':'+password+'@localhost:'+str(server.local_bind_port)+'/'+db+'?charset=UTF8MB4')
            #df.to_sql(con=engine,name='test',if_exists='append')
            #engine.dispose() #Notwendig, sonst kann der Tunnel nicht geschlossen werden
            #server.stop() # Schließen des Tunnels. Kann bei Bedarf hier passieren oder zu einem späteren Zeitpunkt
            break
        except Exception as e: 
            print(e)
            sleep(1)
            try_again = False
            pass

    df.to_sql(con=engine,name=table,if_exists=if_exists,index=index)
    engine.dispose()
    server.stop()



def download_data(table,max_tries = 5):
    """
    df: hochzuladener df
    table: dashboard_id als str oder int. Zu finden in Projekteinstellungen unter Daten (ab der Zahl)
    if_exists: aus pd.to_sql.
    index: Übergabe vom Index
    """
    # Definitionen
    
    counter = 0

    while True:
        try:
        # Zugangsdaten
            user = st.secrets["db_user"]
            password = st.secrets["db_pass"]
            ip = st.secrets["db_ip"]
            port = 3306
            db = st.secrets["db_name"]
            ssh_user = st.secrets["ssh_user"]
            ssh_password= st.secrets["ssh_pass"]

            key = io.StringIO(st.secrets["ssh_key"])
            key = paramiko.RSAKey.from_private_key(key, password=ssh_password)

            # DF erstellen

            # SSH Tunnel aufbauen
            server = SSHTunnelForwarder(
                ip,
                ssh_username=ssh_user,
                ssh_password=ssh_password,
                remote_bind_address=('127.0.0.1', port),
                ssh_pkey=key,
            )

            server.start()

            #print(server.local_bind_port)  # show assigned local port
            # Ab hier besteht die Verbindung und wir können auf die Datenbank zugreifen

            engine = create_engine('mysql+pymysql://'+user+':'+password+'@localhost:'+str(server.local_bind_port)+'/'+db+'?charset=UTF8MB4')
            #df.to_sql(con=engine,name='test',if_exists='append')
            #engine.dispose() #Notwendig, sonst kann der Tunnel nicht geschlossen werden
            #server.stop() # Schließen des Tunnels. Kann bei Bedarf hier passieren oder zu einem späteren Zeitpunkt
            print("Successful")
            break
        except Exception as e: 
            counter +=1
            if counter >= max_tries:
                
                return "Connection Failed"
            print(f"{counter} - Try again - {e}")
            sleep(5)
            pass
    df = pd.read_sql_table(con=engine,table_name=str(table))
    engine.dispose()
    server.stop()
    return(df)