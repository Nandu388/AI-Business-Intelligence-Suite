import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

PASTEL = ["#B39DDB","#80CBC4","#F48FB1","#FFCC80","#A5D6A7","#90CAF9","#EF9A9A","#CE93D8"]

def style_fig(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#1A1D2E",
        font_color="#E8E8F0",
        font_family="sans-serif",
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=40, r=20, t=50, b=40),
        colorway=PASTEL,
    )
    fig.update_xaxes(gridcolor="#2A2D3E", zerolinecolor="#2A2D3E")
    fig.update_yaxes(gridcolor="#2A2D3E", zerolinecolor="#2A2D3E")
    return fig

def histogram(df, col):
    fig = px.histogram(df, x=col, nbins=40, color_discrete_sequence=[PASTEL[0]],
                       title=f"Distribution of {col}")
    return style_fig(fig)

def correlation_heatmap(df):
    corr = df.select_dtypes(include=np.number).corr()
    fig = go.Figure(go.Heatmap(z=corr.values, x=corr.columns, y=corr.columns,
                                colorscale="Purples", zmid=0,
                                text=corr.round(2).values, texttemplate="%{text}"))
    fig.update_layout(title="Correlation Matrix")
    return style_fig(fig)

def boxplot(df, col):
    fig = px.box(df, y=col, color_discrete_sequence=[PASTEL[1]], title=f"Box Plot — {col}")
    return style_fig(fig)

def scatter(df, x, y, color=None):
    fig = px.scatter(df, x=x, y=y, color=color, color_discrete_sequence=PASTEL,
                     title=f"{x} vs {y}", opacity=0.7)
    return style_fig(fig)

def bar(df, x, y, title=""):
    fig = px.bar(df, x=x, y=y, color_discrete_sequence=[PASTEL[0]], title=title)
    return style_fig(fig)

def line_forecast(actual, forecast, ci_lower=None, ci_upper=None, title="Sales Forecast"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=actual.index, y=actual.values, name="Actual",
                             line=dict(color=PASTEL[1], width=2)))
    fig.add_trace(go.Scatter(x=forecast.index, y=forecast.values, name="Forecast",
                             line=dict(color=PASTEL[0], width=2, dash="dash")))
    if ci_lower is not None and ci_upper is not None:
        fig.add_trace(go.Scatter(
            x=list(forecast.index) + list(forecast.index[::-1]),
            y=list(ci_upper) + list(ci_lower[::-1]),
            fill="toself", fillcolor="rgba(179,157,219,0.15)",
            line=dict(color="rgba(0,0,0,0)"), name="95% CI"
        ))
    fig.update_layout(title=title)
    return style_fig(fig)

def pie_chart(labels, values, title=""):
    fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.4,
                            marker_colors=PASTEL))
    fig.update_layout(title=title)
    return style_fig(fig)

def churn_gauge(churn_prob):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(churn_prob * 100, 1),
        title={"text": "Churn Probability (%)"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": PASTEL[2]},
            "steps": [
                {"range": [0, 30], "color": "#1A1D2E"},
                {"range": [30, 70], "color": "#2A2D3E"},
                {"range": [70, 100], "color": "#3A1D2E"},
            ],
        }
    ))
    return style_fig(fig)

def feature_importance_bar(features, importances, title="Feature Importance"):
    df = pd.DataFrame({"Feature": features, "Importance": importances})
    df = df.sort_values("Importance", ascending=True).tail(15)
    fig = px.bar(df, x="Importance", y="Feature", orientation="h",
                 color_discrete_sequence=[PASTEL[0]], title=title)
    return style_fig(fig)

def cluster_scatter(df, x, y, cluster_col):
    fig = px.scatter(df, x=x, y=y, color=cluster_col.astype(str),
                     color_discrete_sequence=PASTEL, title="Customer Segments",
                     opacity=0.75)
    return style_fig(fig)