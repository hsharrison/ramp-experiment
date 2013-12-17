#!/usr/bin/env python3
import matplotlib.pyplot as plt
from ramp import RampExperiment

data = RampExperiment.load_experiment('exp1.dat').data
angle_map = {1: 12,
             2: 17,
             3: 22,
             4: 27,
             5: 33,
             6: 39,
             7: 45}
data['angle'] = [angle_map[angle] for angle in data['angle']]

means = data.groupby(['angle', 'perception']).mean()
means['can step'] *= 100
means = means.reset_index()

can_step = means.pivot(index='angle', columns='perception', values='can step')
confidence = means.pivot(index='angle', columns='perception', values='confidence')

p = can_step.plot()
plt.xlabel('Angle of inclination (deg)')
plt.ylabel('Percent "Yes"')
p.get_figure().savefig('can_step.png')

p = confidence.plot()
plt.xlabel('Angle of inclination (deg)')
plt.ylabel('Percent "Yes"')
p.get_figure().savefig('confidence.png')