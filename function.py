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


