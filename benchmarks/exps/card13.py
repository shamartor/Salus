# -*- coding: future_fstrings -*-
"""
Check inference workloads. See card#241

LaneMgr: enabled
Scheduler: fair
Work conservation: True
Collected data: memory usage over time
"""
from __future__ import absolute_import, print_function, division, unicode_literals

import random
from absl import flags

from benchmarks.driver.runner import Executor
from benchmarks.driver.server.config import presets
from benchmarks.driver.utils import execute
from benchmarks.driver.workload import WTL
from benchmarks.exps import run_seq, maybe_forced_preset, Pause, run_tf, run_tfdist

from benchmarks.driver.utils.compatiblity import pathlib


FLAGS = flags.FLAGS


def case1():
    scfg = maybe_forced_preset(presets.MostEfficient)

    run_tfdist(FLAGS.save_dir/'case1',
               WTL.create("inception3eval", 50, 50, executor=Executor.TF),
               WTL.create("inception3eval", 50, 50, executor=Executor.TFDist)
               )

    run_seq(scfg.copy(output_dir=FLAGS.save_dir/'case1'),
            WTL.create("inception3eval", 50, 50))


def case2():
    """Measure TF inference memory usage"""
    wl = WTL.create("inception3eval", 50, 50, executor=Executor.TF)
    wl.env['TF_CPP_MIN_VLOG_LEVEL'] = '1'
    wl.env['TF_CPP_MIN_LOG_LEVEL'] = ''
    outdir = FLAGS.save_dir/'case2'/wl.canonical_name
    run_tf(outdir, wl)

    # filter and move file to a more convinent name
    for f in outdir.iterdir():
        with f.with_name('alloc.output').open('w') as file:
            grep = execute(['egrep', r"] (\+|-)", f.name], stdout=file, cwd=str(f.parent))
            grep.wait()
        f.unlink()
        break


def main(argv):
    command = argv[0] if argv else "test"

    {
        "case1": case1,
        "case2": case2,
    }[command]()