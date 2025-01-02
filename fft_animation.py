import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import numpy as np
from scipy.fft import fft, fftfreq

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Label("Signal Length (sec.):", style = {"padding-left": "20px", "margin-bottom": "30px"}),
            dcc.Slider(id='time-range'
                        , min=0, max=10, step=1, value=10
                        , marks = {0: {'label': '0'}, 10: {'label': '10'}}
                        , tooltip = {"placement": "bottom", "always_visible": True}
                        , updatemode="drag"
                        )
            ]
            , style = {'width': '15%', 'display': 'inline-block', 'padding': '0 10px'}
            ),
        
        html.Div([
            html.Label("Sampling Points:", style = {"padding-left": "20px"}),
            dcc.Slider(id='sampling-points'
                        , min=256, max=4096, step=64, value=2048
                        , marks = {256: {'label': '256'}, 4096: {'label': '4096'}}
                        , tooltip = {"placement": "bottom", "always_visible": True}
                        , updatemode="drag"
                        )
            ]
            , style = {'width': '10%', 'display': 'inline-block', 'padding': '0 10px'}
            ),

        html.Div([
            html.Label("Winding Frequency:", style = {"padding-left": "20px"}),
            dcc.Slider(id='winding-frequency'
                       , min = 0.01, max = 10, step = 0.01, value = 0.5
                       , marks = {0.01: {'label': '0'}, 10: {'label': '10'}}
                        , tooltip = {"placement": "bottom", "always_visible": True}
                       , updatemode="drag"
                       )
            ], style={'width': '15%', 'display': 'inline-block', 'padding': '0 10px'}
            ),
            
        html.Div([
            html.Label("Time Slider:", style = {"padding-left": "20px"}),
            dcc.Slider(id='time-pointer'
                       , step = 0.01, min = 0, max = 10, value = 1.39
                       , marks = {0: {'label': '0'}, 10: {'label': '10'}}
                       , tooltip = {"placement": "bottom", "always_visible": True}
                       , updatemode="drag"
                       )
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '0 0px'}
            ),
            
    ]),

    html.Div([
        html.Div([
            dcc.Graph(id='curled-graph', animate=True),
        ], style={'width': '40%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='input-signal', animate=True),
            dcc.Graph(id='output-graph', animate=True)
        ], style={'width': '60%', 'display': 'inline-block', 'verticalAlign': 'top'}),
    ]),
])


def generate_signal(time_range, num_points):
    t = np.linspace(0, time_range, num_points)
    signal = (np.sin(2 * np.pi * 1 * t) + 0.5 * np.sin(2 * np.pi * 3 * t)) * 0.5 + 0.6
    return t, signal


