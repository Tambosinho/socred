import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# CONEXAO COM DB GSHEETS E TESTE

conn = st.experimental_connection("gsheets", type=GSheetsConnection)

def reg_query():
    return conn.query(sql = '''
    SELECT 
        "atividadeNome", "membroNome", "momento", "pontos"
    FROM 
        "registros"
    WHERE "membroNome" IS NOT NULL

    ''', spreadsheet="https://docs.google.com/spreadsheets/d/15_lPmkaCqF6KesLeyxm6HVLYn3MWl1Oq_tlU46dJcE0/edit#gid=0", ttl = 0.5)

def act_query():
    return conn.query(sql = ''' 
    SELECT "atividadeId", "atividadeNome", "points"
    FROM "atividades"
    WHERE "atividadeNome" is not null
                        
''' )

def mem_query():
    return conn.query(sql = ''' 
    SELECT "membroId", "membroNome"
    FROM "membros"
    WHERE "membroId" is not null
                        
''' )

table_members = mem_query()
table_act = act_query()
table_registers = reg_query()

table_members.to_csv(path_or_buf="tables/members.csv")
table_act.to_csv(path_or_buf="tables/activities.csv")
table_registers.to_csv(path_or_buf="tables/registros.csv")


