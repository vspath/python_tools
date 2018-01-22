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
from bokeh.embed import file_html
from bokeh.resources import CDN
from bokeh.layouts import gridplot


def split_df_by_value_range(df, round_base=-3, threshold=100):
    range_means = df.mean().round(round_base).unique()
    num_range = len(range_means)

    avg = df.mean()

    # subdivide values dataframe by value range and store them into a dict
    df_dict = {}
    for r_mean in range_means:
        df_dict[r_mean] = pd.DataFrame()

    for col in df.columns:
        for r_mean in range_means:
            if abs(round(df[col].mean(), round_base) - r_mean) < threshold:
                df_dict[r_mean][df[col].name] = df[col]

    return df_dict


def plot_df_bokeh(df,
                  save_plot=False,
                  output_path= os.getcwd(),
                  output_filename= "data.html",
                  hook_att_df=None,
                  title=None,
                  time_series=False,
                  x_axis_label=None,
                  y_axis_label=None,
                  label={}):

    formatter = {}

    # Create Figure object
    if time_series:
        x_axis_type = "datetime"
    else:
        x_axis_type = "auto"

    if not df.index.name:
        df.index.name = "index"

    p = figure(title=title,
               x_axis_label=x_axis_label,
               y_axis_label=y_axis_label,
               x_axis_type=x_axis_type,
               width=800, height=500,
               #tools = "pan,box_zoom,wheel_zoom,save,reset,hover",
               toolbar_location="above")


    # create invisible datacolumn where hook will be attached
    if hook_att_df is None:
        df['invisible'] = df[df.columns[0]]
    else:
        df['invisible'] = df[hook_att_df]

    # create a color iterator
    colors = itertools.cycle(palette)

    # remove "/" from column names
    cols = [c.replace("/", "_") for c in list(df.columns)]

    df.columns = cols

    #---------------------------------------------------------
    # define dataframe columns as data source
    source = ColumnDataSource(df)

    # plot column data
    for name, color in zip(df, colors):
        # add invisible line to anchor tooltip
        if name == 'invisible':
            p.line(x=df.index.name,
                   y=name,
                   source=source,
                   line_alpha=0,
                   name='tooltip_anchor')
        else:
            p.line(x=df.index.name,
                   y=name,
                   source=source,
                   legend=f"{name}_values",
                   color=color)

    # interactive legend, allows to hide single lines
    p.legend.location = "top_right"
    p.legend.click_policy = "hide"


    # add all columns to hovertool except the invisible one where the hovertool will be attached to
    tooltips = [(c, '@' + c) for c in cols if c != 'invisible']

    if time_series:
        tooltips.append((df.index.name, "@" + df.index.name + "{%F %T}"))
        formatter = {df.index.name: 'datetime'}

    # create hover tool
    hover = HoverTool(tooltips=tooltips,
                      formatters=formatter,
                      mode='vline',
                      names=['tooltip_anchor'],
                      line_policy="nearest")

    # add hover to figure
    p.add_tools(hover)


    # add meta info to plot
    if label:
        if isinstance(label, dict):
            for key, value in label.items():
                lab = Label(x=10, y=30, x_units='screen', y_units='screen',
                            text=value,
                            render_mode='css',
                            border_line_color='black', border_line_alpha=1.0,
                            text_font_size='11pt',
                            background_fill_color='white', background_fill_alpha=1.0)
                p.add_layout(lab)

        elif isinstance(label, str):
            lab = Label(x=10, y=30, x_units='screen', y_units='screen',
                        text=label,
                        render_mode='css',
                        border_line_color='black', border_line_alpha=1.0,
                        text_font_size='11pt',
                        background_fill_color='white', background_fill_alpha=1.0)
            p.add_layout(lab)


    if save_plot:
        if "." not in output_filename:
            output_filename = output_filename + ".html"
        # save html
        print("File saved as:", os.path.join(output_path, output_filename))
        html = file_html(p, CDN)
        with open(f"{output_path}/{output_filename}", "w") as f:
            f.write(html)

    return (p)