@app.callback(
    [
        Output('input-signal', 'figure'),
        Output('curled-graph', 'figure'),
        Output('output-graph', 'figure'),
        Output('time-pointer', 'max'),
        Output('time-pointer', 'value'),
    ],
    [
        Input('time-range', 'value'),
        Input('sampling-points', 'value'),
        Input('winding-frequency', 'value'),
        Input('time-pointer', 'value'),
    ],
)
def update_graphs(time_range, num_points, winding_freq, time_pointer):
    t, signal = generate_signal(time_range, num_points)

    # Input Signal Plot
    input_fig = go.Figure()
    input_fig.add_trace(go.Scatter(x=t, y=signal, mode='lines', name='Input Signal'))
    # Spacing between full revolutions on the complex plane
    spacing = 1 / winding_freq
    # Draw the vertical lines to show the spacing between revolutions
    vertical_lines = np.arange(0, time_range + spacing, spacing)
    y_min, y_max = [min(signal)*1.2, max(signal)*1.2]
    for x in vertical_lines:
        input_fig.add_trace(go.Scatter(
            x=[x, x],
            y=[y_min, y_max],
            mode='lines',
            name='Vertical Line',
            line=dict(color='#AAAAAA', dash='dashdot'),
            showlegend=False
        ))

    input_fig.update_layout(
        title='Input Signal'
        , xaxis_title='Time (s)'
        , yaxis_title='Amplitude'
        , yaxis=dict(range=[y_min, y_max])
        , xaxis=dict(range=[0, time_range])
        , legend = dict(x=1,  # Position at the right edge
                        y=1,  # Position at the top
                        xanchor="right",  # Align the legend box's right edge with `x`
                        yanchor="top",    # Align the legend box's top edge with `y`
                        bgcolor="rgba(255, 255, 255, 0.5)",  # Optional: Semi-transparent background
                        bordercolor="darkgrey",  # Optional: Add a border around the legend
                        borderwidth=1         # Optional: Border width
                    )
        )

    # Curled Graph (Signal Wrapped Around a Circle)
    theta = 2 * np.pi * winding_freq * t
    x = signal * np.cos(theta)
    y = -signal * np.sin(theta)
    curled_fig = go.Figure()
    curled_fig.add_trace(
        go.Scatter(x=x
                   , y=y
                   , mode='lines'
                   , name='Wrapped Signal'
                   , showlegend = True
                   )
        )



    # Show the Origin
    curled_fig.add_trace(
        go.Scatter(
            x=[0],
            y=[0],
            mode='markers',
            marker=dict(color='red', size=8),
            name='Center of Mass (Origin)',
            legendgroup = "vector",
            showlegend=False
            )
        )
    
    # Show the Center of Mass (-> Scaled Fourier Transform)
    curled_fig.add_trace(
        go.Scatter(
            x=[0, np.mean(x)],  # Start and end x-coordinates
            y=[0, np.mean(y)],  # Start and end y-coordinates
            mode='lines+markers',
            line=dict(color='red', width=2),
            marker=dict(symbol='arrow-up', size=10, angleref = 'previous'),
            name='Center of Mass',
            legendgroup='vector',  # Group with the Origin
            showlegend=True  # Only show one legend entry for the group
            )
        )

    
    curled_fig.update_layout(
        title='Fourier Transform on the Complex Plane',
        #xaxis=dict(scaleanchor='y', scaleratio=1),
        xaxis_title='X',
        yaxis_title='Y',
        width = 800,
        height = 800,
        xaxis=dict(range=[-1.5, 1.5]),
        yaxis=dict(range=[-1.5, 1.5]),
        legend = dict(x=1,  # Position at the right edge
                        y=1,  # Position at the top
                        xanchor="right",  # Align the legend box's right edge with `x`
                        yanchor="top",    # Align the legend box's top edge with `y`
                        bgcolor="rgba(255, 255, 255, 0.5)",  # Optional: Semi-transparent background
                        bordercolor="darkgrey",  # Optional: Add a border around the legend
                        borderwidth=1         # Optional: Border width
                    )

    )

    # Fourier Transform
    N = len(signal)*10
    yf = fft(signal, n = N)
    xf = fftfreq(N, (t[1] - t[0]))[:N // 2]
    output_fig = go.Figure()
    output_fig.add_trace(
        go.Scatter(x=xf
                   , y=2.0 / N * np.abs(yf[0:N // 2])
                   , mode='lines'
                   , name='Fourier Transform'
                   , showlegend = True
                   )
        )
    
    # Show the Center of Mass on the Frequency Domain
    freq_idx = np.abs(xf - winding_freq).argmin()
    print(F"{winding_freq=}  {xf[freq_idx]=}  {(2.0 / N * np.abs(yf[freq_idx]))=}")
    output_fig.add_trace(
        go.Scatter(
            x=[xf[freq_idx], xf[freq_idx]],  # Start and end x-coordinates
            y=[0, 2.0 / N * np.abs(yf[freq_idx])],  # Start and end y-coordinates
            mode='lines+markers',
            line=dict(color='red', width=2),
            marker=dict(symbol='arrow-up', size=10, angleref = 'previous'),
            name='Center of Mass',
            showlegend=True  # Only show one legend entry for the group
            )
        )
    output_fig.update_layout(
        title='Fourier Transform'
        , xaxis_title='Frequency (Hz)'
        , yaxis_title='Magnitude'
        #, xaxis = dict(range = [1, np.max(xf)])
        , legend = dict(x=1,  # Position at the right edge
                        y=1,  # Position at the top
                        xanchor="right",  # Align the legend box's right edge with `x`
                        yanchor="top",    # Align the legend box's top edge with `y`
                        bgcolor="rgba(255, 255, 255, 0.5)",  # Optional: Semi-transparent background
                        bordercolor="darkgrey",  # Optional: Add a border around the legend
                        borderwidth=1         # Optional: Border width
                    )
        )

    if time_pointer is not None:
        mid_time = time_pointer
        idx = np.abs(t - time_pointer).argmin()

        input_fig.add_trace(go.Scatter(
            x=[time_pointer, time_pointer],
            y=[0, signal[idx]],
            mode='lines',
            name='Time Pointer',
            line=dict(color='darkgreen', dash='dot')
        ))

        curled_fig.add_trace(go.Scatter(
            x= [0, x[idx]],
            y= [0, y[idx]],
            mode='lines+markers',
            name='Signal Ampliture',
            line=dict(color='darkgreen', width=2, dash='dot')
        ))

        # curled_fig.update_layout(
        #     annotations=[
        #         dict(
        #             ax=0, ay=0,  # Start point (origin)
        #             x=np.mean(x), y=np.mean(y),  # End point
        #             xref = "x", yref = "y",
        #             axref = "x", ayref = "y",
        #             arrowhead = 3,  # Arrowhead style
        #             arrowwidth = 2,
        #             arrowcolor = "red",
        #             legendgroup = "vector"
        #         )
        #     ],
        #     xaxis=dict(scaleanchor='y', scaleratio=1),  # Link x and y axis scales
        #     yaxis=dict(scaleanchor='x')  # Ensure both axes have the same scaling
        # )

    else:
        mid_time = time_range / 2


    return input_fig, curled_fig, output_fig, time_range, mid_time


if __name__ == '__main__':
    app.run_server(debug=True)