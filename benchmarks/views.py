#####
# System includes
###
import re
import decimal
import csv
import json
from math import floor, log
from collections import OrderedDict
import pandas
import numpy

#####
# Django includes
###
from django.shortcuts import render, render_to_response
from django.db.models import Sum, Avg
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

#####
# Third-party includes
###

# Bokeh
from bokeh import palettes
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import components
from bokeh.models import (
    CustomJS, ColumnDataSource, Legend,
    HoverTool, PanTool, BoxZoomTool, CrosshairTool,
    ResetTool, SaveTool, WheelZoomTool,
)
from bokeh.models.widgets import (
    Slider, Select, CheckboxGroup, Div, RadioGroup, CheckboxButtonGroup,
    RadioButtonGroup,
)
from bokeh.layouts import column, row

# Misc.
from pandas_datareader import wb

# Guardian
from guardian.shortcuts import get_perms, get_objects_for_user


#####
# Project includes
###
from techlab_systems.models import SystemConfiguration, HardwareConfiguration
from SSD.models import SSD
from software_configuration.models import OS, LinuxKernel
from hardware_configuration.models import CPU
from benchmarks.models import (
    # HEPSpec06
    HEPSPEC06Run,
    # ssdbench_l2
    SSDBenchL2, SSDBenchL2Stability,
    # ssdbench_l3
    SSDBenchL3Analytics, SSDBenchL3Checkpointing, SSDBenchL3HFT,
    SSDBenchL3Db8kpage, SSDBenchL3BigBlock, SSDBenchL3OLTP, SSDBenchL3Metadata,
)
from benchmarks.forms import ImportSSDBenchmarkForm


#####
# Utilities
###
def DEBUG(var, text=None):
    print("############ DEBUG ############")
    if text:
        print(text)
    print("{}".format(var))
    print("########## ENDDEBUG ###########")


def is_integer(x):
    try:
        f_x = float(x)
        i_x = int(x)
        return f_x == i_x
    except:
        return False


def is_float(x):
    try:
        f_x = float(x)
        i_x = int(x)
        return f_x != i_x
    except:
        return False


def is_list_of_integer(l):
    for x in l:
        if not is_integer(x):
            return False
    return True


def is_list_of_floats(l):
    for x in l:
        if not is_float(x):
            return False
    return True


def int_or_none(i):
    return int(i) if i else None


def dec_or_none(d):
    return decimal.Decimal(d) if d else None


def checkbox_group_build_checked_list(filter_name):
    return """
    var {name}_checked = [];
    if ( {name}_obj.active.length > 0 ) {{
        for ( id of {name}_obj.active ) {{
            {name}_checked.push({name}_obj.labels[id])
        }}
    }} else {{
        for ( label of {name}_obj.labels ) {{
            {name}_checked.push(label)
        }}
    }}
    """.format(name=filter_name)


def first(x):
    return x.iloc[0]


def get_runs_for_user(request):
    available_hardware_configurations = get_objects_for_user(
        request.user,
        klass=HardwareConfiguration,
        perms='view_bench'
    )
    return HEPSPEC06Run.objects.filter(
        system_configuration__hardware_configuration__in=available_hardware_configurations)


def get_allowed_ssd_benchmark_entries_for_user(request, modelclass):
    allowed_ssds = get_objects_for_user(
        request.user,
        klass=SSD,
        perms='view_bench')
    return modelclass.objects.filter(ssd__in=allowed_ssds)


def init_filter_values(filters):
    js_code = ""
    for k, v in filters.items():
        if v['type'].startswith('checkbox'):
            js_code += """
var {key}_checked = [];
if ( {key}.active.length > 0 ) {{
    for ( id of {key}.active ) {{
        {key}_checked.push({key}.labels[id])
    }}
}} else {{
    for ( label of {key}.labels ) {{
        {key}_checked.push(label)
    }}
}}
""".format(key=k)
        elif v['type'] == 'select':
            js_code += "var {key}_selected = {key}.value;\n".format(key=k)
        elif v['type'] == 'slider_min':
            js_code += "var {key} = {key}.value;\n".format(key=k)
        elif v['type'] == 'slider_max':
            js_code += "var {key} = {key}.value;\n".format(key=k)

    return js_code


