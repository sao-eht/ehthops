import marimo

__generated_with = "0.19.4"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # RR-LL delay tests

    __Changelog:__ [L. Blackburn, Sep 2018; rewritten for Python 3.9 Dec 2022; as marimo notebook with Python 3.10 Jan 2026]

    The purpose of this test is to check stability of RR-LL delay alignment for baselines in the array. We expect R-L delay to be stable at each antenna, thus baseline RR-LL delay should also be stable. RR-LL is a cleaner signal than the RL or LR necessary for a direct measurement of R-L at a single site because it has less relative contamination from leakage. Also because ALMA XY feeds are aligned, ALMA is able to be used as a reference by assuming R-L delay at ALMA is exactly zero.
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Apply data filters and modify the polarization column to handle mixed polarization data. In mixedpol basis, all four correlations can be used in computing RR-LL difference since all four Stokes components are present in each correlation product. To enable this, we relabel XL and YL to LL and XR and YR to RR.
    """)
    return


@app.cell
def _(a):
    # data filters -- remove SMAR-SMAW baselines (only applicable to EHT2017 data)
    thres = 7.0
    a_snrcut = a[(a.snr > thres) & ~a.baseline.isin({'RS', 'SR'})].copy()
    # Relabel polarizations if mixedpol visibilities are present
    a_snrcut['polarization'] = a_snrcut.polarization.replace({'XL': 'LL', 'YL': 'LL', 'XR': 'RR', 'YR': 'RR'})
    return (a_snrcut,)


@app.cell
def _(a_snrcut):
    # Compute the boundaries between expt_nos
    sorted_a = a_snrcut.sort_values(['expt_no', 'scan_no'])
    last_scans = sorted_a.groupby('expt_no')['scan_no'].max()  # Find the 'max' scan_no for each expt_no
    elines = (last_scans.iloc[:-1] + 0.5).to_numpy()  # Drop the final expt_no and offset by 0.5
    return (elines,)


@app.cell
def _(a_snrcut, hu):
    # calculate the segmented statistics
    (p, stats) = hu.rrll_segmented(a_snrcut, restarts=hu.restarts)
    wa = sorted([bl for bl in set(p.index.get_level_values('baseline')) if bl[0] == 'A'])
    # filter out ALMA and non-ALMA baselines
    na = sorted([bl for bl in set(p.index.get_level_values('baseline')) if bl[0] != 'A'])
    return na, p, stats, wa


@app.cell
def _(stats, wa):
    print(stats.loc[(slice(None),slice(None),wa),:])
    return


@app.cell
def _(elines, hu, na, p, plt, wa, wide):
    # Make rrll plots for ALMA and non-ALMA baselines in different subplots
    fig = plt.figure()

    plt.subplot(3, 1, 1)
    hu.rrllplot(p, baselines=wa, vlines=elines)
    plt.xlim(0, 1.05*plt.xlim()[1])
    plt.title('RR-LL delay after subtracting mean value [%.0f MHz]' % (p.iloc[0].ref_freq))

    plt.subplot(3, 1, 2)
    hu.rrllplot(p, baselines=na[:len(na)//2], vlines=elines)
    plt.xlim(0, 1.05*plt.xlim()[1])

    plt.subplot(3, 1, 3)
    hu.rrllplot(p, baselines=na[len(na)//2:], vlines=elines)
    plt.xlim(0, 1.05*plt.xlim()[1])
    wide(12, 10)

    fig
    return


@app.cell
def _(p):
    # table of outliers
    outliers = (p.LLRR_offset.abs() > 0.000050) & (p.LLRR_std.abs() > 5)
    print(p.loc[outliers, "expt_no scan_id source timetag mbd_unwrap LLRR_offset LLRR_std".split()])
    return


@app.cell
def _(p, plt, wide):
    # scatter plot shows balancing between systematic error and bandwidth inflation factor
    # we want to see relatively well-behaved distribution across multiple SNR
    fig2 = plt.figure()

    plt.semilogx(p['LLRR_err'].values, p['LLRR_std'].values, '.')
    plt.ylim(-5, 5)
    plt.xlabel('predicted LL-RR error')
    plt.ylabel('sigmas away from mean')

    plt.gca().yaxis.grid(ls='--', alpha=0.5)
    wide(10, 5)

    fig2
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Plot histograms of deviation from mean for ALMA and non-ALMA baselines separately.
    """)
    return


@app.cell
def _(na, norm, np, p, plt, pu, wa, wide):
    # histogram of sigmas deviation
    lim = 8 # np.ceil(np.max(np.abs(p.LLRR_std)))
    xx = np.linspace(-lim, lim, 200)
    bins = np.linspace(-lim, lim, 161)

    for baselines in [wa, na]:
        q = p.loc[(slice(None),slice(None),baselines),:]
        (names, vals) = zip(*[(bl, rows.LLRR_std) for (bl, rows) in q.groupby('baseline')])
        names2 = list(name + ': %.1f' % np.sqrt(np.mean(val**2)) for (name, val) in zip(names, vals))
        plt.hist(vals, bins=bins, histtype='barstacked', alpha=1.0, label=names2, density=True)

        # Plot the normal distribution for comparison
        plt.plot(xx, norm.pdf(xx, loc=0, scale=1.0), 'k--', alpha=0.5)

        plt.xlabel('std away from mean')
        plt.ylabel('distribution of scans')
        plt.title('RR-LL delay offsets after subtracting mean value [%.0f MHz]' % (p.iloc[0].ref_freq))
        plt.legend(loc='upper right')
        plt.grid(alpha=0.25)

        std = np.mean(q.LLRR_std**2)
        pu.tag('N = %d, std=%.1f' % (len(q), std), loc='upper left')
        plt.xlim(-lim, lim) # only show bulk distribution

        wide(12, 4.5)
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
    from scipy.stats import norm
    import os
    import sys
    import seaborn as sns

    sns.reset_orig()
    return hops, hu, norm, np, os, plt, pu, util


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
