#!/usr/bin/env python3
import matplotlib.pyplot as plt
from ramp import RampExperiment

data = RampExperiment.load_experiment('exp1.dat').data
angle_map = {7: 12,
             6: 17,
             5: 22,
             4: 27,
             3: 33,
             2: 39,
             1: 45}
data['angle'] = [angle_map[angle] for angle in data['angle']]

#workaround for timedelta since pandas can't take the mean of a timedelta:
# http://stackoverflow.com/questions/20625982/split-apply-combine-on-pandas-timedelta-column
data['rt'] = [10**-9 * float(rt) for rt in data['rt']]

means = data.groupby(['angle', 'perception']).mean()
means['can step'] *= 100
means = means.reset_index()


def make_plot(values, ylabel, filename):
    p = means.pivot(index='angle', columns='perception', values=values).plot(style='-o')
    plt.xlabel('Angle of inclination (deg)')
    plt.ylabel(ylabel)
    p.get_figure().savefig(filename)


make_plot('can step', 'Percent "Yes"', 'can_step.png')
make_plot('confidence', 'Confidence Judgment', 'confidence.png')
make_plot('rt', 'Response Time (sec)', 'rt.png')

# Remove outliers
z = lambda x: (x - x.mean()) / x.std()
data['rt_z'] = data.groupby(['angle', 'perception'])['rt'].transform(z)
data['rt'][abs(data['rt_z']) > 3] = None

means = data.groupby(['angle', 'perception']).mean().reset_index()

make_plot('rt', 'Response Time (sec)', 'rt_rm_outliers.png')

# Remove subject4
means = data.ix[1:3].append(data.ix[5:10]).groupby(['angle', 'perception']).mean()
means['can step'] *= 100
means = means.reset_index()

make_plot('can step', 'Percent "Yes"', 'can_step_rm4.png')
make_plot('confidence', 'Confidence Judgment', 'confidence_rm4.png')
make_plot('rt', 'Response Time (sec)', 'rt_rm4.png')