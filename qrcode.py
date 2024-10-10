import streamlit as st
import pandas as pd
from PIL import Image
import win32print

st.set_page_config(layout="wide",page_title="Jacaratinha Brinquedos",page_icon = "Jacaratinha.png")
img, name = st.columns([1,4])
img.image("Jacaratinha.png",width=100)
name.title("Base de Dados - Jacaratinha Brinquedos")
bdd = pd.read_csv(r"database.csv", encoding="utf-8", sep="\t")
bdd.columns= ["Cod. Interno","SKU","Nome Produto", "Reforço", "Tamanho Embalagem","Corredor","Localização","Anuncio?","Imagem"]

radio = st.radio("",["Resumo de Pedidos","QRCode","Consulta","Imprimir Etiquetas"],horizontal = True)

if radio == "Resumo de Pedidos":
    st.header("Resumo dos Pedidos")
    uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=["xlsx", "xls"])

    if uploaded_file:
        st.subheader("Informações pertinentes")
        col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1.5])
        st.subheader("Resumo das Embalagens")
        bag1, bag2, bag3, bag4, bag5, bag6 = st.columns([1.2,1,1,1,1,1])

        #Base de dados com SKU
        
        #Lê o arquivo xls e retorna a tabela
        pedidos = pd.read_excel(uploaded_file)
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


        bag1.metric("M Pequeno (20x34)",(pedidoSKU['Tamanho Embalagem'] == 'Muito Pequeno (20 x 34)').sum())
        bag2.metric("Pequeno (26x36)",(pedidoSKU['Tamanho Embalagem'] == 'Pequeno (26 x 36)').sum())
        bag3.metric("Médio (32x40)",(pedidoSKU['Tamanho Embalagem'] == 'Médio (32 x 40)').sum())
        bag4.metric("Grande (40x60)",(pedidoSKU['Tamanho Embalagem'] == 'Grande (40 x 60)').sum())
        bag5.metric("M Grande(50x60)",(pedidoSKU['Tamanho Embalagem'] == 'Muito Grande (50 x 60)').sum())
        bag6.metric("Personalizado",(pedidoSKU['Tamanho Embalagem'].str.contains('Personalizad', case=False, na=False).sum()))

    else:
        st.subheader("Por favor, suba um arquivo RelPedidosCorImp.xls")

elif radio == "QRCode":
    st.subheader("Leitor de QRCode")

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