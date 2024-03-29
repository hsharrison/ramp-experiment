#!/usr/bin/env python3.3
"""
Slope perception experiment.

Usage:
  ramp.py new <experiment_file> [--participants=<p>] [--trials=<t>] [--debug]
  ramp.py run <experiment_file> [--demo] [--finished] [--debug] [(<level> <n>)]...
  ramp.py export <experiment_file> <data_file> [--debug]
  ramp.py -h | --help

Options:
  -h, --help          Show this screen.
  --participants=<p>  Number of participants [default: 10].
  --trials=<t>        Number of trials pre block per angle [default: 3].
  --demo              Don't save data.
  --finished          Run the next participant that hasn't finished, rather than the next that hasn't started.
  --debug             Print debug messages to console.

"""
from time import sleep
from datetime import datetime
from random import random

import logging
import pyglet
import experimentator as exp

can_step_responses = {pyglet.window.key.PAGEDOWN: True, pyglet.window.key.PAGEUP: False}
confidence_responses = {pyglet.window.key._1: 1,
                        pyglet.window.key._2: 2,
                        pyglet.window.key._3: 3,
                        pyglet.window.key._4: 4,
                        pyglet.window.key._5: 5,
                        pyglet.window.key._6: 6,
                        pyglet.window.key._7: 7}


class RampExperiment(exp.Experiment):
    def __init__(self, settings_by_level, **kwargs):

        self.font_size = 50
        self.text_x = 50
        self.text_y = 50
        self.window = None
        self.wait = None
        self.press = None
        self.press_time = None
        self.beep = None
        self.noise = None
        self.label = None

        self.init_sounds()

        super().__init__(settings_by_level, **kwargs)

    def init_sounds(self):
        self.beep = pyglet.media.Player()
        self.beep.eos_action = self.beep.EOS_LOOP
        self.beep.queue(pyglet.media.load('beep.mp3'))

        self.noise = pyglet.media.Player()
        self.noise.eos_action = self.noise.EOS_LOOP
        self.noise.queue(pyglet.media.load('noise.mp3'))

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['beep'], state['noise'], state['window'], state['press'], state['label']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        #self.init_sounds()
        new_entries = dict(window=None, press=None, label=None)
        self.__dict__.update(new_entries)

    def on_key_press(self, symbol, _):
        logging.debug('Key press: {}, wait: {}.'.format(symbol, self.wait))

        if symbol == pyglet.window.key.ESCAPE:
            pyglet.app.exit()
            raise exp.QuitSession('User quit')

        if self.wait == 'any' and symbol not in can_step_responses:
            self.wait = None
            pyglet.app.exit()

        elif self.wait == 'participant' and symbol in can_step_responses:
            self.press = symbol
            self.press_time = datetime.now()
            self.wait = None
            pyglet.app.exit()

        elif self.wait == 'confidence' and symbol in confidence_responses:
            self.press = symbol
            self.wait = None
            pyglet.app.exit()

    def on_draw(self):
        self.window.clear()
        self.label.draw()

    def play_beep(self, duration=0.5):
        self.beep.play()
        sleep(duration)
        self.beep.pause()

    def start(self, level, **kwargs):
        if level == 'block':
            self.window = pyglet.window.Window(fullscreen=True)
            self.window.push_handlers(self)
            self.label = pyglet.text.Label('Beginning {} perception block.'.format(kwargs['perception']),
                                           font_size=self.font_size,
                                           x=self.text_x,
                                           y=self.text_y)
            self.wait = 'any'
            pyglet.app.run()
            self.window.clear()

    def end(self, level, **kwargs):
        if level == 'block':
            self.window.close()

        elif level == 'participant':
            # Add participant information
            max_angle = input("Enter participant's max angle:  ")
            gender = input("Enter participant's gender:  ")
            age = input("Enter participant's age:  ")

            which_participant = kwargs['participant']

            self.find_section(participant=which_participant).add_data(max_angle=max_angle,
                                                                      gender=gender,
                                                                      age=age)

    def run_trial(self, **kwargs):
        self.press = None
        self.press_time = None

        # Set ramp angle
        self.noise.play()
        self.label = pyglet.text.Label('Set ramp to angle {} and press any key.'.format(kwargs['angle']),
                                       font_size=self.font_size,
                                       x=self.text_x,
                                       y=self.text_y)
        self.wait = 'any'
        pyglet.app.run()
        self.noise.pause()

        # Get participant response
        sleep(0.5 + 1.5*random())
        self.play_beep()
        start_time = datetime.now()
        self.wait = 'participant'
        self.label = pyglet.text.Label('Waiting for participant response...',
                                       font_size=self.font_size,
                                       x=self.text_x,
                                       y=self.text_y)
        pyglet.app.run()
        self.window.clear()
        can_step = can_step_responses.get(self.press, self.press)

        # Get confidence
        self.label = pyglet.text.Label('Enter confidence report.',
                                       font_size=self.font_size,
                                       x=self.text_x,
                                       y=self.text_y)
        self.wait = 'confidence'
        pyglet.app.run()
        self.window.clear()
        confidence = confidence_responses.get(self.press, self.press)

        return {'can step': can_step,
                'confidence': confidence,
                'rt': self.press_time - start_time}


if __name__ == '__main__':
    from docopt import docopt
    opts = docopt(__doc__)

    if opts['--debug']:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug('DEMO MODE = {}.'.format(opts['--demo']))

    if opts['new']:
        settings = {'participant': dict(n=int(opts['--participants'])),
                    'block': dict(sort='random', ivs={'perception': ['haptic', 'visual']}),
                    'trial': dict(n=int(opts['--trials']), sort='random', ivs={'angle': list(range(1, 8))})}
        levels = ('participant', 'block', 'trial')
        RampExperiment(settings, levels=levels, experiment_file=opts['<experiment_file>'])

    elif opts['run']:
        experiment_file = opts['<experiment_file>']
        by_started = not opts['--finished']

        section_dict = {level: int(n) for level, n in zip(opts['<level>'], opts['<n>'])}
        experiment = RampExperiment.load_experiment(experiment_file)

        if section_dict:
            # If section not specified, could be overwriting data
            experiment.save(experiment_file + datetime.now().strftime('.%m-%d-%H-%M-backup'))
            section = experiment.find_section(**section_dict)
        else:
            section = experiment.find_first_not_run('participant', by_started=by_started)

        exp.run_experiment_section(experiment, demo=opts['--demo'], section=section)
        experiment.save(experiment_file)

    elif opts['export']:
        exp.export_experiment_data(opts['<experiment_file>'], opts['<data_file>'])