def init_filter_condition(filters, suffix="", source_suffix=""):
    conditions = []
    suffix_ = "_' + {}".format(suffix) if suffix else "'"
    source_suffix_ = "_{}".format(source_suffix) if source_suffix else ""
    for k, v in filters.items():
        if v['type'].startswith('checkbox'):
            conditions.append("{key}_checked.indexOf(original_data{source_suffix}['{ds_column}{suffix}][i]) >= 0".format(key=k, ds_column=v['ds_column'], suffix=suffix_, source_suffix=source_suffix_))
        elif v['type'] == 'select':
            conditions.append("{key}_selected === original_data{source_suffix}['{ds_column}{suffix}][i]".format(key=k, ds_column=v['ds_column'], suffix=suffix_, source_suffix=source_suffix_))
        elif v['type'] == 'slider_min':
            conditions.append("original_data{source_suffix}['{ds_column}{suffix}][i] >= parseFloat({key})".format(key=k, ds_column=v['ds_column'], suffix=suffix_, source_suffix=source_suffix_))
        elif v['type'] == 'slider_max':
            conditions.append("original_data{source_suffix}['{ds_column}{suffix}][i] <= parseFloat({key})".format(key=k, ds_column=v['ds_column'], suffix=suffix_, source_suffix=source_suffix_))
    return " && ".join(conditions)


#####
# Views
###
def home(request):
    return render(request, "benchmarks/home.html", {})


