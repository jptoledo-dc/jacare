import streamlit as st
import pandas as pd
from PIL import Image
import os
import datetime
import pytz

st.set_page_config(layout="wide",page_title="Jacaratinha Brinquedos",page_icon = "Jacaratinha.png")
img, name = st.columns([1,4])
img.image("Jacaratinha.png",width=100)
name.title("Base de Dados - Jacaratinha Brinquedos")
bdd = pd.read_csv(r"database.csv", encoding="utf-8", sep="\t")
bdd.columns= ["Cod. Interno","SKU","Nome Produto", "Reforço", "Tamanho Embalagem","Corredor","Localização","Anuncio?","Imagem"]

radio = st.radio("",["Resumo de Pedidos","Consulta","Imprimir Etiquetas","Alterar informações"],horizontal = True)

if radio == "Resumo de Pedidos":
    st.header("Resumo dos Pedidos")
    uf, pb = st.columns([5,1])
    uploaded_file = uf.file_uploader("Suba um arquivo RelPedidosCorImp.xls", type=["xlsx", "xls"])
    if uploaded_file:
        if pb.button("Enviar o arquivo"):
             # Nome do arquivo
            file_name = uploaded_file.name

            # Caminho onde o arquivo será salvo (mesma pasta do script)
            file_path = os.path.join(os.getcwd(), file_name)

            # Salva o arquivo na pasta local
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.success(f"Arquivo {file_name} salvo com sucesso na pasta do script.")
    file_name = "RelPedidosCorImp.xls"
    file_path = os.path.join(os.getcwd(), file_name)
    if os.path.isfile(file_path):
        st.subheader("Informações pertinentes")
        col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1.5])
        st.subheader("Resumo das Embalagens")
        bag1, bag2, bag3, bag4, bag5, bag6 = st.columns([1.2,1,1,1,1,1])

        #Base de dados com SKU
        
        #Lê o arquivo xls e retorna a tabela
        pedidos = pd.read_excel(file_name)
        pedidos = pedidos.iloc[:-1]
        pedidos["Cod Pedido"] = pedidos["Pedido"].str[:6]
        pedidos.columns = ["Quantidade","SKU","Data","Pedido com Preço", "Pedido"]

        pedidoSKU = pd.merge(bdd, pedidos, on="SKU",how="right")
        pedidoSKU['Faturamento'] = pedidoSKU['Pedido com Preço'].str.replace(',','.',regex=False).str[19:].astype(float)
        total_pedidos = pedidoSKU.groupby(['SKU','Nome Produto','Tamanho Embalagem'])['Quantidade'].sum().reset_index().sort_values(by="Quantidade",ascending=False)
        total_pedidos['Quantidade'] = total_pedidos['Quantidade'].astype(int)

        st.markdown(total_pedidos.style.hide(axis="index").to_html(), unsafe_allow_html=True)


        col1.metric("Total de Pacotes",pedidoSKU['Pedido'].nunique())
        col2.metric("Total de Produtos",int(pedidoSKU['Quantidade'].sum()))
        col3.metric("Produtos diferentes",pedidoSKU['SKU'].nunique())
        tot_fatura = "R$"+str(round(pedidoSKU['Faturamento'].sum(),2))
        col4.metric("Não Cadastrado",pedidoSKU['Nome Produto'].isna().sum())
        col5.metric("Total de Faturamento",tot_fatura.replace('.',','))

        #['Muito Pequeno (20 x 34)','Pequeno (26 x 36)','Médio (32 x 40)','Grande (40 x 60)','Muito Grande (50 x 60)','Personalizado']
        bag1.metric("M Pequeno (20x34)",(pedidoSKU['Tamanho Embalagem'] == 'Muito Pequeno (20 x 34)').sum())
        bag2.metric("Pequeno (26x36)",(pedidoSKU['Tamanho Embalagem'] == 'Pequeno (26 x 36)').sum())
        bag3.metric("Médio (32x40)",(pedidoSKU['Tamanho Embalagem'] == 'Médio (32 x 40)').sum())
        bag4.metric("Grande (40x60)",(pedidoSKU['Tamanho Embalagem'] == 'Grande (40 x 60)').sum())
        bag5.metric("M Grande(50x60)",(pedidoSKU['Tamanho Embalagem'] == 'Muito Grande (50 x 60)').sum())
        bag6.metric("Personalizado",(pedidoSKU['Tamanho Embalagem'].str.contains('Personalizad', case=False, na=False).sum()))

        pedidos = pedidos.reindex(columns=['Pedido','Quantidade','SKU','Data','Pedido com Preço'])
        pedidos['Lote'] = datetime.datetime.today().strftime("%d/%m/%Y")
        fuso = pytz.timezone('America/Sao_Paulo')
        pedidos['Hora'] = datetime.datetime.now(fuso).strftime("%H:%M")
        pedidos['Data'] = pedidos['Data'].dt.strftime("%d/%m/%Y")
        pedidos['Quantidade'] = pedidos['Quantidade'].astype(int)
        indices_vazios = pedidos[pedidos['Pedido'].isna() | (pedidos['Pedido'] == '')].index

        for indice in indices_vazios:
            pedido_anterior = pedidos.loc[indice-1, 'Pedido']
            ped_original = str(pedido_anterior)+"-1"
            ped_novo = str(pedido_anterior)+"-2"
            pedidos.loc[indice-1,'Pedido'] = ped_original
            pedidos.loc[indice,'Pedido'] = ped_novo
        pedidos.set_index('Pedido', inplace=True)
        st.write(pedidos)

        #with open('planilha_isa.txt','w+') as p:
        #    for index, row in pedidos.iterrows():
        #        p.write(f"{row['Pedido']},{row['Quantidade']},{row['SKU']},{row['Data']},{row['Pedido com Preço']},{row['Lote']},{row['Hora']}\n".replace(",","\t"))
        #    p.close()
        
        #with open('planilha_isa.txt','r+') as p:
        #    st.text_area(label="Copie",value=p.read())


    else:
        st.subheader("Por favor, suba um arquivo RelPedidosCorImp.xls")
        st.write(f"O arquivo '{file_name}' não foi encontrado no diretório.")        

