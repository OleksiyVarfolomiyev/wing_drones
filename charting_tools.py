import data_aggregation_tools as da
import ETL as etl
import plotly.graph_objects as go
import data_aggregation_tools as da
import plotly.express as px
from plotly.subplots import make_subplots

def hide_axis_title(fig):
    fig.update_layout(margin=dict(l=0, r=0, b=0), yaxis_title='')
    fig.update_layout(xaxis_title='')

def fig_add_mean(fig, data, column=None, row=None, col_num=None):
    """ Add a horizontal line for the mean"""
    mean_value = data[column].mean()
    fig.add_shape(
        type='line',
        x0 = data.index[0],
        x1 = data.index[-1],
        y0=mean_value,
        y1=mean_value,
        name='mean',
        line=dict(color='blue', dash = 'dot'),
        row=row,
        col=col_num
    )
    return fig

def subplot_horizontal(fig1, fig2, rows, cols, type1, type2, title1, title2, show):
    fig = make_subplots(rows=rows, cols=cols,
                    specs=[[{'type': type1}, {'type': type2}]],
                    subplot_titles=[title1, title2])

    fig.add_trace(fig1.data[0], row=1, col=1)
    fig.add_trace(fig2.data[0], row=1, col=2)

    fig.update_layout(grid={'columns': cols, 'rows': rows, 'pattern': "independent"})
    if show:
        fig.show(renderer="notebook")
    else:
        return fig

def subplot_vertical(data1, data2, col1, col2, fig1, fig2, rows, cols, type1, type2, barmode, title1, title2, show):
    """Plot two charts vertically"""
    fig = make_subplots(rows=rows, cols=cols,
                        specs=[[{'type': type1}], [{'type': type2}]],
                        subplot_titles=[title1, title2])
    if not data1.empty:
       fig = fig_add_mean(fig, data1, col1)
    if not data2.empty:
       fig = fig_add_mean(fig, data2, col2, row=2, col_num=1)

    fig.update_layout(
        barmode = barmode,
        legend = dict(orientation='h', x=0.2, y=-0.1)
        )
    for trace in fig1.data:
        fig.add_trace(trace, row=1, col=1)

    for trace in fig2.data:
        fig.add_trace(trace, row=2, col=1)

    fig.update_layout(grid={'columns': cols, 'rows': rows, 'pattern': "independent"})
    fig.update_layout(height=700)
    fig.update_layout(coloraxis_showscale=False)

    if show:
        fig.show(renderer="notebook")
    else:
        return fig

def pie_plot(data, col, title, show):
    """Pie plot"""
    fig = px.pie(data,
             values = data[col],
             names = data.index,
             hole=0.5,
             title = title)
    if show:
        fig.show(renderer="notebook")
    else:
        return fig

def bar_plot(data, col, fig_title, show):
    """Bar plot"""
    fig = px.bar(data, x = data.index, y = col,
            color = col,
            text_auto = '.2s',
            title = fig_title,
            color_continuous_scale = 'bluyl'
            )
    fig.update_layout(coloraxis_showscale=False)

    fig = fig_add_mean(fig, data, col)
    hide_axis_title(fig)
    if show:
        fig.show(renderer="notebook")
    else:
        return fig

def bar_plot_horizontal(data, col, title):
    """Horizontal bar plot"""
    fig = px.bar(data, x = data[col], y = data.index, orientation='h',
             title = title, color=col,  text_auto='.2s')
    hide_axis_title(fig)
    fig = fig_add_mean(fig, data, col)
    fig.update_traces(marker_showscale=False)
    fig.show(renderer="notebook")

