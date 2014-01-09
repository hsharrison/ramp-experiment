#!/usr/bin/env python3
import statsmodels.api as sm
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

# remove subject 4
data = data.ix[1:3].append(data.ix[5:])

# use int for response
data['response'] = data['can step'].astype(int)

# anovas
lm = sm.formula.ols('response ~ perception * C(angle)', data).fit()
anova_table = sm.stats.anova_lm(lm, typ=2)

print('\n\nResponses\n------')
print(anova_table)

lm = sm.formula.ols('confidence ~ perception * C(angle)', data).fit()
anova_table = sm.stats.anova_lm(lm, typ=2)
print('\n\nConfidence\n------')
print(anova_table)

lm = sm.formula.ols('rt ~ perception * C(angle)', data).fit()
anova_table = sm.stats.anova_lm(lm, typ=2)
print('\n\nResponse time\n------')
print(anova_table)