def cpu_benchmarks(request):

    # Get data
    runs = get_runs_for_user(request)
    if not runs:
        return render(request, "benchmarks/no_privilege.html", {})

    # Select fields
    fields = [
        {'name': 'pk', 'path': 'system_configuration.pk', 'agg': first, 'dtype': 'int'},
        {'name': 'system_configuration', 'path': 'system_configuration', 'agg': first, 'dtype': 'str'},
        {'name': 'nb_workers', 'path': 'nb_workers', 'agg': first, 'dtype': 'int'},
        {'name': 'score', 'path': 'score', 'agg': numpy.mean, 'dtype': 'float'},
        # {'name': 'os', 'path': 'system_configuration.software_configuration.os', 'agg': (lambda x: "[{}]".format(', '.join(x))), 'dtype': 'str'},
        {'name': 'os', 'path': 'system_configuration.software_configuration.os', 'agg': first, 'dtype': 'str'},
        {'name': 'architecture', 'path': 'system_configuration.hardware_configuration.architecture.name', 'agg': first, 'dtype': 'str'},
        {'name': 'owner', 'path': 'system_configuration.hardware_configuration.owner', 'agg': first, 'dtype': 'str'},
        {'name': 'active_energy', 'path': 'active_energy', 'agg': numpy.mean, 'dtype': 'float'},
        {'name': 'apparent_energy', 'path': 'apparent_energy', 'agg': numpy.mean, 'dtype': 'float'},
        # {'name': 'score_by_worker', 'path': 'score', 'agg': numpy.mean, 'operations': {['nb_workers', 'divide'],}},
    ]

    # Build bokeh data sources
    configuration_pks = list(set([run.system_configuration.pk for run in runs]))

    # Build raw DataFrame with all necessary fields from the HEPSPEC06 runs
    df_data = {}
    for field in fields:
        exec("df_data['{name}'] = [{dtype}(run.{path}) for run in runs]".format(name=field['name'], dtype=field['dtype'], path=field['path']))
    df = pandas.DataFrame(df_data)

    grouped_df = df.groupby(['pk', 'nb_workers']).agg({field['name']: field['agg'] for field in fields})
    ds = ColumnDataSource()
    ds.add(configuration_pks, 'pks')

    for pk in configuration_pks:
        for field in fields:
            ds.add(list(grouped_df[grouped_df['pk'] == pk][field['name']].as_matrix()), '{}_{}'.format(field['name'], pk))

    original_ds = ColumnDataSource()
    for key in ds.column_names:
        original_ds.add(ds.data[key], key)

    # Build plots
    plots = [
        {'title': 'Score / Workers', 'x': 'nb_workers', 'y': 'score', 'source': ds},
        {'title': 'Active Energy / Workers', 'x': 'nb_workers', 'y': 'active_energy', 'source': ds},
        {'title': 'Apparent Energy / Workers', 'x': 'nb_workers', 'y': 'apparent_energy', 'source': ds},
        {'title': 'Workers / Workers', 'x': 'nb_workers', 'y': 'nb_workers', 'source': ds},
    ]
    for plot in plots:
        tools = [
            PanTool(), BoxZoomTool(), CrosshairTool(),
            WheelZoomTool(), ResetTool(), SaveTool()
        ]
        plot['figure'] = figure(title=plot['title'], toolbar_location='right', tools=tools, x_axis_label=plot['x'], y_axis_label=plot['y'])
        pks = plot['source'].data['pks']
        legends = []
        for n, pk, color in zip(range(10), pks, palettes.magma(len(pks))):
            # exec("legend_text = plot['source'].data['system_configuration_{}'][0]"    .format(pk))
            legend_text = runs.filter(system_configuration__pk=pk)[0].system_configuration.hardware_configuration.name
            line = plot['figure'].line(
                "{}_{}".format(plot['x'], pk),
                "{}_{}".format(plot['y'], pk),
                source=plot['source'],
                line_width=3, line_alpha=0.5, color=color
            )
            circle = plot['figure'].circle(
                "{}_{}".format(plot['x'], pk),
                "{}_{}".format(plot['y'], pk),
                source=plot['source'],
                size=8, fill_color='white', color=color
            )
            legends += [(legend_text, [line, circle])]
        legend = Legend(legends=legends, location=(60, 0))
        plot['figure'].add_layout(legend, 'below')

    # Build filters
    filters = OrderedDict()
    filters['nb_workers_min'] = {'type': 'slider_min', 'category': 'benchmark', 'description': 'Filter benchmark runs below a minimum number of workers.', 'ds_column': 'nb_workers', 'init': min}
    filters['nb_workers_max'] = {'type': 'slider_max', 'category': 'benchmark', 'description': 'Filter benchmark runs above a maximum number of workers.', 'ds_column': 'nb_workers', 'init': max}
    filters['architecture'] = {'type': 'checkbox_group', 'category': 'hardware', 'description': 'Select hardware architectures.', 'ds_column': 'architecture'}
    filters['os'] = {'type': 'checkbox_group', 'category': 'software', 'description': 'Select operating systems.', 'ds_column': 'os'}
    filters['owner'] = {'type': 'checkbox_group', 'category': 'hardware', 'description': 'Select a project.', 'ds_column': 'owner'}
    filters['system'] = {'type': 'checkbox_group', 'category': 'hardware', 'description': 'Select a configuration.', 'ds_column': 'system_configuration'}

    pks = [pk for pk in original_ds.data['pks']]
    for name, f in filters.items():
        value_set = sorted(list(set(
            [value for value in sum([original_ds.data['{}_{}'.format(f['ds_column'], pk)] for pk in pks], [])]
        )))
        if f['type'].startswith('slider'):
            step = 1 if is_list_of_integer(value_set) else 10**floor(log(min([value_set[i + 1] - value_set[i] for i in range(len(value_set)) if i + 1 < len(value_set)]), 10))
            f['object'] = Slider(
                title=name,
                start=min(value_set),
                end=max(value_set),
                value=f['init'](value_set),
                step=step
            )
        elif f['type'] == 'checkbox_group':
            f['object'] = CheckboxGroup(labels=value_set)
        elif f['type'] == 'checkbox_button_group':
            f['object'] = CheckboxButtonGroup(labels=value_set)
        elif f['type'] == 'select':
            f['object'] = Select(
                title=name, value=value_set[0], options=value_set
            )

    callback_code = """
var data = source.data;
var original_data = original_source.data;

// Init filter values
{init_filter_values}

for ( var j = 0; j < original_data['pks'].length; j++ ) {{
    var pk = original_data['pks'][j];
    data['nb_workers_' + pk] = [];
    data['score_' + pk] = [];
    for ( var i=0; i<original_data[Object.keys(original_data)[0]].length; i++ ) {{
        if (
            {filter_condition}
        ) {{
            data['nb_workers_' + pk].push(original_data['nb_workers_' + pk][i]);
            data['score_' + pk].push(original_data['score_' + pk][i]);
        }}
    }}
}}

source.trigger('change');
""".format(
        init_filter_values=init_filter_values(filters),
        filter_condition=init_filter_condition(filters, "pk")
    )

    # now define the callback objects now that the filter widgets exist
    callback_source_args = {'source': ds, 'original_source': original_ds}
    callback_filter_args = {k: v['object'] for k, v in filters.items()}
    callback_args = dict(callback_filter_args, **callback_source_args)

    generic_callback = CustomJS(
        args=callback_args,
        code=callback_code
    )

    for name, f in filters.items():
        f['object'].callback = generic_callback

    # Build component
    plots_layout = column([plot['figure'] for plot in plots], sizing_mode='scale_width')
