import os
import pandas as pd
import matplotlib.pyplot as plt
import json
import pprint
import itertools

from bokeh.io import push_notebook, show, output_notebook
from bokeh.plotting import figure, output_file
from bokeh.models import ColumnDataSource, LinearAxis, Range1d, HoverTool, Label
from bokeh.palettes import Set1_5 as palette # select a palette
from bokeh.layouts import gridplot


def plot_df_bokeh(df,
                  output_path=os.getcwd(),
                  output_file="data.html",
                  hook_att_col=None,
                  title=None,
                  label=dict()):
    output_notebook()

    # create invisible datacolumn where hook will be attached
    if hook_att_col is None:
        df['invisible'] = df[df.columns[0]]
    else:
        df['invisible'] = df[hook_att_col]

    tooltips = []
    for col in df.columns:
        form = ""
        # if isinstance(df[col][0], float):
        #    form = "{(00.00)}"
        tooltips.append((col, "@" + col + form))

    if isinstance(df.index[0], pd.Timestamp):
        tooltips.append(('timestamp', "@" + col + "{%F}"))
        formatter = {'timestamp': 'datetime'}
        x_axis_type = "datetime"

    # Create hover tool
    hover = HoverTool(tooltips=tooltips,
                      # TODO: add formatters (modify datetime, decimal points, etc.)
                      formatters=formatter,
                      mode='vline',
                      names=['tooltip_anchor'],
                      line_policy="nearest")

    # Create new figure
    p = figure(title=title,
               x_axis_label='time',
               y_axis_label='Temperature in degree C',
               # x_axis_type= x_axis_type,
               # y_range=[22,42], #TODO: insert min/max + offset to set range automatically
               width=800, height=500,
               toolbar_location="above")

    # create a color iterator
    colors = itertools.cycle(palette)

    # define dataframe columns as data source
    source = ColumnDataSource(df)

    for name, color in zip(df, colors):
        # add invisible line to anchor tooltip
        if name == 'invisible':
            line = p.line(x='timestamp',
                          y=name,
                          source=source,
                          line_alpha=0,
                          name='tooltip_anchor')
        else:
            source = ColumnDataSource(df)
            p.line(x='timestamp',
                   y=name,
                   source=source,
                   legend=f"{name}_values",
                   color=color)

    # add hover to figure
    # p.add_tools(hover)

    # interactive legend, allows to hide single lines
    p.legend.location = "top_right"
    p.legend.click_policy = "hide"

    # add meta info to plot
    if label:
        for key, value in label.items():
            lab = Label(x=10, y=30, x_units='screen', y_units='screen',
                        text=value,
                        render_mode='css',
                        border_line_color='black', border_line_alpha=1.0,
                        text_font_size='11pt',
                        background_fill_color='white', background_fill_alpha=1.0)
            p.add_layout(lab)

    # display plot
    # save html
    show(p)
    return (p)


