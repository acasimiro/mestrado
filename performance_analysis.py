from __future__ import division

import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

plt.style.use('ggplot')

OUTPUT_FOLDER = 'output/'


def run_performance_analysis(filepath, mapping, alpha, beta, gamma, delta):
    if [v for v in (alpha, beta, gamma, delta) if (v < 0) or (v > 1)]:
        raise RuntimeError('Parameter outside range [0,1]')
    if alpha + beta + gamma != 1.0:
        raise RuntimeError('alpha + beta + gamma != 1.0')

    strategies_mapping = {k:v[0] for k, v in mapping.items()}
    ctr_performance, ecpm_performance = performance_data(filepath, strategies_mapping)

    colors_mapping = dict(mapping.values())
    performance_chart(ctr_performance, colors_mapping, 'CTR')
    performance_chart(ecpm_performance, colors_mapping, 'ECPM')

    fobj_chart(ctr_performance, ecpm_performance, colors_mapping, alpha, beta, gamma, delta)


def performance_data(filepath, strategies_mapping):
    df = pd.read_csv(filepath)

    df = df[df.STRATEGY.isin(strategies_mapping)]
    df.STRATEGY = df.STRATEGY.apply(strategies_mapping.get)

    make_date = lambda r: dt.date(r['NUM_YEAR'], r['NUM_MONTH'], r['NUM_DAY'])
    df['DATE'] = df.apply(make_date, axis=1)
    df['CTR'] = df['CLICKS']/df['IMPRESSIONS']
    df['ECPM'] = df['REVENUE']/df['IMPRESSIONS']
    df = df[['STRATEGY', 'DATE', 'CTR', 'ECPM']]
    df.set_index(['DATE'], inplace=True)

    grouped = df.groupby(['STRATEGY'])

    baseline_ctr = grouped.get_group('stRND').CTR
    baseline_ecpm = grouped.get_group('stRND').ECPM

    ctr_performance = {}
    ecpm_performance = {}
    for strategy, group in grouped:
        if strategy == 'stRND':  continue
        ctr_performance[strategy] = (group['CTR'] - baseline_ctr) / (baseline_ctr)
        ecpm_performance[strategy] = (group['ECPM'] - baseline_ecpm) / (baseline_ecpm)

    return ctr_performance, ecpm_performance


def performance_chart(performance, colors, label):
    num_days = len(performance.values()[0])
    x_labels = ['Dia ' + str(i) for i in range(1, num_days + 1)]
    x_index = np.arange(len(x_labels))

    num_strategies = len(performance)
    bar_width = 1/(num_strategies + 2)

    fig = plt.figure(figsize=(12, 4))
    ax  = fig.add_subplot(111)
    for i, (st, series) in enumerate(performance.items(), 1):
        ax.bar(x_index + i*bar_width, series, bar_width, color=colors[st], label=st)
    # plt.title('Desempenho das estrategias por ' + label, fontsize=14)
    plt.ylabel(label)
    plt.xticks(x_index + 0.5, x_labels)
    ax.set_position([0.1, 0, 0.5, 0.8])
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.25), ncol=len(x_labels))
    plt.tight_layout()
    fig.savefig(OUTPUT_FOLDER + label + '_performance.pdf')
    plt.show()


def fobj_chart(ctrs, ecpms, colors, alpha, beta, gamma, delta):
    strategies = ctrs.keys()
    
    num_days = len(ctrs.values()[0])
    x_labels = ['Dia ' + str(i) for i in range(1, num_days + 1)]
    x_index = np.arange(len(x_labels))
    
    fig = plt.figure(figsize=(12, 4))
    ax = fig.add_subplot(111)
    for st in ctrs:
        C = ctrs[st]
        E = ecpms[st]
        mu = (C + E)/2
        sigma2 = ((C-mu)**2 + (E-mu)**2)/2
        fobjs = (alpha + beta)*C + gamma*E - delta*sigma2
        ax.plot(x_index, fobjs, color=colors[st], label=st, marker='.')
    #plt.title('Funcao objetivo das estrategias', fontsize=14)
    plt.ylabel('Fobj')
    plt.xticks(x_index, x_labels)
    ax.set_position([0.1, 0, 0.5, 0.8])
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.25), ncol=len(x_labels))
    ax.set_xlim([x_index[0]-0.1, x_index[-1]+0.1])
    plt.tight_layout()
    fig.savefig(OUTPUT_FOLDER + 'Fobj.pdf')
    plt.show()
