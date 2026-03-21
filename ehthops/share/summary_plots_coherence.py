import marimo

__generated_with = "0.19.4"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Coherence tests

    __Changelog:__ [L. Blackburn, Sep 2018; rewritten for Python 3.9 Dec 2022; as marimo notebook with Python 3.10 Jan 2026]

    The purpose of this test is to check the degree of phase coherence on different baslines by calculating the amplitude loss using different coherent integration timescales. Poor phase coherence can be a result of low signal-to-noise and poor atmosphere, or an issue with ad-hoc phase correction.
    """)
    return


@app.cell
def _(hops, os, util):
    # Define variables and load data
    alist0 = 'alist.v6.2s.avg'
    alist1 = 'alist.v6.30s.avg'
    datadir = os.environ['DATADIR']

    a0 = util.noauto(hops.read_alist(os.path.join(datadir, alist0)))
    a1 = util.noauto(hops.read_alist(os.path.join(datadir, alist1)))

    # Pre-process the alist files for easier manipulation
    util.fix(a0)
    util.add_days(a0)
    util.add_path(a0)
    util.add_scanno(a0)

    util.fix(a1)
    util.add_days(a1)
    util.add_path(a1)
    util.add_scanno(a1)
    return a0, a1


@app.cell
def _(a0, a1):
    # Compute the ratio between the amplitudes of the 30s and the 2s alist files
    idx_cols = 'expt_no source scan_id baseline polarization'.split()
    # Set MultiIndex columns and group by the same columns (except polarization) for averaging
    group_cols = 'expt_no source scan_id baseline'.split()
    a0_1 = a0[a0.polarization.isin({'RR', 'LL', 'YR', 'XL', 'RY', 'LX'})].set_index(idx_cols).groupby(group_cols).mean(numeric_only=True)
    a1_1 = a1[a1.polarization.isin({'RR', 'LL', 'YR', 'XL', 'RY', 'LX'})].set_index(idx_cols).groupby(group_cols).mean(numeric_only=True)
    # Filter the data to include only the correlation products in the principal diagonal and compute the mean.
    # With the convention 'L' before 'R' for circular polarizations, we account for both 'lin-circ' and 'circ-lin' correlation products.
    a0_1['snr1'] = a1_1.snr
    a0_1['amp1'] = a1_1.amp
    a0_1['coh'] = a0_1.amp1 / a0_1.amp
    # Add some columns to a0 from a1 for easier manipulation later
    # Compute the amplitude ratio
    a = a0_1.reset_index().dropna()
    return (a,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The 2s integration SNR is plotted against the amplitude ratio computed above between 30s and 2s (coherently) averaged data. If the adhoc phase correction step has worked as expected, the coherence losses should be minimized and the effect should be more pronounced as the SNR increases.

    The vertical dashed line marks a (reasonable) SNR threshold beyond which the coherence loss mitigation is clearly visible.
    """)
    return


@app.cell
def _(a, plt, wide):
    wide(8, 4.5)
    plt.loglog(a.snr, a.coh, '.', ms=1)
    plt.axvline(7, color='k', ls='--', lw=2, alpha=0.25)
    plt.axhline(1, color='k', ls='--', lw=2, alpha=0.25)
    plt.ylim(.2, 2)
    plt.xlim(1, None)
    plt.xlabel('2s SNR')
    plt.ylabel('30s relative amplitude')
    plt.title('30s/2s amplitude ratio')
    plt.gcf()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Coherence loss plots by station

    We now make a series of plots showing the coherence loss for all baselines to a given station.
    """)
    return


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
    return (elines,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Below, we plot the scan numbers (time) against the coherence loss between the 30s and 2s averaged data for all baselines to each station. The outliers, corresponding to the data points for which the coherence loss is below *outliers_coh* when the SNR is greater than *outliers_snr*, are highlighted.
    """)
    return


@app.cell
def _(a_snrcut, elines, multline, plt, tightx):
    # Get sorted list of unique sites from the baseline column
    sites = sorted(set().union(*set(a_snrcut.baseline)))
    snr_split = 50
    # Define cutoffs for SNR and outliers
    outliers_coh = 0.8
    outliers_snr = 20

    outputs = []
    for site in sites:
        fig = plt.figure(figsize=(12, 4))  # Create new figure for each site
    
        df_site = a_snrcut[a_snrcut.baseline.str.contains(site)]
        for (bl, rows) in df_site.groupby('baseline'):
            lo_mask = rows.snr < snr_split
            hi_mask = rows.snr >= snr_split
            bl = bl if bl[1] == site else bl[::-1]  # Reverse the baseline if the second character is not the site
            h = plt.errorbar(rows[hi_mask].scan_no, rows[hi_mask].coh, yerr=1.0 / rows[hi_mask].snr, fmt='.', label='_nolegend_' if hi_mask.sum() == 0 else bl, zorder=10)
            _ = plt.errorbar(rows[lo_mask].scan_no, rows[lo_mask].coh, yerr=1.0 / rows[lo_mask].snr, fmt='.', label=bl if hi_mask.sum() == 0 and lo_mask.sum() > 0 else '_nolegend_', color=h[0].get_color(), alpha=0.5)
        multline(elines)
        _ = plt.title('Coherence loss in 30 seconds [%.0f MHz]' % df_site.iloc[0].ref_freq)
        tightx()
        _ = plt.xlim(0, plt.xlim()[1] * 1.1)
        _ = plt.grid(axis='y', alpha=0.25)
        _ = plt.legend(loc='best')
        outliers = df_site[(df_site.coh < outliers_coh) & (df_site.snr > outliers_snr)]
        if len(outliers) > 0:
            _ = plt.plot(outliers.scan_no, outliers.coh, 'ko', ms=8, mfc='none', mew=2, zorder=-100)
    
        outputs.append(fig)
        plt.close(fig)
    
        # Add outliers table right after the figure
        if len(outliers) > 0:
            outputs.append(outliers[['expt_no', 'scan_id', 'source', 'baseline', 'snr', 'coh']])

    outputs
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
    import matplotlib.pyplot as plt
    import os
    import sys
    import seaborn as sns

    sns.reset_orig()
    return hops, os, plt, util


@app.cell
def _(plt):
    def wide(w=8, h=3): plt.setp(plt.gcf(), figwidth=w, figheight=h); \
        plt.tight_layout()

    def tightx(): plt.autoscale(enable=True, axis='x', tight=True)

    def multline(xs, fun=plt.axvline):
        for x in xs: fun(x, alpha=0.25, ls='--', color='k')

    def toiter(x):
        return(x if hasattr(x, '__iter__') else [x,])
    return multline, tightx, wide


if __name__ == "__main__":
    app.run()