#    plots2 = row(plot2, sizing_mode='scale_width')
    widgets_list = []
    for name, f in filters.items():
        widgets_list.append(Div(text="<h3>{}</h3>".format(name)))
        widgets_list.append(f['object'])
    widgets = column([w for w in widgets_list], sizing_mode='scale_width')
#    widgets = column([f['object'] for name, f in filters.items()], sizing_mode='scale_width')

    script, elements_to_render = components([widgets, plots_layout], wrap_plot_info=False)
    context = {
        'bokeh_script': script,
        'bokeh_widgets': [elements_to_render[0]],
        'bokeh_plots': elements_to_render[1:],
    }

    return render(request, 'benchmarks/bokeh_base.html', context)


def import_l2_csv(request):
    # Get Form data
    ssd = SSD.objects.get(pk=request.POST['ssd'])
    filename = request.FILES['file']
    os = OS.objects.get(pk=request.POST['os']) if request.POST['os'] else None
    kernel = LinuxKernel.objects.get(pk=request.POST['kernel']) if request.POST['kernel'] else None
    cpu = CPU.objects.get(pk=request.POST['cpu']) if request.POST['cpu'] else None

    columns = 'percent_capacity_used,acces_type,percent_write,block_size,threads,qd_per_thread,iops,throughput,read_latency,write_latency,comment'
    content = filename.read()
    filename.close()
    pattern = re.compile("^[^,\n]+$", re.VERBOSE | re.MULTILINE)
    block_indices = [match.start() for match in pattern.finditer(content)]
    block_indices.append(len(content))
    added, ignored = [], []
    for i in range(len(block_indices) - 1):
        block = content[block_indices[i]:block_indices[i + 1]].strip('\n').split('\n')
        test_description = block[0]
        runs = block[1:]
        for run in runs:
            args = run.split(',')
            obj, created = SSDBenchL2.objects.get_or_create(
                test_description=test_description,
                percent_capacity_used=int(args[0]),
                access_type=SSDBenchL2.import_access_type(args[1]),
                percent_write=int(args[2]),
                block_size=int(args[3]),
                threads=int(args[4]),
                qd_per_thread=int(args[5]),
                iops=dec_or_none(args[6]),
                throughput=int(args[7]),
                read_latency=dec_or_none(args[8]),
                write_latency=dec_or_none(args[9]),
                comment=args[10],
                ssd=ssd,
                os=os, cpu=cpu, kernel=kernel
            )
            if created:
                added.append(run)
            else:
                ignored.append(run)
    return added, ignored