elif radio == "Consulta":
    st.header("Consulta de Produtos")
    filtros, imagens = st.columns([2,4])
    cod_produto = filtros.selectbox("Selecione o produto",bdd["SKU"].sort_values(ascending=True))
    filtros.subheader("Descrição do Produto : \n"+bdd.loc[bdd['SKU'] == cod_produto, 'Nome Produto'].values[0])
    filtros.subheader("Tamanho da Embalagem: \n"+bdd.loc[bdd['SKU'] == cod_produto, 'Tamanho Embalagem'].values[0])
    filtros.subheader("Possui anuncio ativo? \n"+bdd.loc[bdd['SKU'] == cod_produto, 'Anuncio?'].values[0])
    filtros.subheader("Precisa reforçar acetato? \n"+bdd.loc[bdd['SKU'] == cod_produto, 'Reforço'].values[0])

    loc = bdd.loc[bdd['SKU'] == cod_produto, 'Localização'].values[0]
    imagem_valor =  bdd.loc[bdd['SKU'] == cod_produto, 'Imagem'].values[0]
    imagens.image(imagem_valor, width=500)
    


    try:
        with st.expander("Localização"):
            filtros.subheader("Localização:  "+loc)
            mapa = Image.open(f"mapa{loc}.png")
            st.image(mapa)
    except:
        st.title("Não contém localização")
    
elif radio == "Imprimir Etiquetas":
    st.header("Imprimir Etiquetas")
    entrada_de_dados = st.text_area("Cole as duas colunas (Pedido ATOM e SKU):")
    fragmentado = entrada_de_dados.split("\n")
    def_largura = 800
    def_altura = 150
    def_thickness = 5
    molde = f"^GB{def_largura},{def_altura},{def_thickness}^FS"

    #Acima de 15 é 50
    #Até 15 é 170
    #Gerador de Etiquetas
    lista_pronta = []
    impressao = []
    impressao.append("^XA\n")
    contador = 0
    field_origin_box = 0
    field_origin_text_width = 20
    tamanho_lista = len(fragmentado)
    cont_geral = 1
    if len(entrada_de_dados) >0:
        for linha in fragmentado:
            if contador < 7:
                if cont_geral != tamanho_lista:

                    if len(linha) >= 15:
                        field_origin_text = 50
                    else:
                        field_origin_text = 170
                    impressao.append(f"""
                            ^FO0,{field_origin_box}
                            ^GB{def_largura},{def_altura},{def_thickness}^FS
                            ^FO{field_origin_text},{field_origin_text_width}
                            ^AF,120,20
                            ^FD{linha}^FS
                            """)
                    contador += 1
                    field_origin_box += 150
                    field_origin_text_width += 150
                    cont_geral += 1
                else:
                    if len(linha) >= 15:
                        field_origin_text = 50
                    else:
                        field_origin_text = 170
                    impressao.append(f"""
                            ^FO0,{field_origin_box}
                            ^GB{def_largura},{def_altura},{def_thickness}^FS
                            ^FO{field_origin_text},{field_origin_text_width}
                            ^AF,120,20
                            ^FD{linha}^FS
                            """)
                    impressao.append("\n^XZ\n")
                    lista_pronta.append("".join(impressao))
            elif contador == 7:
                if len(linha) >= 15:
                        field_origin_text = 50
                else:
                        field_origin_text = 170
                impressao.append(f"""^FO0,{field_origin_box}
                                ^GB{def_largura},{def_altura},{def_thickness}^FS
                                ^FO{field_origin_text},{field_origin_text_width}
                                ^AF,120,20
                                ^FD{linha}^FS""")
                impressao.append("\n^XZ\n")
                contador = 0
                field_origin_box = 0
                field_origin_text_width = 20
                lista_pronta.append("".join(impressao))
                impressao = []
                impressao.append("^XA\n")
                cont_geral += 1


        resultado = "".join(lista_pronta).replace("	"," ")
        st.text_area(label="Copie e resultado!",value=resultado)
    else:
        pass

