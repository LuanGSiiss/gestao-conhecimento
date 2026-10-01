import pandas as pd
import numpy as np
import streamlit as st
from sqlalchemy import create_engine


@st.cache_data
def load_base():
    conexao = create_engine(st.secrets['url'])
    with conexao.connect() as cnx:
        df = pd.read_sql(
            sql="select * from dw_europa",
            con=cnx
        )
    dims = [c for c in df.columns if df[c].dtypes in ['object'] or c in ['data', 'ano', 'mes', 'dia']]
    meds = [c for c in df.columns if df[c].dtypes not in ['object'] and c not in ['data', 'ano', 'mes', 'dia']]
    meds = [c for c in meds if c not in ['latitude', 'longitude']]
    return df, dims, meds

def analise_variancia(df, var, grp):
    tukey = pairwise_tukeyhsd(
        endog=df[var], groups=df[grp], alpha=0.05
    )
    tuk = []
    combinacao = combinations(tukey.groupsunique,2)
    for grupo in list(combinacao):
        tuk.insert(len(tuk), [grupo[0],grupo[1]])
    tuk = pd.DataFrame(tuk, columns=['grupo1', 'grupo2'])
    tuk['diferente'] = tukey.reject
    tuk['valor'] = tukey.meandiffs
    tuk['grupo'] = tuk.apply(lambda x : f"{x['grupo1']} - {x['grupo2']}", axis=1)
    return tuk


def classes(base, variavel):
    iqr = base[variavel].quantile(0.75) - base[variavel].quantile(0.25)
    out_min = base[variavel].quantile(0.25) - (1.5 * iqr)
    out_max = base[variavel].quantile(0.75) + (1.5 * iqr)
    limite_inferior = base[variavel].mean() - (1.96 * base[variavel].std() / np.sqrt(len(base)))
    limite_superior = base[variavel].mean() + (1.96 * base[variavel].std() / np.sqrt(len(base)))
    base['outlier_minimo'] = base[variavel].apply(lambda x : True if x < out_min else False)
    base['outlier_maximo'] = base[variavel].apply(lambda x : True if x > out_max else False)
    base['posicao'] = base[variavel].apply(
        lambda x : 'abaixo'
        if x < limite_inferior
        else (
            'acima'
            if x > limite_superior
            else 'media'
        )
    )
    media = base[variavel].mean()
    desvio = base[variavel].std()
    base['estrelas'] = base[variavel].apply(lambda x : round((x - media) / desvio,0) + 3)
    base['posicao_final'] = base.apply(
        lambda x : 'outlier maximo' if x['outlier_maximo'] else (
            'acima da media' if x['posicao'] == 'acima' else (
                'na media' if x['posicao'] == 'media' else (
                    'outlier minimo' if x['outlier_minimo'] else 'abaixo da media'
                )
            )
        ),
        axis = 1
    )
    base['relacao_media'] = base[variavel] - media
    base['positivo'] = base['relacao_media'].apply(lambda x : True if x >= 0 else False)
    return base, limite_inferior, limite_superior, out_min, out_max


def cor_classe(s):
    if s.outlier_maximo == True:
        return ['background-color: #686de0']*len(s)
    elif s.posicao == 'acima':
        return ['background-color: #badc58']*len(s)
    elif s.posicao == 'media':
        return ['background-color: #f6e58d']*len(s)
    elif s.outlier_minimo == True:
        return ['background-color: #ff7979'] * len(s)
    else:
        return ['background-color: #ffbe76']*len(s)

cores_abc = {
    "A": "#badc58",
    "B": "#f6e58d",
    "C": "#ffbe76"
}


def curvaabc(abc, medida, dimensao):
    abc['percentual'] = abc[medida] / abc[medida].sum()
    abc_sort = abc.sort_values(by=medida, ascending=False).copy()
    abc_sort['percentual_acumulado'] = abc_sort['percentual'].cumsum()
    abc_sort['acumulado'] = abc_sort[medida].cumsum()
    abc_sort['posicao'] = abc_sort['percentual_acumulado'].apply(
        lambda x : 'A' if x <= 0.65 else (
            'B' if x <= 0.90 else 'C'
        )
    )
    abc_sort['posicao_final'] = abc_sort.apply(lambda x : x[dimensao] if x['posicao'] != 'A' else 'Outros', axis=1)
    return abc_sort


def cor_abc(s):
    if s.posicao == 'A':
        return ['background-color: #badc58']*len(s)
    elif s.posicao == 'B':
        return ['background-color: #f6e58d']*len(s)
    else:
        return ['background-color: #ffbe76']*len(s)


cores_posicao_final = {
    "outlier maximo": "#686de0",
    "acima da media": "#badc58",
    "na media": "#f6e58d",
    "abaixo da media": "#ffbe76",
    "outlier minimo": "#ff7979"
}
