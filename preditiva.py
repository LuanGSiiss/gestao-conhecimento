import streamlit as st
import plotly.express as px
import pandas as pd

from function import load_base
from function import serietemporal, rfm, classificacao, regressao

import logging
logging.getLogger("prophet").setLevel(logging.WARNING)
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)

st.session_state['dw'], st.session_state['dims'], st.session_state['meds'] = load_base()
with st.container(horizontal=True):
    st.badge(
        label="Data Analysis",
        color="orange",
        icon=":material/monitoring:"
    )
    st.badge(
        label="Preditive Analysis",
        color="green",
        icon=":material/monitoring:"
    )
dimensao = st.segmented_control(
    label='Dimensão',
    options=st.session_state['dims'],
    selection_mode='single'
)
medida = st.segmented_control(
    label='Medida',
    options=st.session_state['meds'],
    selection_mode='single'
)
st.divider()
if (dimensao is not None) & (medida is not None):
    base = st.session_state['dw'].groupby(dimensao)[medida].sum().reset_index()
    if len(base[dimensao]) < 10:
        st.badge(
            label="Série Temporal",
            icon=":material/monitoring:",
            color="primary"
        )
        ts = serietemporal(
            dataframe=st.session_state['dw'],
            dimensao=dimensao,
            medida=medida,
            periodos=12
        )
        dim = st.segmented_control(
            label=dimensao,
            options=list(ts[dimensao].unique()),
            selection_mode='single',
            default=list(ts[dimensao].unique())[0]
        )
        if dim is not None:
            previsao = ts[ts[dimensao] == dim][['data', 'limite_baixo', 'previsto', 'limite_alto', 'historico']]
            previsao = previsao.melt(
                id_vars=['data'],
                var_name='medida',
                value_name='valor'
            )
            st.plotly_chart(
                px.line(
                    data_frame=previsao,
                    y="valor",
                    x="data",
                    color="medida",
                    height=600,
                    color_discrete_sequence=["lightgray", "blue", "lightgray", "green"],
                )
            )
    elif len(base[dimensao]) < 100:
        st.badge(
            label="Classificacao",
            icon=":material/monitoring:",
            color="primary"
        )
        st.dataframe(
            classificacao(
                rfm(st.session_state['dw'], dimensao),
                medida
            ),
            column_config={
                "prob_abaixo_media": st.column_config.ProgressColumn(
                    label="prob_abaixo_media",
                    format="%.2f",
                    min_value=0,
                    max_value=100
                ),
                "prob_acima_media": st.column_config.ProgressColumn(
                    label="prob_acima_media",
                    format="%.2f",
                    min_value=0,
                    max_value=100
                ),
            },
            hide_index=True
        )
    else:
        st.badge(
            label="Regressão",
            icon=":material/monitoring:",
            color="primary"
        )
        base = st.session_state['dw'].groupby(dimensao)[medida].mean().reset_index()
        base = base.rename(columns={medida: 'media'})
        base = pd.merge(
            rfm(st.session_state['dw'], dimensao),
            base,
            on=dimensao
        )
        st.dataframe(
            regressao(base, medida),
            hide_index=True
        )