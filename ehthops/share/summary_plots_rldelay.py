import marimo

__generated_with = "0.19.4"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # R-L delay tests

    __Changelog:__ [L. Blackburn, Sep 2018; rewritten for Python 3.9 Dec 2022; as marimo notebook with Python 3.10 Jan 2026]

    The purpose of this test is to check stability of R-L delay alignment in one antenna using a reference signal (either polarization) from another antenna. Outliers in R-L delay indicate a mis-fringe in the parallel and/or cross hand polarization product of the baselines being tested. The test is sensitive to delayed leakage in either antenna which can cause a spurious cross-hand fringe. It can also show misidentified singleband delay, e.g. from being outside the search window.
    """)
    return


@app.cell
def _(hops, os, util):
    # define and load data
    alistf = 'alist.v6'
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
    a_snrcut = a[(a.snr > thres) & ~a.baseline.isin({'RS', 'SR'})].copy()
    return (a_snrcut,)


@app.cell
def _(a_snrcut):
    # Compute the boundaries between expt_nos
    sorted_a = a_snrcut.sort_values(['expt_no', 'scan_no'])
    last_scans = sorted_a.groupby('expt_no')['scan_no'].max()  # Find the 'max' scan_no for each expt_no
    elines = (last_scans.iloc[:-1] + 0.5).to_numpy()  # Drop the final expt_no and offset by 0.5
    return (elines,)


@app.cell
def _(a_snrcut, elines, hu, multline, np, plt, wide):
    # Get sorted list of unique sites from the baseline column
    sites = sorted(set().union(*set(a_snrcut.baseline)))
    lroffset_thres = 0.0002
    # Define cutoffs
    lrstd_thres = 5.0
    for site in sites:
        try:
            (p, stats) = hu.rl_segmented(a_snrcut, site, restarts=hu.restarts)
            hu.rlplot(p, corrected=True)
            multline(elines)
            outliers = (np.abs(p.LR_offset) > lroffset_thres) & (np.abs(p.LR_std) > lrstd_thres) & ~(p.baseline.str.contains('L') & (np.abs(np.abs(p.LR_offset) - 0.00145) < lroffset_thres))
            if len(outliers) > 0:
                _ = plt.plot(p[outliers].scan_no, 1000.0 * p[outliers].LR_offset_wrap, 'ko', ms=8, mfc='none', mew=2, zorder=-100)
            _ = plt.title('R-L delay after subtracting mean value [%.0f MHz]' % p.iloc[0].ref_freq)
            _ = plt.xlim(0, 1.05 * plt.xlim()[1])
            wide(12, 5)
            plt.show()
            print(p.loc[outliers, 'expt_no scan_id source timetag baseline ref_pol mbd_unwrap LR_offset LR_offset_wrap'.split()])
        except Exception as e:
            print(f'Error processing site {site}: {e}\nMoving on to next site...')
            continue
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
    return hops, hu, np, os, plt, util


@app.cell
def _(plt):
    def wide(w=8, h=3): plt.setp(plt.gcf(), figwidth=w, figheight=h); \
        plt.tight_layout()

    def tightx(): plt.autoscale(enable=True, axis='x', tight=True)

    def multline(xs, fun=plt.axvline):
        for x in xs: fun(x, alpha=0.25, ls='--', color='k')

    def toiter(x):
        return(x if hasattr(x, '__iter__') else [x,])
    return multline, wide


if __name__ == "__main__":
    app.run()