def import_l3_csv(data):
    # Get Form data
    ssd = data['ssd']
    os = data['os']
    kernel = data['kernel']
    cpu = data['cpu']

    # Read uploaded file content
    content = data['file'].read()
    data['file'].close()

    added, ignored = [], []
    for line in content.splitlines()[1:]:
        values = line.split(',')
        obj, created = None, False
        if values[0] == 'analytics':
            obj, created = SSDBenchL3Analytics.objects.get_or_create(
                ssd=ssd, os=os, cpu=cpu, kernel=kernel,
                rdmbps=values[9], wrmbps=values[5], rdiops=values[11], wriops=values[7]
            )
        elif values[0] == 'checkpointing':
            obj, created = SSDBenchL3Checkpointing.objects.get_or_create(
                ssd=ssd, os=os, cpu=cpu, kernel=kernel,
                rdmbps=values[9], wrmbps=values[5], rdiops=values[11], wriops=values[7]
            )
        elif values[0] == 'hft':
            obj, created = SSDBenchL3HFT.objects.get_or_create(
                ssd=ssd, os=os, cpu=cpu, kernel=kernel,
                rdmbps=values[9], wrmbps=values[5], rdiops=values[11], wriops=values[7]
            )
        elif values[0] == 'db8kpage':
            obj, created = SSDBenchL3Db8kpage.objects.get_or_create(
                ssd=ssd, os=os, cpu=cpu, kernel=kernel,
                rdmbps=values[9], wrmbps=values[5], rdiops=values[11], wriops=values[7]
            )
        elif values[0] == 'bigblock':
            obj, created = SSDBenchL3BigBlock.objects.get_or_create(
                ssd=ssd, os=os, cpu=cpu, kernel=kernel,
                rdmbps=values[9], wrmbps=values[5], rdiops=values[11], wriops=values[7]
            )
        elif values[0] == 'oltp':
            obj, created = SSDBenchL3OLTP.objects.get_or_create(
                ssd=ssd, os=os, cpu=cpu, kernel=kernel,
                p99rd=values[5], p99wr=values[7]
            )
        elif values[0] == 'metadata':
            obj, created = SSDBenchL3Metadata.objects.get_or_create(
                ssd=ssd, os=os, cpu=cpu, kernel=kernel,
                creation=values[5], deletion=values[7]
            )
        if created:
            added.append("ssdbench_l3 {} for {}: {}".format(values[0], ssd, line))
        else:
            ignored.append(line)

    return added, ignored


def import_l2_stability_csv(data):
    # Get Form data
    ssd = data['ssd']
    os = data['os']
    kernel = data['kernel']
    cpu = data['cpu']

    # Read uploaded file content
    content = data['file'].read()
    data['file'].close()

    iops_array = [value for value in content.splitlines()[1:]]
    obj, created = SSDBenchL2Stability.objects.get_or_create(
        ssd=ssd, os=os, cpu=cpu, kernel=kernel, iops=iops_array
    )
    added, ignored = [], []
    entry = "stability test for ssd {}: {}".format(ssd, iops_array)
    if created:
        added.append(entry)
    else:
        ignored.append(entry)
    return added, ignored


