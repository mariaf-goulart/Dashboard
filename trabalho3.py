import os
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
caminho_excel = os.path.join(BASE_DIR, '1 - Base de Dados.xlsx')
df = pd.read_excel(caminho_excel)
df = df.drop("Unnamed: 0", axis=1, errors="ignore")

# Meses em ordem cronológica
df = df.sort_values('Data_Pedido', kind='stable')
df['Data_Pedido'] = df['Data_Pedido'].dt.strftime('%B %Y')

# Meses em português
meses = {'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março', 'April': 'Abril',
         'May': 'Maio', 'June': 'Junho', 'July': 'Julho', 'August': 'Agosto',
         'September': 'Setembro', 'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'}
df['Data_Pedido'] = df['Data_Pedido'].replace(meses, regex=True)

# Nomes sem "_" e sem espaço duplicado
for col in ['Nome_Representante', 'Nome_Produto', 'Nome_Cliente', 'Regional', 'Estado_Cliente', 'Cidade_Cliente']:
    df[col] = df[col].astype(str).str.replace('_', ' ').str.split().str.join(' ')

# Listas em ordem alfabética
ordem_estados = sorted(df['Estado_Cliente'].unique())
ordem_representantes = sorted(df['Nome_Representante'].unique())
ordem_cidades = sorted(df['Cidade_Cliente'].unique())


app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True)

server = app.server  # necessário para o PythonAnywhere

