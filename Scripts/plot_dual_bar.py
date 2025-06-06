# Importação dos pacotes necessários
import pandas as pd
import numpy as np
from plotnine import (
    ggplot, aes, geom_col, geom_hline, geom_label, coord_flip,
    scale_color_manual, scale_fill_manual, scale_y_continuous,
    coord_cartesian, theme_minimal, labs, guides, theme, element_blank
)

def plot_dual_bar(data: pd.DataFrame, group_var: str):
    """
    Gráfico de barras horizontais com scores positivos e negativos.
    
    Parâmetros:
    - data: DataFrame.
    - group_var: nome da variável de agrupamento.
    
    Retorna:
    - plotnine.ggplot.
    """
    
    # 1. Ajuste de sinal
    data = data.copy()
    data['answer_score_adj'] = np.where(data['answer_negative'], 
                                        data['answer_score'] * -1, 
                                        data['answer_score'])
    
    # 2. Agregação
    agg = (
        data.groupby([group_var, 'answer_negative'])
        .agg(mean_score=('answer_score_adj', 'mean'),
             sd_score=('answer_score_adj', 'std'))
        .reset_index()
    )
    
    # 3. Label para score e posição do label
    agg['label_score'] = agg['mean_score'].abs().round().astype(int).astype(str) + '%'
    agg['label_x'] = np.where(agg['mean_score'] < 0, agg['mean_score'] + 5, agg['mean_score'] - 5)
    
    # 4. Médias negativas/positivas
    agg['negative'] = agg['mean_score'] < 0
    media_neg_pos = (
        agg.groupby('negative')
        .agg(mean=('mean_score', 'mean'))
        .reset_index()
    )
    
    # 5. Criar labels manuais
    media_labels = {}
    for _, row in media_neg_pos.iterrows():
        key = row['negative']
        val = f"Média {'negativa' if key else 'positiva'}: {abs(round(row['mean'], 1))}%"
        media_labels[key] = val
    
    # 6. Cores
    color_values = {True: 'red', False: 'blue'}
    
    # 7. Plot
    p = (
        ggplot(agg, aes(
            x=group_var,
            y='mean_score',
            fill='answer_negative'
        )) +
        geom_col(position='identity', color='#666666') +
        geom_hline(
            data=media_neg_pos,
            mapping=aes(yintercept='mean', color='negative'),
            linetype='dashed',
            size=1
        ) +
        scale_color_manual(
            name='Média',
            values=color_values,
            labels=[media_labels[False], media_labels[True]]
        ) +
        geom_label(
            aes(
                x=group_var,
                y='label_x',
                label='label_score'
            ),
            fill='white',
            size=8,  # Ajuste conforme preferência
            fontweight='bold',
            color='black'
        ) +
        scale_fill_manual(
            values={False: "#5798ff", True: "#ff5454"}
        ) +
        scale_y_continuous(
            limits=[-100, 100],
            breaks=list(range(-100, 125, 25)),
            labels=[f"{abs(x)}%" for x in range(-100, 125, 25)]
        ) +
        coord_cartesian(expand=False) +
        theme_minimal(base_size=12) +
        labs(
            x="Média Score (%)",
            y="Média Score (%)",
            fill=None
        ) +
        guides(fill=False) +
        theme(
            axis_title_y = element_blank(),
            panel_grid_major_y=element_blank(),
            panel_grid_minor=element_blank(),
            legend_position='bottom'
        ) +
        coord_flip() 
    )
    
    return p