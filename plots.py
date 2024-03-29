#!/usr/bin/env python3.3
import matplotlib.pyplot as plt
import numpy as np
from ramp import RampExperiment


def process_data(filename):
    data = RampExperiment.load_experiment(filename).data
    angle_map = {7: 12,
                 6: 17,
                 5: 22,
                 4: 27,
                 3: 33,
                 2: 39,
                 1: 45}
    data['angle'] = [angle_map[angle] for angle in data['angle']]

    #workaround for timedelta since pandas can't take the mean of a timedelta:
    # http://stackoverflow.com/questions/20625982/
    # split-apply-combine-on-pandas-timedelta-column
    data['rt'] = [rt.total_seconds() if rt else None for rt in data['rt']]

    # remove subject 4
    data = data.ix[1:3].append(data.ix[5:])

    # SEM function
    sem = lambda x: np.std(x, ddof=1) / np.sqrt(len(x))
    sem.__name__ = 'sem'

    # split-apply-combine
    summary = data.groupby(['angle', 'perception']).aggregate([np.mean, sem])
    summary['can step'] *= 100

    return summary


def determine_half_angles(df):
    # determine 50% angles
    boundary = {}
    for perception in ('haptic', 'visual'):
        percents = df['can step', 'mean'].swaplevel(
            'angle', 'perception').xs(perception)[:-1].copy()
        percents.sort()
        boundary[perception] = np.interp(50, percents, percents.index)
    print('Angles with 50% responding "yes":')
    print(boundary)
    return boundary


def make_plot(df):
    haptic = df.xs('haptic', level='perception')
    visual = df.xs('visual', level='perception')
    plt.errorbar(visual.index, visual['mean'],
                 yerr=visual['sem'], fmt='k-o', label='visual')
    plt.hold(True)
    plt.errorbar(haptic.index, haptic['mean'],
                 yerr=haptic['sem'], fmt='k:o', label='haptic')
    plt.xlabel('Angle (deg)')
    plt.legend(title='Perception')
    plt.hold(False)


def make_plots(filename):
    summary = process_data(filename)
    boundary = determine_half_angles(summary)

    make_plot(summary['can step'])
    plt.ylabel('Percent "yes"')
    plt.hold(True)
    plt.plot([boundary['visual'], boundary['visual']],
             [plt.ylim()[0], 50], 'k-')
    plt.plot([boundary['haptic'], boundary['haptic']],
             [plt.ylim()[0], 50], 'k:')
    plt.hold(False)
    plt.savefig('can_step.png')

    make_plot(summary['confidence'])
    plt.ylabel('Confidence report')
    plt.savefig('confidence.png')

    make_plot(summary['rt'])
    plt.ylabel('Reaction time (sec)')
    plt.savefig('rt.png')
