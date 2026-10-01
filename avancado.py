import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from function import load_base

st.session_state['dw'], st.session_state['dims'], st.session_state['meds'] = load_base()
with st.container(horizontal=True):
    st.badge(
        label="EDA - Exploratory Data Amalysis",
        color="orange",
        icon=":material/pivot_table_chart:"
    )
    st.badge(
        label="Visual Reports",
        color="green",
        icon=":material/pivot_table_chart:"
    )
tabs = st.tabs(['Redes', 'Cascata'])
with tabs[0]:
    dimensao = st.segmented_control(
        label='Dimensão',
        options=st.secrets['sankey'],
        selection_mode='multi'
    )
    medida = st.segmented_control(
        label='Medida',
        options=['quantidade', 'vendas'],
        selection_mode='single'
    )
    if (len(dimensao) > 2) & (medida is not None):
        base = st.session_state['dw'].groupby(dimensao)[medida].sum().reset_index()
        rotulos = pd.DataFrame()
        sequencia = 0
        for dim in dimensao:
            distinto = base[dim].unique()
            for dist in distinto:
                linha = {
                    'sequencia': sequencia,
                    'conteudo': dist
                }
                rotulos = pd.concat(
                    [
                        rotulos,
                        pd.DataFrame([linha])
                    ]
                )
                sequencia += 1
        rotulos['sequencia'] = rotulos['sequencia'].astype(int)
        rede = pd.DataFrame()
        for indice in range(0, len(dimensao)-1):
            for index, row in base.iterrows():
                linha = {
                    'origem': rotulos[rotulos['conteudo'] == row[dimensao[indice]]]['sequencia'].values[0],
                    'destino': rotulos[rotulos['conteudo'] == row[dimensao[indice+1]]]['sequencia'].values[0],
                    'valor': row[medida],
                    'rotulo': row[medida]
                }
                rede = pd.concat(
                    [
                        rede,
                        pd.DataFrame([linha])
                    ]
                )
        dados = dict(
            type='sankey',
            domain=dict(x=[0, 1], y=[0, 1]),
            orientation="h",
            valueformat=".0f",
            node=dict(pad=10, thickness=30, line=dict(color="black", width=0.5), label=rotulos['conteudo'].to_list()),
            link=dict(
                source=rede['origem'].dropna(axis=0, how='any'),
                target=rede['destino'].dropna(axis=0, how='any'),
                value=rede['valor'].dropna(axis=0, how='any'),
                label=rede['rotulo'].dropna(axis=0, how='any'),
            )
        )
        layout = dict(title="Sankey Chart", height=800, width=1500, font=dict(size=10),)
        st.plotly_chart(
            go.Figure(
                dict(
                    data=[dados],
                    layout=layout
                )
            )
        )
with tabs[1]:
    with st.container(horizontal=True):
        ano = st.segmented_control(
            label='Selecione o Ano',
            options=st.session_state['dw']['ano'].sort_values(ascending=True).unique(),
            selection_mode='single'
        )
        mes = st.segmented_control(
            label='Selecione o Mês',
            options=st.session_state['dw']['mes'].sort_values(ascending=True).unique(),
            selection_mode='single'
        )
        medida = st.segmented_control(
            label='Medida',
            options=st.session_state['meds'],
            selection_mode='single'
        )
    if (ano is not None) & (mes is not None) & (medida is not None):
        base = st.session_state['dw'][
            (st.session_state['dw']['ano'] == ano) &
            (st.session_state['dw']['mes'] == mes)
        ].groupby('dia')[medida].sum().reset_index()
        medidas = ['relative'] * len(base['dia'])
        fig = go.Figure(
            go.Waterfall(
                measure=medidas,
                x=base['dia'],
                y=base[medida]
            )
        )
        fig.update_layout(title="Waterfall Chart", width=1500, height=800)
        fig.update_traces(width=0.6)
        st.plotly_chart(fig)