elif radio == "Alterar informações":
    col_sa, col_sb = st.columns([4,1])
    if 'acesso' not in st.session_state:
        st.session_state.acesso = False
    if not st.session_state.acesso:
        senha_acesso = col_sa.text_input("Insira a senha:",type="password")
        st.error("ATENÇÃO! ESSA ABA EXIGE PRIVILÉGIO DE ADMINISTRADOR, POR FAVOR, INSIRA A SENHA DE ACESSO:")
        if col_sb.button("Acessar"):
            if senha_acesso == "Batatinha123":
                st.success("Acesso garantido")
                st.session_state.acesso = True
            else:
                st.error("Senha errada, por favor, tente novamente!")
    if st.session_state.acesso:
        st.title("Alteração de Informações na base de dados")
        col_infos, col_alter = st.columns([2,3])
        prod_id = col_infos.selectbox("Selecione o produto que deseja alterar",bdd["SKU"].sort_values(ascending=True))
        infos_imagem =  bdd.loc[bdd['SKU'] == prod_id, 'Imagem'].values[0]
        col_infos.image(infos_imagem, width=500)

        at_ci = bdd.loc[bdd['SKU'] == prod_id, 'Cod. Interno'].values[0]
        at_sku = col_alter.text_input(label="SKU",value=bdd.loc[bdd['SKU'] == prod_id, 'SKU'].values[0])
        at_np = col_alter.text_input(label="Nome do Produto",value=bdd.loc[bdd['SKU'] == prod_id, 'Nome Produto'].values[0])
        lista_emb = ['Muito Pequeno (20 x 34)','Pequeno (26 x 36)','Médio (32 x 40)','Grande (40 x 60)','Muito Grande (50 x 60)','Caixa Personalizada','Embalagem Personalizada']
        indice = lista_emb.index(bdd.loc[bdd['SKU'] == prod_id, 'Tamanho Embalagem'].values[0])
        at_te = col_alter.selectbox(label="Tamanho da Embalagem",index=indice,options=lista_emb)
        at_loc = col_alter.text_input(label="Localização",value=bdd.loc[bdd['SKU'] == prod_id, 'Localização'].values[0])
        at_crd = col_alter.text_input(label="Corredor",value=bdd.loc[bdd['SKU'] == prod_id, 'Corredor'].values[0])
        at_anun = col_alter.text_input(label="Anuncio?",value=bdd.loc[bdd['SKU'] == prod_id, 'Anuncio?'].values[0])
        at_ref = col_alter.text_input(label="Reforço de Acetato",value=bdd.loc[bdd['SKU'] == prod_id, 'Reforço'].values[0])
        at_img = col_alter.text_input(label="Link da imagem (ML ou Shopee)",value=bdd.loc[bdd['SKU'] == prod_id, 'Imagem'].values[0])
        at_button = col_alter.button("Salvar as informações alteradas")
        if at_button:
            bdd.loc[bdd['SKU'] == prod_id, bdd.columns] = [at_ci, at_sku,at_np,at_ref,at_te,at_crd,at_loc, at_anun,at_img]
            bdd.to_csv('database.csv', index=False,sep="\t")
            st.success("Informações foram salvas com sucesso!")

elif radio == "Teste":
    st.title("Teste")

    caminho_arquivo = r"C:\Users\Usuario\Downloads\Fichas.xlsx"  # Substitua pelo caminho correto

    # Carregar o arquivo Excel
    excel_geral = pd.ExcelFile(caminho_arquivo)
    excel_fiscais = pd.read_excel(r"C:\Users\Usuario\Downloads\Fiscais.xlsx")

    # Listar todas as abas
    abas = excel_geral.sheet_names
    st.write("Abas disponíveis no arquivo Excel:")
    aba_selecionada = st.selectbox("Selecione a aba",abas)
    df = pd.read_excel(caminho_arquivo,sheet_name=aba_selecionada)
    filtro_sku = df[df['SKU'].str.contains('GP', na=False)]

    # Retornar apenas os valores da coluna 'SKU'
    valores_sku = filtro_sku['SKU'].tolist()
    produto = st.selectbox("Selecione o SKU",valores_sku)
    df_filtrado = df[df['SKU'] == produto]
    id = df_filtrado['ID'].iloc[0]
    geral, ficha, condicao = st.columns(3)
    for column in df_filtrado.columns:
            geral.write(f"{column}: \n{df_filtrado[column].iloc[0]}")
    fiscais_filtrado = excel_fiscais[excel_fiscais['Código do Anúncio'] == id]
    coluna_2 = fiscais_filtrado.columns[5:21]
    for column in coluna_2:
        if column in ['EAN','Origem','NCM','Unidade de medida comercial','Peso líquido','Peso bruto','Custo do produto','Descrição do produto para NF-e:']:
            ficha.write(f"{column}: \n{fiscais_filtrado[column].iloc[0]}")