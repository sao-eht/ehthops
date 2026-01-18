import marimo

__generated_with = "0.19.4"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Polarization fraction tests

    __Changelog:__ [L. Blackburn, Sep 2018; rewritten for Python 3.9 Dec 2022; as marimo notebook with Python 3.10 Jan 2026]

    The purpose of this test is to check stability of polarization fraction on various baselines. The test is sensitive to leakage and false fringes.
    """)
    return


@app.cell
def _(hops, os, util):
    # define and load data
    alistf = 'alist.v6'
    datadir = os.environ['DATADIR']

    a = util.noauto(hops.read_alist(os.path.join(datadir, alistf)))

    # Pre-process the alist dataframe
    util.fix(a)
    util.unwrap_mbd(a)
    util.add_days(a)
    util.add_delayerr(a)
    util.add_path(a)
    util.add_scanno(a)
    util.add_gmst(a)

    days = sorted(set(a.expt_no))
    return a, days


@app.cell
def _(a):
    # data filters
    snr_cutoff = 7  # reasonable SNR cutoff for filtering
    a_snrcut = a[(a.snr > snr_cutoff) & ~a.baseline.str.contains('R')]
    return (a_snrcut,)


@app.cell
def _(a_snrcut):
    # Compute the boundaries between expt_nos
    sorted_a = a_snrcut.sort_values(['expt_no', 'scan_no'])
    last_scans = sorted_a.groupby('expt_no')['scan_no'].max()  # Find the 'max' scan_no for each expt_no
    elines = (last_scans.iloc[:-1] + 0.5).to_numpy()  # Drop the final expt_no and offset by 0.5
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For all rows uniquely identified by *index_cols*, we compute the polarization fraction (and its error) using the corresponding SNR values for each polarization product. Entries in the alist file for which all four polarization products are not present are ignored.
    """)
    return


@app.cell
def _(a_snrcut, np):
    index_cols = 'expt_no scan_no gmst timetag baseline source u v'.split()
    p = a_snrcut.pivot_table(aggfunc='first', index=index_cols, columns=['polarization'], values=['snr']).dropna()
    p['fpol'] = np.sqrt(p.snr.LR * p.snr.RL / (p.snr.LL * p.snr.RR))
    p['fpol_err'] = np.sqrt(2.0 / (p.snr.LL * p.snr.RR))
    q = p.reset_index()
    return (q,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For each source, plot the polarization fractions against

    - GMST

    - uv-coverage
    """)
    return


@app.cell
def _(pftrend, pfuv, plt, q):
    for src in sorted(set(q.source)):
        pftrend(q, src)
        plt.show()

        pfuv(q, src, 'jet')
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
    import itertools
    import matplotlib.pyplot as plt
    import numpy as np
    import os
    import sys
    import seaborn as sns
    from matplotlib.legend import Legend

    sns.reset_orig()
    return Legend, hops, itertools, np, os, plt, util


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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define functions for plotting the polarization fraction for a given source against time (GMST) and uv-coverage.
    """)
    return


@app.cell
def _(Legend, days, itertools, np, plt, wide):
    def pftrend(b, src):
        df = b[b.source == src].copy()
        t = np.hstack((df.gmst.sort_values().values, df.gmst.sort_values().values + 24.0))
        idx = np.argmax(np.diff(t))  # Ensure that the GMST is in the range 0-24 hours
        toff = np.fmod(48.0 - 0.5 * (t[idx] + t[1 + idx]), 24.0)
        df['gmst'] = np.fmod(df.gmst + toff, 24.0) - toff
        if df.gmst.max() < 0:
            df.gmst = df.gmst + 24
        ax = None
        blc = dict(zip(sorted(set(df.baseline)), itertools.cycle(plt.rcParams['axes.prop_cycle'].by_key()['color'])))
        lnum = 1000000.0
        for (i, day) in enumerate(days):  # Assign unique colour to each baseline
            ax = plt.subplot(1, len(days), 1 + i, sharey=ax, sharex=ax)
            dayrows = df[df.expt_no == day]
            if len(dayrows) < lnum:
                (lax, lnum) = (ax, len(dayrows))
            if i > 0:
                _ = plt.setp(ax.get_yticklabels(), visible=False)
            for (bl, blrows) in dayrows.groupby('baseline'):
                h = plt.errorbar(blrows.gmst, blrows.fpol, blrows.fpol_err, fmt='.', color=blc[bl], label='_nolegend_')
                _ = plt.plot(blrows.gmst, blrows.fpol, '-', color=h[0].get_color(), alpha=0.25, label='_nolegend_')
            ax.grid(axis='y', alpha=0.25)
        lines = [plt.Line2D([0], [0], color=blc[bl], marker='.', ls='none') for bl in sorted(blc.keys())]  # Remember the axis with the fewest rows for placing the legend
        leg = Legend(lax, lines, sorted(blc.keys()), loc='best', ncol=2)
        _ = lax.add_artist(leg)
        wide(12, 4)
        plt.subplots_adjust(hspace=0, wspace=0)
        _ = plt.suptitle('%s fractional polarization vs GMST' % src, y=plt.gcf().subplotpars.top, va='bottom')  # plot data with errorbars  # plot a line through the data
    return (pftrend,)


@app.cell
def _(days, plt, wide):
    def pfuv(b, src, cmap='jet'):
        df = b[b.source == src].sort_values('fpol')

        ax = None
        lim = 1.1e-3 * max(df.u.abs().max(), df.v.abs().max())

        for(i, day) in enumerate(days):
            ax = plt.subplot(1, len(days), 1+i, sharey=ax, sharex=ax, aspect=1.0)

            dayrows = df[df.expt_no == day]

            if i > 0:
                _ = plt.setp(ax.get_yticklabels(), visible=False)

            _ = plt.scatter(1e-3 * dayrows.u, 1e-3 * dayrows.v, c=dayrows.fpol, cmap=cmap, vmin=0, vmax=1)
            _ = plt.scatter(-1e-3 * dayrows.u, -1e-3 * dayrows.v, c=dayrows.fpol, cmap=cmap, vmin=0, vmax=1)
            _ = plt.grid(which='both', ls='--', alpha=0.25)

        wide(12, 3)

        plt.xlim(-lim, lim)
        plt.ylim(-lim, lim)

        plt.subplots_adjust(hspace=0, wspace=0)
        _ = plt.suptitle('%s fractional polarization vs (u, v) [Gly]' %
                         src, y=plt.gcf().subplotpars.top, va='bottom')
    return (pfuv,)


if __name__ == "__main__":
    app.run()