def plot_df_dict_bokeh(df_dict,
                  save_plot=False,
                  output_path= os.getcwd(),
                  output_filename= "data.html",
                  hook_att_df=None,
                  title=None,
                  time_series=False,
                  x_axis_label=None,
                  y_axis_label=None,
                  label={}):

    tooltips = []
    formatter = {}

    #---------------------------------------------------------
    # Create Figure object
    if time_series:
        x_axis_type = "datetime"
    else:
        x_axis_type = "auto"

    p = figure(title=title,
               x_axis_label=x_axis_label,
               y_axis_label=y_axis_label,
               x_axis_type=x_axis_type,
               width=800, height=500,
               #tools = "pan,box_zoom,wheel_zoom,save,reset,hover",
               toolbar_location="above")


    # create invisible datacolumn where hook will be attached
    if hook_att_df is None:
        key_inv = list(df_dict.keys())[0]
        df_dict[key_inv]['invisible'] = df_dict[key_inv][df_dict[key_inv].columns[0]]
    else:
        df_dict[hook_att_df]['invisible'] = df_dict[hook_att_df][df_dict[hook_att_df].columns[0]]

    # create a color iterator
    colors = itertools.cycle(palette)


    # ----------------
    # Hovertool

    #TODO: hover tool needs all the columns added to ColumnDataSource for displaying the values
    cols = []
    for df in df_dict.values():
        cols.extend(list(df.columns.values))
    cols = [c.replace("/", "_") for c in cols]

    # add all columns to hovertool except the invisible one where the hovertool will be attached to
    tooltips = [(c, '@' + c) for c in cols if c != 'invisible']


    #---------------------------------------------------------
    # iterate over dataframes in dict and create a new y-range for each dataframe
    for key, df in df_dict.items():

        # define dataframe columns as data source
        source = ColumnDataSource(df)

        if time_series:
            if len([k for (k, v) in tooltips if k == df.index.name]) == 0:
                tooltips.append((df.index.name, "@" + df.index.name + "{%F %T}"))
                formatter = {df.index.name: 'datetime'}

        # define y ranges
        range_min = df.values.min()
        range_max = df.values.max()
        range_offset = (range_max - range_min) / 10

        # dataframe which contains the hook-attach-column defines the basic y-range
        if 'invisible' in df.columns:

            p.y_range = Range1d(start=range_min - range_offset,
                                end=range_max + range_offset)

            for name, color in zip(df, colors):
                # add invisible line to anchor tooltip
                if name == 'invisible':
                    p.line(x=df.index.name,
                           y=name,
                           source=source,
                           line_alpha=0,
                           name='tooltip_anchor')
                else:
                    p.line(x=df.index.name,
                           y=name,
                           source=source,
                           legend=f"{name}_values",
                           color=color)

        # for all other dataframes new y-ranges are added
        else:
            range_name = f"{key}_range"
            p.extra_y_ranges = {range_name: Range1d(start=range_min - range_offset,
                                                    end=range_max + range_offset)}
            # Adding the second axis to the plot.
            p.add_layout(LinearAxis(y_range_name=range_name), 'right')

            for name, color in zip(df, colors):
                p.line(x=df.index.name,
                       y=name,
                       source=source,
                       y_range_name=range_name,
                       legend=f"{name}_values",
                       color=color)




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

    # create hover tool
    hover = HoverTool(tooltips=tooltips,
                      formatters=formatter,
                      mode='vline',
                      names=['tooltip_anchor'],
                      line_policy="nearest")
    # add hover to figure
    p.add_tools(hover)

    if save_plot:
        if "." not in output_filename:
            output_filename = output_filename + ".html"
        # save html
        print("File saved as:", os.path.join(output_path, output_filename))
        html = file_html(p, CDN)
        with open(f"{output_path}/{output_filename}", "w") as f:
            f.write(html)

    return (p)




#df = pd.DataFrame()
#df['temp'] = [29,30,28,29]
#df['temp2'] = [27,25,26,28]

#print(df.head())

#plot_df_bokeh(df, save_plot=True, output_path="/Users/VeSpa/Desktop", output_filename="test.html")

