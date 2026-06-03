from plotly.subplots import make_subplots
import plotly.graph_objects as go

def create_rich_chart(df, ticker): # 2段構成（上：株価、下：出来高）
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
    
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name=ticker), row=1, col=1) # ローソク足またはライン

    ma200 = df['Close'].rolling(window=200).mean() # 移動平均線（オプションで追加）
    fig.add_trace(go.Scatter(x=df.index, y=ma200, name="MA200", line=dict(dash='dot')), row=1, col=1)

    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Volume"), row=2, col=1) # 出来高

    fig.update_layout(height=600, template="plotly_dark", showlegend=True)
    return fig