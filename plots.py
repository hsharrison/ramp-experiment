#!/usr/bin/env python3
import pandas as pd
from ramp import RampExperiment
from ggplot import *

data = RampExperiment.load_experiment('exp1.dat').data
angle_map = {1: 12,
             2: 17,
             3: 22,
             4: 27,
             5: 33,
             6: 39,
             7: 45}
data['angle'] = [angle_map[angle] for angle in data['angle']]

percents = pd.DataFrame(data.groupby(['angle', 'perception']).mean()*100)

p = ggplot(aes(x='angle', y='can step', shape='perception'), data=percents.reset_index()) + \
    geom_point() + \
    stat_smooth() + \
    xlab('Angle of inclination (deg)') + \
    ylab('Percent "Yes"')

print(p)