def stack_bar_plot(df, title, show):
    """Stacked bar plot"""
    df['Date'] = df['Date'].astype(str)
    mean_value = df[df.columns[1:]].sum(axis=1).mean()

    fig = go.Figure()

    for column in df.columns[df.columns != 'Date']:
        fig.add_trace(
        go.Bar(name=column, x = df['Date'], y = df[column],
               text = df[column].apply(etl.format_money)
        ))

    fig.update_layout(
    barmode='stack',
    title = title,
    legend=dict(orientation='h', x=0.2, y=-0.1),
    # Add a horizontal line at the mean value
        shapes=[
            dict(
                type='line',
                x0=df['Date'].iloc[0],
                x1=df['Date'].iloc[-1],
                y0=mean_value,
                y1=mean_value,
                line=dict(color='blue', dash='dot')
            )
        ]
    )

    if show:
        fig.show(renderer="notebook")
    else:
        return fig

def line_plot(data, col, title, show):
    """Line plot"""
    fig = px.line(data, x = data.index, y = data[col], title = title)
    fig.update_traces(line=dict(color='green'))

    # Add the moving average
    window = 14
    moving_avg = data[col].rolling(window=window).mean()

    fig.add_trace(go.Scatter(x = data.index, y = moving_avg,
                             mode='lines', name=f'{window}-Day Moving Average',
                             showlegend = False,
                             line=dict(color='orange', dash = 'dot') ))
    hide_axis_title(fig)
    fig = fig_add_mean(fig, data, col)

    if show:
        fig.show(renderer="notebook")
    else:
        return fig

def bar_plot_with_line(df, col, fig_title, show):
    """Bar plot with a line plot"""
    fig = go.Figure()

# Create a color scale
    scale = px.colors.sequential.Viridis
# Map y-values to colors
    df['color'] = df[col].apply(lambda y: scale[int(y * (len(scale) - 1) / max(df[col]))])

# Add a Bar trace for the bar plot
    fig.add_trace(
    go.Bar(x = df.index,
            y = df[col],
            marker_color = df['color'],
            #text = [f'{round(val/1e6, 2)}M' for val in df[col]],
            text = df[col],
            textposition='auto'
        )
    )

# Add a Scatter trace for the line plot
    fig.add_trace(
    go.Scatter(x = df.index, y = df[col],
            mode='lines+markers', line_shape='linear',
            line=dict(color='green'))
    )

    fig.update_layout(
    title=fig_title,
    xaxis_title='',
    yaxis_title='',
    template='plotly_white',
    showlegend = False
    )
    fig = fig_add_mean(fig, df, col)
    if show:
        fig.show(renderer="notebook")
    else:
        return fig

def bar_plot_grouped(data, col1, col2, fig_title, show):
    """Grouped bar plot"""
    trace1 = go.Bar(x=data.index, y=data[col1], name=col1, text=data[col1].apply(etl.format_money), marker_color = 'blue', showlegend=False)
    trace2 = go.Bar(x=data.index, y=data[col2], name=col2, text=data[col2].apply(etl.format_money), marker_color = 'yellow', showlegend=False)

    layout = go.Layout(
        barmode='group',
        title=fig_title,
        xaxis=dict(title='', tickangle=-45),
        yaxis=dict(title='')
    )
    fig = go.Figure(data=[trace1, trace2], layout=layout)
    fig = fig_add_mean(fig, data, col1)
    fig.update_layout(xaxis=dict(tickformat='%b'))
    fig.update_layout(showlegend=False)

    hide_axis_title(fig)

    if show:
        fig.show(renderer="notebook")
    else:
        return fig


def chart_by_period(data, categories, period, title1, title2):
    """bar plot by period on top and stacked bar plot by period on the bottom"""
    data_sum_by_period = da.sum_by_period(data, period)
    data_sum_by_period.index = data_sum_by_period.index.start_time
    fig1 = bar_plot(data_sum_by_period, 'UAH', title1, False)

    data_sum_by_period_by_category = da.sum_by_period_by_category(categories, period, data, 'Category').fillna(0)
    if period == 'w':
        data_sum_by_period_by_category['Date'] = data_sum_by_period_by_category['Date'].astype(str).str.split('/').str[0]
    fig2 = stack_bar_plot(data_sum_by_period_by_category, title2, False)

    subplot_vertical(data_sum_by_period, data_sum_by_period, 'UAH', 'UAH', fig1, fig2, 2, 1, 'xy', 'xy', 'stack', title1, title2, True)
