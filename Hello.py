# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
from streamlit.logger import get_logger
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

LOGGER = get_logger(__name__)

def run():
    st.set_page_config(
        page_title="Atividades",
        page_icon=":fire:",
    )
  
    # CONEXAO COM DB GSHEETS E TESTE

    conn = st.experimental_connection("gsheets", type=GSheetsConnection)

    
    # DETERMINAR PONTUACAO MINIMA POR MES POR MEMBRO:

    pontuacao_minima = 300


    # FUNCAO PARA CALCULAR A FREQUENCIA DE REGISTROS POR SEMANA

    # def freq_semanal(df, coluna_tempo):
    #     seq_time = pd.to_datetime(df[coluna_tempo])

    #     week_day_counts = seq_time.dt.dayofweek.value_counts().sort_index()
    #     for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
    #         if day not in week_day_counts.index :
    #             week_day_counts[day] = 0 
    #     result_df = pd.DataFrame({'Day of Week': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],'Count': week_day_counts})
    #     return result_df

    # FUNCAO PARA REGISTRAR NOVA LINHA COM VALORES DO SUBMIT FORM

    def newline_reg(mem, act, momento):
        return pd.DataFrame({"membroNome": [mem], "atividadeNome": [act], "momento":[momento], "pontos":[pontos]}, index=[0])



    # AQUI COMECA O CODIGO

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

    def registros_do_mes(all_registers, dia_limite):
        from datetime import datetime
        dia_limite = dia_limite
        # Obtém a data atual
        hoje = datetime.now()
    
        # Calcula a data de início como o dia 27 do mês anterior
        data_inicio = hoje.replace(day=dia_limite, month=hoje.month-1, year=hoje.year) if hoje.day <= dia_limite else hoje.replace(day=10)
    
        # Filtra as atividades a partir da data de início
        atividades_filtradas = all_registers[pd.to_datetime(all_registers['momento']) >= pd.to_datetime(data_inicio)]
    
        return atividades_filtradas
    


    ### VAMOS COMPUTAR OS PONTOS DE CADA MEMBRO ###
    reg = registros_do_mes(reg_query(), 27)
    act_table = act_query()
    mem = mem_query()
    registros = reg_query()

    # Junta tabelas
    comp_tab = reg.join(act_table.set_index("atividadeNome"), on ="atividadeNome")

    # group_by membroNome e sum(points), depois sorta DESC
    pontuacoes = pd.DataFrame(comp_tab.groupby(["membroNome"]).sum().sort_values(by=["points"], ascending=False)["points"]).fillna(0)

    pontuacoes["progress"] = round(pontuacoes["points"]*100/pontuacao_minima)




    st.title("Gerenciamento de Trabalho - República FGV 2023 - Beta")

    mem_list = [
        "Tambosi",
        "Pedro",
        "Vinicius",
        "Lunardon",
        "Felipao",
        "Osmar",
        "Otavio"
    ]

    act_list = [
        "Limpar pia",
        "Limpar fogao",
        "Encher filtro",
        "Encher gelo",
        "Trocar lixo grande",
        "Lavar panos prato/chao",
        "Trocar lixo pequeno",
        "Limpar mesa",
        "Secar louca",
        "Lavar louca",
        "Louca diaria (completa)",
        "Compra comunitaria", 
        "Lavar Airfryer"
    ]

    st.subheader("Adicione um registro de atividade")

    with st.form(key="form1"):
        act_name = st.selectbox("Atividade", act_list)
        mem_name = st.selectbox("Membro", mem_list)
        momento = datetime.datetime.now()

        submit = st.form_submit_button("Enviar")

    if submit:

        pontos = act_table[act_table["atividadeNome"]==act_name]["points"]
        
        # Create a new DataFrame for the record
        new_record = newline_reg(mem_name, act_name, momento, pontos)
        
        # Concatenate the new record with the existing registros DataFrame
        new_registros = pd.concat([registros, new_record])

        conn.update(worksheet="registros", data = new_registros)

        st.success(f"{mem_name} adicionou atividade {act_name} com sucesso!")


    ### DIVIDER
    st.divider()


    ### CRIA TABELA COM RANKING
    st.subheader(body="Ranking com pontuações")
    st.dataframe(data = pontuacoes.rename(columns={"membroNome":"Membro", "progress":"Progresso(%)", "points":"Pontos"}), use_container_width = True )

    ### DIVIDER
    st.divider()


    ### CRIA DASHBOARD COM RANKINGS
    st.subheader("Progresso dos membros")

    # Define the number of columns you want to create
    num_columns = mem["membroNome"].size

    # Create the columns using a for loop
    columns = [st.columns(num_columns)]

    # Iterate through the series and add the data to the columns
    for i, name in enumerate(mem["membroNome"]):
        with columns[0][i]:
            try:
                pontos = int(pontuacoes[pontuacoes.index==name].loc[name, "points"]) #total pontos do membro
                prog = int(pontuacoes[pontuacoes.index==name].loc[name, "progress"]) #total progresso do membro
                name_upper = name.upper()

                cont = st.container()

                if name == pontuacoes.index[0]: # Adiciona coroinha no nome do 1o colocado
                    titulo_cor = str(name_upper)
                    cont.write(f":crown: :orange[{titulo_cor}]")
                    
                else:
                    titulo_cor = str(name_upper)
                    cont.write(f":blue[{titulo_cor}]")
                
                if prog < 100 :
                    cont.progress(int(prog), text=f"{pontos} pts  •  {prog}%")

                else: 
                    cont.progress(100, text=f"{pontos} pts  •  {prog}%")
                    cont.write(":white_check_mark: :green[Congrats!]")
                
            except KeyError:

                continue

    ### ADICIONA FREQUENCIA SEMANAL
    # st.table(freq_semanal(reg, "momento"))



if __name__ == "__main__":
    run()
