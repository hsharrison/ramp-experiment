#!/usr/bin/env python3.3
import numpy as np
import rpy2.robjects as r
import pandas.rpy.common as com

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
data['rt'] = [rt.total_seconds() if rt else None for rt in data['rt']]

# remove subject 4
data = data.ix[1:3].append(data.ix[5:])

# use int for response
data['response'] = data['can step'].astype(int)

# Means by subject
means = data.reset_index().groupby(['participant', 'perception', 'angle']).mean()

# arcsine transformation
means['response'] = np.arcsin(np.sqrt(means['response']))

# Mixed ANOVA must be done in R
r.globalenv['means'] = com.convert_to_r_dataframe(means.reset_index(), strings_as_factors=True)
r.r('''
means$angle <- factor(means$angle)
means$participant <- factor(means$participant)
''')

for variable in ['response', 'rt', 'confidence']:
    print('\n\n{}\n-------'.format(variable))
    print(r.r('summary(aov({} ~ angle*perception + Error(participant), data=means))'.format(variable)))

# Get the actual mean boundary
data['max_angle'] = data['max_angle'].astype(int)
data['max_angle'] = [angle_map[max_angle] for max_angle in data['max_angle']]
mean_boundary = data.reset_index().groupby('participant').mean()['max_angle'].mean()
print('\n\nMean boundary: {}'.format(mean_boundary))