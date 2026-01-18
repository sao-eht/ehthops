import marimo

__generated_with = "0.19.4"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Baseline delays and rates

    __Changelog:__ [L. Blackburn, Sep 2018; rewritten for Python 3.9 Dec 2022; as marimo notebook with Python 3.10 Jan 2026]

    The purpose of this test is to check continuity of delay and rate solutions. Fringe delay and rate should be relatively smooth from scan to scan, and outliers indicate some issue with the fringe solution.
    """)
    return


@app.cell
def _(hops, os, util):
    # define and load data
    alistf = "alist.v6"
    datadir = os.environ['DATADIR']

    a = util.noauto(hops.read_alist(os.path.join(datadir, alistf)))

    # Pre-process alist dataframe
    util.fix(a)
    util.unwrap_mbd(a)
    util.add_days(a)
    util.add_delayerr(a)
    util.add_path(a)
    util.add_scanno(a)
    return (a,)


@app.cell
def _(a):
    # data filters -- remove SMAR-SMAW baselines (only applicable to EHT2017 data)
    thres = 7.0
    a_filtered = a[(a.snr > thres) & ~a.baseline.isin({'RS', 'SR'})].copy()
    return (a_filtered,)


@app.cell
def _(a_filtered):
    # Compute the boundaries between expt_nos
    sorted_a = a_filtered.sort_values(['expt_no', 'scan_no'])
    last_scans = sorted_a.groupby('expt_no')['scan_no'].max()  # Find the 'max' scan_no for each expt_no
    elines = (last_scans.iloc[:-1] + 0.5).to_numpy()  # Drop the final expt_no and offset by 0.5
    return (elines,)


@app.cell
def _(a_filtered, elines, hu, plt, wide):
    sites = sorted(set(''.join(a_filtered.baseline)))
    for (i, site) in enumerate(sites):
        hu.trendplot(a_filtered, site, vlines=elines, col='mbd_unwrap')
        plt.title('measured delays [ns @ %.0f MHz]' % a_filtered.iloc[0].ref_freq)
        wide(12, 4)
        plt.show()
    return (sites,)


@app.cell
def _(a_filtered, elines, hu, plt, sites, wide):
    for (i2, site2) in enumerate(sites):
        hu.trendplot(a_filtered, site2, vlines=elines, col='delay_rate')
        plt.title('measured rate [ps/s @ %.0f MHz]' % a_filtered.iloc[0].ref_freq)
        wide(12, 4)
        plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Imports and Helper Code
    """)
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import pandas as pd
    from eat.io import hops, util
    from eat.hops import util as hu
    from eat.plots import util as pu
    import matplotlib.pyplot as plt
    import numpy as np
    import os
    import sys
    import seaborn as sns

    sns.reset_orig()
    return hops, hu, os, plt, util


@app.cell
def _(plt):
    def wide(w=8, h=3): plt.setp(plt.gcf(), figwidth=w, figheight=h); \
        plt.tight_layout()

    def tightx(): plt.autoscale(enable=True, axis='x', tight=True)

    def multline(xs, fun=plt.axvline):
        for x in xs: fun(x, alpha=0.25, ls='--', color='k')

    def toiter(x):
        return(x if hasattr(x, '__iter__') else [x,])
    return (wide,)


if __name__ == "__main__":
    app.run()
