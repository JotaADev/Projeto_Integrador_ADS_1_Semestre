import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# Lê o arquivo XLSX que contém os símbolos das ações internacionais
xlsx_symbols = pd.read_excel('NASDAQ.xlsx')

# Extrai os símbolos da coluna "Symbol" para um array
partial_symbols = xlsx_symbols['Symbol'].values

# Define o array que receberá o retorno da API
data_symbols = []

# Percorre o arquivo com os símbolos da NASDAQ
for symbol in partial_symbols:
    stock = yf.Ticker(symbol)
    data = stock.history(period="5y")
    if 'Dividends' in data.columns:  # Verifica se há dados de dividendos
        total_dividends = data['Dividends'].sum()
        data_symbols.append({'Ticker': symbol, 'TotalDividends': total_dividends})

# Cria um DataFrame com os dados de dividendos
df_dividends = pd.DataFrame(data_symbols)

# Seleciona os top 10 tickers com base nos dividendos pagos nos últimos 5 anos
top_10_tickers = df_dividends.nlargest(10, 'TotalDividends')['Ticker'].values

# Define o array que receberá o retorno da API para os top 10 tickers
data_top_symbols = []

# Percorre os top 10 tickers
for symbol in top_10_tickers:
    stock = yf.Ticker(symbol)
    data = stock.history(period="2y")
    data_top_symbols.append(data)

# Cria o DataFrame final
df_top_10 = pd.concat(data_top_symbols, keys=top_10_tickers, names=['Ticker', 'Date'])
df_top_10 = df_top_10.reset_index()
df_top_10['Date'] = df_top_10['Date'].dt.tz_localize(None)

# Adiciona a média dos preços de "Close" por mês
df_top_10['Month'] = df_top_10['Date'].dt.to_period('M')
df_top_10_avg = df_top_10.groupby(['Ticker', 'Month'])['Close'].mean().reset_index()

# Adiciona a soma dos dividendos por mês
df_top_10_sum = df_top_10.groupby(['Ticker', 'Month'])['Dividends'].sum().reset_index()

# Merge dos DataFrames para ter todas as informações em um só lugar
df_combined = pd.merge(df_top_10_avg, df_top_10_sum, on=['Ticker', 'Month'])

# Calcula a porcentagem de dividendos em relação ao fechamento
df_combined['Dividend_Percentage'] = (df_combined['Dividends'] / df_combined['Close']) * 100

# Convertendo o período para representação no formato "MM/AAAA"
df_combined['Month'] = df_combined['Month'].dt.to_timestamp().dt.strftime('%m/%Y')

# Criação do Gráfico de Média de Fechamento e Soma de Dividendos
plt.figure(figsize=(12, 8))
for ticker in top_10_tickers:
    data_ticker = df_combined[df_combined['Ticker'] == ticker]
    plt.plot(data_ticker['Month'], data_ticker['Close'], label=f'{ticker} - Close Avg')
    plt.bar(data_ticker['Month'], data_ticker['Dividends'], label=f'{ticker} - Dividends Sum', alpha=0.5)

plt.title('Média de Fechamento e Soma de Dividendos por Mês - Top 10 Tickers')
plt.xlabel('Mês/Ano')
plt.ylabel('Valor')
plt.xticks(rotation=45, ha='right')
plt.legend()
plt.tight_layout()
plt.show()

# Criação do gráfico da porcentagem de dividendos em relação ao fechamento por mês
plt.figure(figsize=(12, 8))
for ticker in top_10_tickers:
    data_ticker = df_combined[df_combined['Ticker'] == ticker]
    plt.plot(data_ticker['Month'], data_ticker['Dividend_Percentage'], label=f'{ticker} - Dividend Percentage')

plt.title('Porcentagem de Dividendos em Relação ao Fechamento por Mês - Top 10 Tickers')
plt.xlabel('Mês/Ano')
plt.ylabel('Porcentagem')
plt.xticks(rotation=45, ha='right')  # Rotaciona os rótulos do eixo x para melhor legibilidade
plt.legend()
plt.tight_layout()  # Ajusta o layout para evitar cortes nos rótulos
plt.show()

# Código para Gráfico de Fechamento com Médias Móveis
plt.figure(figsize=(12, 8))
for ticker in top_10_tickers:
    data_ticker = df_top_10_avg[df_top_10_avg['Ticker'] == ticker]
    data_ticker['Month'] = data_ticker['Month'].dt.to_timestamp().dt.strftime('%m/%Y')
    data_ticker['MA10'] = data_ticker['Close'].rolling(window=10).mean()
    data_ticker['MA20'] = data_ticker['Close'].rolling(window=20).mean()

    plt.plot(data_ticker['Month'], data_ticker['MA10'], label=f'{ticker} - MA10')

plt.title('Fechamento por Mês com Médias Móveis de 10 - Top 10 Tickers')
plt.xlabel('Mês/Ano')
plt.ylabel('Valor')
plt.xticks(rotation=45, ha='right')
plt.legend()
plt.tight_layout()
plt.show()