def import_benchmarks(request):
    filename = "No file uploaded"
    content = ""
    if request.method == 'POST':
        form = ImportSSDBenchmarkForm(request.POST, request.FILES)
        if form.is_valid():
            filename = request.FILES['file']
            ssd = request.POST['ssd']
            added, ignored = [], []
            if(request.POST['benchmark_type'] == 'l2'):
                added, ignored = import_l2_csv(request)
            elif(request.POST['benchmark_type'] == 'stability'):
                added, ignored = import_l2_stability_csv(form.cleaned_data)
            elif(request.POST['benchmark_type'] == 'l3'):
                added, ignored = import_l3_csv(form.cleaned_data)
            if added != []:
                content += "The following entries have been added\n"
                for line in added:
                    content += "{}\n".format(line)
            if ignored != []:
                content += "The following entries have been ignored\n"
                for line in ignored:
                    content += "{}\n".format(line)
    else:
        form = ImportSSDBenchmarkForm()
    context = {'form': form, 'content': content}
    return render(request, 'benchmarks/import_benchmarks.html', context)


def ssd_benchmarks(request):

    # Get data
    l2_entries = get_allowed_ssd_benchmark_entries_for_user(request, SSDBenchL2)
    if not l2_entries:
        return render(request, "benchmarks/no_privilege.html", {})

    fields = [
        {'name': 'pk', 'path': 'ssd.pk', 'agg': first, 'dtype': 'int'},
        {'name': 'ssd', 'path': 'ssd', 'agg': first, 'dtype': 'str'},
        {'name': 'os', 'path': 'os', 'agg': first, 'dtype': 'str'},
        {'name': 'manufacturer', 'path': 'ssd.manufacturer.name', 'agg': first, 'dtype': 'str'},
        {'name': 'form_factor', 'path': 'ssd.form_factor.name', 'agg': first, 'dtype': 'str'},
        {'name': 'interface', 'path': 'ssd.interface.name', 'agg': first, 'dtype': 'str'},
        {'name': 'percent_capacity_used', 'path': 'percent_capacity_used', 'agg': first, 'dtype': 'int'},
        {'name': 'access_type', 'path': 'access_type', 'agg': first, 'dtype': 'int'},
        {'name': 'percent_write', 'path': 'percent_write', 'agg': first, 'dtype': 'int'},
        {'name': 'block_size', 'path': 'block_size', 'agg': first, 'dtype': 'int'},
        {'name': 'threads', 'path': 'threads', 'agg': first, 'dtype': 'int'},
        {'name': 'qd_per_thread', 'path': 'qd_per_thread', 'agg': first, 'dtype': 'int'},
        {'name': 'iops', 'path': 'iops', 'agg': first, 'dtype': 'int'},
        {'name': 'throughput', 'path': 'throughput', 'agg': first, 'dtype': 'int'},
        {'name': 'read_latency', 'path': 'read_latency', 'agg': first, 'dtype': 'dec_or_none'},
        {'name': 'write_latency', 'path': 'write_latency', 'agg': first, 'dtype': 'dec_or_none'},
        {'name': 'test_description', 'path': 'test_description', 'agg': first, 'dtype': 'str'},
        {'name': 'capacity', 'path': 'ssd.capacity', 'agg': first, 'dtype': 'int'},
    ]

    # Build bokeh data sources
    ssd_pks = list(set([entry.ssd.pk for entry in l2_entries]))

    # Build raw DataFrame with all necessary fields
    df_data = {}
    for field in fields:
        exec("df_data['{name}'] = [{dtype}(entry.{path}) for entry in l2_entries]".format(name=field['name'], dtype=field['dtype'], path=field['path']))
    df = pandas.DataFrame(df_data)

    grouped_df = df.groupby(['pk', 'test_description']).agg({field['name']: field['agg'] for field in fields})
    original_ds = ColumnDataSource()
    original_ds.add(ssd_pks, 'pks')
    ds = ColumnDataSource()
    ds.add(ssd_pks, 'pks')

    for pk in ssd_pks:
        for field in fields:
            original_ds.add(list(grouped_df[grouped_df['pk'] == pk][field['name']].as_matrix()), '{}_{}'.format(field['name'], pk))
            ds.add(list(grouped_df[grouped_df['pk'] == pk][field['name']].as_matrix()), '{}_{}'.format(field['name'], pk))

    # Build plots
    tests = [
        {"description": "Sustained Multi-Threaded Random Write Tests by Block Size", "x": "block_size", "y": "iops", "test_id": "1"},
        {"description": "Sustained Multi-Threaded Random Write Tests by Block Size", "x": "block_size", "y": "throughput", "test_id": "2"},
        {"description": "Sustained 4KB Random Write Tests by Number of Threads", "x": "threads", "y": "iops", "test_id": "3"},
        {"description": "Sustained 4KB Random Write Tests by Number of Threads", "x": "threads", "y": "throughput", "test_id": "4"},
        {"description": "Sustained 4KB Random mixed 30% Write Tests by Number Threads", "x": "threads", "y": "iops", "test_id": "5"},
        {"description": "Sustained 4KB Random mixed 30% Write Tests by Number Threads", "x": "threads", "y": "throughput", "test_id": "6"},
        {"description": "Sustained Multi-Threaded Random Read Tests by Block Size", "x": "block_size", "y": "iops", "test_id": "7"},
        {"description": "Sustained Multi-Threaded Random Read Tests by Block Size", "x": "block_size", "y": "throughput", "test_id": "8"},
        {"description": "Sustained Multi-Threaded Random Read Tests by Block Size", "x": "block_size", "y": "read_latency", "test_id": "9"},
    ]

    for test in tests:
        test['dataframe'] = df[df['test_description'] == test['description']].groupby(['pk', 'test_description', test['x']]).agg({field['name']: field['agg'] for field in fields})
        test['datasource'] = ColumnDataSource()
        test['datasource'].add(ssd_pks, 'pks')
        test['original_datasource'] = ColumnDataSource()
        test['original_datasource'].add(ssd_pks, 'pks')
        for pk in ssd_pks:
            for field in fields:
                test['datasource'].add(list(test['dataframe'][test['dataframe']['pk'] == pk][field['name']].as_matrix()), '{}_{}'.format(field['name'], pk))
                test['original_datasource'].add(list(test['dataframe'][test['dataframe']['pk'] == pk][field['name']].as_matrix()), '{}_{}'.format(field['name'], pk))

    for test in tests:
        tools = [PanTool(), BoxZoomTool(), CrosshairTool(), WheelZoomTool(), ResetTool(), SaveTool()]
        test['figure'] = figure(title=test['description'], toolbar_location='right', tools=tools, x_axis_label=test['x'], y_axis_label=test['y'])
        pks = test['datasource'].data['pks']
        legends = []
        for n, pk, color in zip(range(10), pks, palettes.magma(len(pks))):
            legend_text = l2_entries.filter(ssd__pk=pk)[0].ssd.__unicode__()
            line = test['figure'].line("{}_{}".format(test['x'], pk), "{}_{}".format(test['y'], pk), source=test['datasource'], line_width=3, line_alpha=0.5, color=color)
            circle = test['figure'].circle("{}_{}".format(test['x'], pk), "{}_{}".format(test['y'], pk), source=test['datasource'], size=8, fill_color='white', color=color)
            legends += [(legend_text, [line, circle])]
        legend = Legend(legends=legends, location=(60, 0))
        test['figure'].add_layout(legend, 'below')

    # Build filters
    filters = OrderedDict()
    filters['ssd'] = {'type': 'checkbox_group', 'category': 'hardware', 'description': 'Filter ssds by model', 'ds_column': 'ssd'}
    filters['os'] = {'type': 'checkbox_group', 'category': 'hardware', 'description': 'Filter oss by model', 'ds_column': 'os'}
    filters['manufacturer'] = {'type': 'checkbox_group', 'category': 'hardware', 'description': 'Filter ssds by manufacturer', 'ds_column': 'manufacturer'}
    filters['form_factor'] = {'type': 'checkbox_group', 'category': 'hardware', 'description': 'Filter ssds by form_factor', 'ds_column': 'form_factor'}
    filters['interface'] = {'type': 'checkbox_group', 'category': 'hardware', 'description': 'Filter ssds by interface', 'ds_column': 'interface'}
    filters['capacity_min'] = {'type': 'slider_min', 'category': 'hardware', 'description': 'Filter ssds by below a minimum capacity', 'ds_column': 'capacity', 'init': min}
    filters['capacity_max'] = {'type': 'slider_max', 'category': 'hardware', 'description': 'Filter ssds by above a maximum capacity', 'ds_column': 'capacity', 'init': max}

    for name, f in filters.items():
        value_set = sorted(list(set([value for value in sum([original_ds.data['{}_{}'.format(f['ds_column'], pk)] for pk in ssd_pks], [])])))
        if f['type'].startswith('slider'):
            step = 1 if is_list_of_integer(value_set) else 10**floor(log(min([value_set[i + 1] - value_set[i] for i in range(len(value_set)) if i + 1 < len(value_set)]), 10))
            f['object'] = Slider(
                title=name,
                start=min(value_set),
                end=max(value_set),
                value=f['init'](value_set),
                step=step
            )
        elif f['type'] == 'checkbox_group':
            f['object'] = CheckboxGroup(labels=value_set)
        elif f['type'] == 'checkbox_button_group':
            f['object'] = CheckboxButtonGroup(labels=value_set)
        elif f['type'] == 'select':
            f['object'] = Select(
                title=name,
                value=value_set[0],
                options=value_set
            )

    callback_base = """
var data_{test_id} = source_{test_id}.data;
var original_data_{test_id} = original_source_{test_id}.data;

for ( var j = 0; j < original_data_{test_id}['pks'].length; j++ ) {{
    var pk = original_data_{test_id}['pks'][j];
    data_{test_id}['{x}_' + pk] = [];
    data_{test_id}['{y}_' + pk] = [];
    for ( var i=0; i<original_data_{test_id}[Object.keys(original_data_{test_id})[0]].length; i++ ) {{
        if (
            {filter_condition}
        ) {{
            data_{test_id}['{x}_' + pk].push(original_data_{test_id}['{x}_' + pk][i]);
            data_{test_id}['{y}_' + pk].push(original_data_{test_id}['{y}_' + pk][i]);
        }}
    }}
}}

source_{test_id}.trigger('change');
"""
    callback_code_chunks = []
    callback_code_chunks.append(init_filter_values(filters))
    for test in tests:
        callback_code_chunks.append(callback_base.format(
            filter_condition=init_filter_condition(filters, "pk", test['test_id']),
            test_id=test['test_id'], x=test['x'], y=test['y']
        ))
    callback_code = "\n".join(callback_code_chunks)

    # now define the callback objects now that the filter widgets exist
    callback_source_args = {}
    for test in tests:
        callback_source_args['original_source_{test_id}'.format(test_id=test['test_id'])] = test['original_datasource']
        callback_source_args['source_{test_id}'.format(test_id=test['test_id'])] = test['datasource']
    callback_filter_args = {k: v['object'] for k, v in filters.items()}
    callback_args = dict(callback_filter_args, **callback_source_args)

    generic_callback = CustomJS(
        args=callback_args,
        code=callback_code
    )

    for name, f in filters.items():
        f['object'].callback = generic_callback

    # Build component
    plots_layout = column(
        [plot['figure'] for plot in tests],
        sizing_mode='scale_width'
    )
    widgets_list = []
    for name, f in filters.items():
        widgets_list.append(Div(text="<h3>{}</h3>".format(name)))
        widgets_list.append(f['object'])
    widgets = column([w for w in widgets_list], sizing_mode='scale_width')

    script, elements_to_render = components(
        [widgets, plots_layout],
        wrap_plot_info=False
    )
    context = {
        'bokeh_script': script,
        'bokeh_widgets': [elements_to_render[0]],
        'bokeh_plots': elements_to_render[1:],
    }

    return render(request, 'benchmarks/bokeh_base.html', context)
