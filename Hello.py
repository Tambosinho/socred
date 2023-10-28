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



    # FUNCAO PARA REGISTRAR NOVA LINHA COM VALORES DO SUBMIT FORM

    def newline_reg(mem, act, momento):
        return pd.DataFrame({"membroNome": [mem], "atividadeNome": [act], "momento":[momento]}, index=[0])



    # AQUI COMECA O CODIGO

    def reg_query():
        return conn.query(sql = '''
        SELECT 
            "atividadeNome", "membroNome", "momento"
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
        "Lavar louca"
    ]

    st.subheader("Adicione um registro de atividade")

    with st.form(key="form1"):
        act = st.selectbox("Atividade", act_list)
        mem = st.selectbox("Membro", mem_list)
        momento = datetime.datetime.now()

        submit = st.form_submit_button("Enviar")

    if submit:

        registros = reg_query()

        st.success(f"{mem} adicionou atividade {act} com sucesso")
        
        # Create a new DataFrame for the record
        new_record = newline_reg(mem, act, momento)
        
        # Concatenate the new record with the existing registros DataFrame
        new_registros = pd.concat([registros, new_record])

        conn.update(worksheet="registros", data = new_registros )


    ### DIVIDER
    st.divider()

    ### AGORA VAMOS COMPUTAR OS PONTOS DE CADA MEMBRO ###
    reg = reg_query()
    act = act_query()
    mem = mem_query()

    pontuacao_minima = 168

    # Junta tabelas
    comp_tab = reg.join(act.set_index("atividadeNome"), on ="atividadeNome")

    # group_by membroNome e sum(points), depois sorta DESC
    pontuacoes = pd.DataFrame(comp_tab.groupby(["membroNome"]).sum().sort_values(by=["points"], ascending=False)["points"]).fillna(0)

    pontuacoes["progress"] = round(pontuacoes["points"]*100/pontuacao_minima)


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


                cont = st.container()
                if name == pontuacoes.index[0]:
                    cont.subheader(f":crown: {name}")
                else:
                    cont.subheader(f"{name}")
                

                cont.progress(int(prog), text=f"{pontos} pts  •  {prog}%")


                if prog >=100:
                    cont.write(":white_check_mark: Congrats!")
                
            except KeyError:
                continue


if __name__ == "__main__":
    run()
