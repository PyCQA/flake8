# -*- coding: utf-8 -*-
# Adapted from a contribution of Johan Dahlin

import collections
try:
    import multiprocessing
except ImportError:     # Python 2.5
    multiprocessing = None

import pep8

__all__ = ['multiprocessing', 'BaseQReport', 'QueueReport']


class BaseQReport(pep8.BaseReport):
    """Base Queue Report."""

    def __init__(self, options):
        assert options.jobs > 0
        super(BaseQReport, self).__init__(options)
        self.counters = collections.defaultdict(int)
        self.n_jobs = options.jobs

        # init queues
        self.task_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()

    def start(self):
        super(BaseQReport, self).start()
        # spawn processes
        for i in range(self.n_jobs):
            p = multiprocessing.Process(target=self.process_main)
            p.start()

    def stop(self):
        # collect queues
        for i in range(self.n_jobs):
            self.task_queue.put('DONE')
            self.update_state(self.result_queue.get())
        super(BaseQReport, self).stop()

    def process_main(self):
        for filename in iter(self.task_queue.get, 'DONE'):
            self.input_file(filename)
        self.result_queue.put(self.get_state())

    def get_state(self):
        return {'total_errors': self.total_errors,
                'counters': self.counters,
                'messages': self.messages}

    def update_state(self, state):
        self.total_errors += state['total_errors']
        for key, value in state['counters'].items():
            self.counters[key] += value
        self.messages.update(state['messages'])


class QueueReport(pep8.StandardReport, BaseQReport):
    """Standard Queue Report."""