app.layout = html.Div(style={'backgroundColor': 'black', 'color': 'white', 'padding': '20px',
                             'maxWidth': '1200px', 'margin': 'auto'}, children=[

    # Layout do dashboard
    html.H1("Relatório de Vendas - 2020", className='display-4 mb-4'),

    # Total de vendas por Mês
    dcc.Graph(
        id='graph1',
        style={'marginBottom': '15px', 'borderRadius': '6px', 'overflow': 'hidden', 'backgroundColor': 'white'},
        figure=px.histogram(df, x='Data_Pedido', y='Valor_Total_Venda', title='Total de Vendas por Mês',
                            color='Data_Pedido', labels={'Data_Pedido': 'Meses', 'Valor_Total_Venda': 'Total de Vendas'})),

    # Total de vendas por Representante
    dcc.Graph(
        id='graph2',
        style={'marginBottom': '15px', 'borderRadius': '6px', 'overflow': 'hidden', 'backgroundColor': 'white'},
        figure=px.histogram(df, x='Nome_Representante', y='Valor_Total_Venda',
                            title='Total de Vendas por Representante', color='Nome_Representante',
                            labels={'Nome_Representante': 'Representantes', 'Valor_Total_Venda': 'Total de Vendas'},
                            category_orders={'Nome_Representante': ordem_representantes})),

    # Tabela à esquerda e Região e Estado à direita
    html.Div(style={'display': 'grid', 'gridTemplateColumns': 'minmax(0, 4fr) minmax(0, 5fr)',
                    'gap': '15px', 'height': '695px', 'marginBottom': '15px'}, children=[

        # Cartão da esquerda
        html.Div(style={'backgroundColor': 'white', 'borderRadius': '6px',
                        'padding': '10px', 'boxSizing': 'border-box', 'overflow': 'hidden'}, children=[
            html.H3("Total de Vendas por Produto",
                    style={'fontSize': '18px', 'height': '40px', 'margin': '0', 'color': '#2a3f5f'}),
            dash_table.DataTable(
                id='table',
                columns=[
                    {'name': 'Produto', 'id': 'produto'},
                    {'name': 'Qtd. Vendida', 'id': 'quantidade', 'type': 'numeric',
                     'format': {'locale': {'group': '.'}, 'specifier': ',.0f'}},
                    {'name': 'Total de Vendas', 'id': 'total', 'type': 'numeric',
                     'format': {'locale': {'symbol': ['R$ ', ''], 'group': '.', 'decimal': ','}, 'specifier': '$,.2f'}},
                ],
                data=df.groupby('Nome_Produto', as_index=False).agg(
                    quantidade=('Quantidade_Vendida', 'sum'), total=('Valor_Total_Venda', 'sum')
                ).sort_values('total', ascending=False).rename(columns={'Nome_Produto': 'produto'}).to_dict('records'),
                sort_action='native',
                style_table={'maxHeight': '620px', 'overflowY': 'auto'},
                style_cell={'textAlign': 'center', 'padding': '4px', 'fontSize': '12px'},
                style_header={'backgroundColor': '#636EFA', 'color': 'white', 'fontWeight': 'bold',
                              'whiteSpace': 'normal'},
                style_data={'color': 'black', 'backgroundColor': 'white'},
                style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#E5ECF6'}],
            ),
        ]),

        # Coluna da direita
        html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '15px'}, children=[

            # Total de vendas por Região
            dcc.Graph(
                id='graph4',
                style={'height': '340px', 'borderRadius': '6px', 'overflow': 'hidden', 'backgroundColor': 'white'},
                figure=px.sunburst(df, path=['Regional', 'Estado_Cliente'], values='Valor_Total_Venda',
                                   title='Total de Vendas por Região', color='Estado_Cliente',
                                   labels={'Regional': 'Região', 'Estado_Cliente': 'Estado', 'Valor_Total_Venda': 'Total de Vendas'}
                                   ).update_layout(margin=dict(t=50, l=10, r=10, b=10))),

            # Total de vendas por Estado
            dcc.Graph(
                id='graph5',
                style={'height': '340px', 'borderRadius': '6px', 'overflow': 'hidden', 'backgroundColor': 'white'},
                figure=px.histogram(df, x='Estado_Cliente', y='Valor_Total_Venda', title='Total de Vendas por Estado',
                                    color='Cidade_Cliente',
                                    labels={'Cidade_Cliente': 'Cidade', 'Estado_Cliente': 'Estado', 'Valor_Total_Venda': 'Total de Vendas'},
                                    category_orders={'Estado_Cliente': ordem_estados, 'Cidade_Cliente': ordem_cidades}
                                    ).update_yaxes(range=[0, 50000000]
                                    ).update_layout(legend=dict(font=dict(size=10), tracegroupgap=0),
                                                    margin=dict(t=50, l=10, r=10, b=40))),
        ]),
    ]),

    # Filtros
    html.Div(style={'display': 'grid', 'gridTemplateColumns': 'minmax(0, 4fr) minmax(0, 5fr)', 'gap': '15px'}, children=[

        # Coluna 1: Estado, Cidade, Produto
        html.Div(children=[

            # Filtro por Estados
            html.Label('Selecione para filtrar Estados selecionados:', style={'color': 'gray', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='estado-dropdown', style={'marginBottom': '12px'},
                options=[{'label': estado, 'value': estado} for estado in df['Estado_Cliente'].unique()],
                value=list(df['Estado_Cliente'].unique()),
                multi=True),

            # Filtro por Cidades, de acordo com o Estado selecionado anteriormente
            html.Label('Selecione para filtrar Cidades selecionadas:', style={'color': 'gray', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='cidade-dropdown', style={'marginBottom': '12px'},
                options=[{'label': cidade, 'value': cidade} for cidade in ordem_cidades],
                multi=True),

            # Filtro 1: Produto
            html.Label('Selecione para filtrar Produtos:', style={'color': 'gray', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='produto-dropdown', style={'marginBottom': '12px'},
                options=[{'label': p, 'value': p} for p in df['Nome_Produto'].unique()],
                multi=True),
        ]),

        # Coluna 2: Cliente, Representante
        html.Div(children=[

            # Filtro 2: Cliente
            html.Label('Selecione para filtrar Clientes:', style={'color': 'gray', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='cliente-dropdown', style={'marginBottom': '12px'},
                options=[{'label': c, 'value': c} for c in df['Nome_Cliente'].unique()],
                multi=True),

            # Filtro 3: Representante
            html.Label('Selecione para filtrar Representantes:', style={'color': 'gray', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='representante-dropdown', style={'marginBottom': '12px'},
                options=[{'label': r, 'value': r} for r in df['Nome_Representante'].unique()],
                multi=True),
        ]),
    ]),
])

# Opções de cidades de acordo com o(s) estado(s) selecionado(s)
@app.callback(
    Output('cidade-dropdown', 'options'),
    Output('cidade-dropdown', 'value'),
    Input('estado-dropdown', 'value'),
    State('cidade-dropdown', 'value'))
def update_cidades_options(selected_estados, selected_cidades):
    if selected_estados:
        cidades = sorted(df[df['Estado_Cliente'].isin(selected_estados)]['Cidade_Cliente'].unique())
    else:
        cidades = ordem_cidades

    options = [{'label': cidade, 'value': cidade} for cidade in cidades]
    # mantém só as cidades já escolhidas que ainda pertencem aos estados selecionados
    value = [c for c in (selected_cidades or []) if c in cidades]
    return options, value

# Atualiza gráficos e tabela com TODOS os filtros
@app.callback(
    Output('graph1', 'figure'),
    Output('graph2', 'figure'),
    Output('table', 'data'),
    Output('graph4', 'figure'),
    Output('graph5', 'figure'),
    Input('estado-dropdown', 'value'),
    Input('cidade-dropdown', 'value'),
    Input('produto-dropdown', 'value'),
    Input('cliente-dropdown', 'value'),
    Input('representante-dropdown', 'value'))
def update_graphs(selected_estados, selected_cidades, selected_produtos, selected_clientes, selected_representantes):

    filtered_df = df

    # Mostra todos os dados quando estiver sem o filtro
    if selected_estados:
        filtered_df = filtered_df[filtered_df['Estado_Cliente'].isin(selected_estados)]
    if selected_cidades:
        filtered_df = filtered_df[filtered_df['Cidade_Cliente'].isin(selected_cidades)]
    if selected_produtos:
        filtered_df = filtered_df[filtered_df['Nome_Produto'].isin(selected_produtos)]
    if selected_clientes:
        filtered_df = filtered_df[filtered_df['Nome_Cliente'].isin(selected_clientes)]
    if selected_representantes:
        filtered_df = filtered_df[filtered_df['Nome_Representante'].isin(selected_representantes)]

    # Combinação de filtros sem nenhuma venda
    if filtered_df.empty:
        return {}, {}, [], {}, {}

    fig1 = px.histogram(filtered_df, x='Data_Pedido', y='Valor_Total_Venda', title='Total de Vendas por Mês',
                        color='Data_Pedido', labels={'Data_Pedido': 'Meses', 'Valor_Total_Venda': 'Total de Vendas'})

    fig2 = px.histogram(filtered_df, x='Nome_Representante', y='Valor_Total_Venda', title='Total de Vendas por Representante',
                        color='Nome_Representante',
                        labels={'Nome_Representante': 'Representantes', 'Valor_Total_Venda': 'Total de Vendas'},
                        category_orders={'Nome_Representante': ordem_representantes})

    tabela = filtered_df.groupby('Nome_Produto', as_index=False).agg(
        quantidade=('Quantidade_Vendida', 'sum'), total=('Valor_Total_Venda', 'sum')
    ).sort_values('total', ascending=False)
    tabela = tabela.rename(columns={'Nome_Produto': 'produto'})

    fig4 = px.sunburst(filtered_df, path=['Regional', 'Estado_Cliente'], values='Valor_Total_Venda',
                       title='Total de Vendas por Região', color='Estado_Cliente',
                       labels={'Regional': 'Região', 'Estado_Cliente': 'Estado', 'Valor_Total_Venda': 'Total de Vendas'}
                       ).update_layout(margin=dict(t=50, l=10, r=10, b=10))

    fig5 = px.histogram(filtered_df, x='Estado_Cliente', y='Valor_Total_Venda', title='Total de Vendas por Estado',
                        color='Cidade_Cliente',
                        labels={'Cidade_Cliente': 'Cidade', 'Estado_Cliente': 'Estado', 'Valor_Total_Venda': 'Total de Vendas'},
                        category_orders={'Estado_Cliente': ordem_estados, 'Cidade_Cliente': ordem_cidades}
                        ).update_yaxes(range=[0, 50000000]
                        ).update_layout(legend=dict(font=dict(size=10), tracegroupgap=0),
                                        margin=dict(t=50, l=10, r=10, b=40))

    return fig1, fig2, tabela.to_dict('records'), fig4, fig5


if __name__ == '__main__':
    app.run(debug=True)