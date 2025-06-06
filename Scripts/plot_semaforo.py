import pandas as pd
import numpy as np
from plotnine import (
    ggplot, aes, geom_col,
    scale_y_continuous, scale_fill_manual,
    coord_cartesian, theme_minimal, scale_x_discrete,
    labs, theme, element_blank, coord_flip, element_text
)
from plotnine import scales


def plot_semaforo(data: pd.DataFrame, group_var: str) -> ggplot:
    """
    Gera um gráfico “semáforo” (100% empilhado) para a variável de agrupamento especificada.
    
    Parâmetros:
    - data: DataFrame que contém pelo menos as colunas:
        * 'employee_registration'      (identificador único do funcionário)
        * group_var (por exemplo, 'question_dimension')
        * 'answer_score_signed'        (score já com sinal: negativo → escala ruim, positivo → escala boa)
    - group_var: string com o nome da coluna de agrupamento (ex: 'question_dimension').
    
    Retorna:
    - Um objeto ggplot (plotnine) pronto para exibir ou salvar.
    """
    
    # 1) Calcular a média de cada funcionário em cada grupo/dimensão
    df_medias = (
        data
        .groupby(['employee_registration', group_var], as_index=False)
        .agg(mean_dim=('answer_score_signed', 'mean'))
    )
    
    # 2) Transformar em valor absoluto para classificar nas faixas
    df_medias['mean_abs'] = df_medias['mean_dim'].abs()
    
    # 3) Criar a coluna 'faixa' de acordo com o valor absoluto
    #    Faixas: 0–33: "Péssimo", 34–66: "Intermediário", 67–100: "Ótimo"
    def atribuir_faixa(x):
        if x <= 33:
            return "Péssimo"
        elif x <= 66:
            return "Intermediário"
        else:
            return "Ótimo"
    
    df_medias['faixa'] = df_medias['mean_abs'].apply(atribuir_faixa)
    
    # 4) Para garantir a ordem de empilhamento (Ótimo → Intermediário → Péssimo)
    df_medias['faixa'] = pd.Categorical(
        df_medias['faixa'],
        categories=["Ótimo", "Intermediário", "Péssimo"],
        ordered=True
    )
    
    # 5) Contar quantos funcionários em cada (group_var,faixa) e calcular proporção
    df_contagem = (
        df_medias
        .groupby([group_var, 'faixa'], as_index=False)
        .agg(n=('employee_registration', 'nunique'))
    )
    df_totais = (
        df_contagem
        .groupby(group_var, as_index=False)
        .agg(n_total=('n', 'sum'))
    )
    df_prop = pd.merge(df_contagem, df_totais, on=group_var, how='left')
    df_prop['prop'] = df_prop['n'] / df_prop['n_total']
    
    # 6) Construir o gráfico plotnine
    p = (
        ggplot(df_prop, aes(
            x=group_var,
            y='prop',
            fill='faixa'
        )) +
        geom_col(
            position='fill',
            color='#666666'  # contorno cinza equivalente a "gray40"
        ) +
        scale_y_continuous(
            breaks=np.linspace(0, 1, 5),
            labels=[f"{int(tick * 100)}%" for tick in np.linspace(0, 1, 5)],
            expand=(0, 0)
        ) +
        # scale_x_discrete(
        #     expand=(0.02, 0)   # ↑ aqui, 0.02 “empurra” a primeira/última categoria 2% da largura total
        # ) +
        scale_fill_manual(
            values={
                "Péssimo": "#EF4444",       # vermelho
                "Intermediário": "#FACC15", # amarelo
                "Ótimo": "#10B981"          # verde
            }
        ) +
        coord_cartesian(expand=False) +
        theme_minimal(base_size=12) +
        labs(
            x="Proporção de funcionários",
            y="Média Score (%)",
            fill="Percepção"
        ) +
        theme(
            # axis_title_x = element_blank(),
            # legend_title=element_blank(),
            panel_grid_major_y=element_blank(),
            panel_grid_minor=element_blank(),
            # axis_text_x = element_text(margin={'t': 200}),
            # plot_margin = {'l': 20, 'r': 10, 't': 10, 'b': 10}
        ) +
        coord_flip()
    )
    
    return p