import marimo

__generated_with = "0.19.4"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Closure phases

    __Changelog:__ [L. Blackburn, Sep 2018; rewritten for Python 3.9 Dec 2022; as marimo notebook with Python 3.10 Jan 2026]

    The purpose of this test is to check trivial and non-trivial closure phases for sanity.

    Load the alist file (for computing global scan numbers) and the scan-averaged closure files for LL and RR polarizations for plotting closure quantities.
    """)
    return


@app.cell
def _(hops, hu, os, pd, util):
    # Define variables and load data
    alistf = 'alist.v6'
    alistfll = 'alist.v6.8s.LL.close.avg'
    alistfrr = 'alist.v6.8s.RR.close.avg'
    datadir = os.environ['DATADIR']

    a = hops.read_alist(os.path.join(datadir, alistf)) # alist file to make scan_no

    ll = hops.read_tlist_v6(os.path.join(datadir, alistfll))
    ll['polarization'] = 'LL'

    rr = hops.read_tlist_v6(os.path.join(datadir, alistfrr))
    rr['polarization'] = 'RR'

    # Concat the two dataframes and pre-process them
    df_close = pd.concat((ll, rr), ignore_index=True)
    util.add_gmst(df_close)
    hu.setparity(df_close)
    util.fix(df_close)
    return a, df_close


@app.cell
def _(a, df_close, util):
    # Add scan_no to the concatenated dataframe for grouping and plotting
    util.add_scanno(a)
    tup2scanno = a.groupby(['expt_no', 'scan_id']).first().scan_no
    df_close_scanno = df_close.join(tup2scanno, on=['expt_no', 'scan_id'], how='left')
    return (df_close_scanno,)


@app.cell
def _(a):
    # Compute the boundaries between expt_nos
    sorted_a = a.sort_values(['expt_no', 'scan_no'])
    last_scans = sorted_a.groupby('expt_no')['scan_no'].max() # Find the 'max' scan_no for each expt_no
    elines = (last_scans.iloc[:-1] + 0.5).to_numpy() # Drop the final expt_no and offset by 0.5
    return (elines,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Plot trivial closure phases

    Generate plots of closure phase (bispectrum phase) vs scan number for all triangles containing the "zero-baselines" ALMA-APEX and SMA-JCMT.
    """)
    return


@app.cell
def _(clplot, df_close_scanno):
    # Plot closure phases for triangles with A and X
    fig = clplot(df_close_scanno, sorted((t for t in set(df_close_scanno.triangle) if 'A' in t and 'X' in t and 'R' not in t)))
    fig
    return


@app.cell
def _(clplot, df_close_scanno):
    # Plot closure phases for triangles with S and J
    fig2 = clplot(df_close_scanno, sorted((t for t in set(df_close_scanno.triangle) if 'S' in t and 'J' in t and 'R' not in t)))
    fig2
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Plot other closure phases by source and track (expt_no)

    Plot closure phases against time for all non-degenerate triangles by source.
    """)
    return


@app.cell
def _(clplot2, df_close_scanno, sns):
    triangles = sorted((t for t in set(df_close_scanno.triangle) if 'R' not in t))
    triangles = [t for t in triangles if not ('X' in t or 'J' in t)]

    sns.set_palette(sns.color_palette(sns.hls_palette(len(triangles), l=0.6, s=0.6)))

    figures = [fig3 for src in sorted(set(df_close_scanno.source)) 
               if (fig3 := clplot2(df_close_scanno, source=src, triangles=triangles)) is not None]
    figures
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Plot closure phases against time for all non-degenerate triangles by source, further subdivided by track (expt no).
    """)
    return


@app.cell
def _(clplot2, df_close_scanno):
    triangles2 = sorted((t for t in set(df_close_scanno.triangle) if 'R' not in t))
    triangles2 = [t for t in triangles2 if not ('X' in t or 'J' in t)]
    sources = ['SGRA', 'M87', '3C279', 'OJ287']

    figures2 = []
    for src2 in sorted(set(sources)):
        for expt_no in sorted(set(df_close_scanno.expt_no)):
            fig4 = clplot2(df_close_scanno[df_close_scanno.expt_no == expt_no], source=src2, triangles=triangles2)
            if fig4 is None:
                continue
            fig4.axes[0].set_title(str(expt_no) + ' - ' + src2 + ' closure phases')
            figures2.append(fig4)

    figures2
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
    import os
    import sys
    import numpy as np
    import seaborn as sns

    sns.reset_orig()
    return hops, hu, np, os, pd, plt, pu, sns, util


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
    Define helper functions for plotting closure phases.
    """)
    return


@app.cell
def _(elines, np, plt, pu, wide):
    def clplot(df_close, triangles, threshold=3):
        wide(12, 5)
        df = df_close[(df_close.bis_snr > threshold) & ~df_close.triangle.str.contains('R') & (df_close.duration > 8 * 5)]
        for tri in triangles:
            rr = df[(df.polarization == 'RR') & (df.triangle == tri)]
            ll = df[(df.polarization == 'LL') & (df.triangle == tri)]
            hl = plt.errorbar(ll.scan_no - 0.025, ll.bis_phas, yerr=1.0 / ll.bis_snr * 180.0 / np.pi, fmt='o', label=tri)
            _ = plt.errorbar(rr.scan_no + 0.025, rr.bis_phas, yerr=1.0 / rr.bis_snr * 180.0 / np.pi, fmt='x', label='_nolegend_', color=hl[0].get_color())
        plt.gca().yaxis.grid(alpha=0.25)
        plt.legend(ncol=3)
        plt.title('closure phases')
        plt.xlabel('scan number')
        plt.ylabel('degrees')
        pu.multline(elines)
        return plt.gcf()
    return (clplot,)


@app.cell
def _(np, plt):
    def clplot2(df_close, source, triangles, threshold=3):
        fig = plt.figure(figsize=(12, 5))
        df = df_close[(df_close.bis_snr > threshold) & ~df_close.triangle.str.contains('R') & (df_close.duration > 8 * 5) & (df_close.source == source) & df_close.triangle.isin(set(triangles))].copy()
        t = np.hstack((df.gmst.sort_values().values, df.gmst.sort_values().values + 24.0))
        if len(t) == 0:
            plt.close(fig)
            return None # No figure returned # Adjust GMST to be continuous across the entire observing track
        idx = np.argmax(np.diff(t))
        toff = np.fmod(48.0 - 0.5 * (t[idx] + t[1 + idx]), 24.0)
        df.gmst = np.fmod(df.gmst + toff, 24.0) - toff
        for tri in triangles:
            rr = df[(df.polarization == 'RR') & (df.triangle == tri)]
            ll = df[(df.polarization == 'LL') & (df.triangle == tri)]
            if len(ll) > 0:
                (llabel, rlabel) = (tri, '_nolegend_')
            elif len(rr) > 0:
                (llabel, rlabel) = ('_nolegend_', tri)
            else:
                (llabel, rlabel) = ('_nolegend_', '_nolegend_')
            hl = plt.errorbar(ll.gmst - 0.01, ll.bis_phas, yerr=1.0 / ll.bis_snr * 180.0 / np.pi, fmt='o', label=llabel)
            _ = plt.errorbar(rr.gmst + 0.01, rr.bis_phas, yerr=1.0 / rr.bis_snr * 180.0 / np.pi, fmt='x', label=rlabel, color=hl[0].get_color())
        plt.gca().yaxis.grid(alpha=0.25)
        plt.legend(ncol=3)
        plt.title(source + ' closure phases')
        plt.xlabel('GMST hour')
        plt.ylabel('degrees')
        plt.ylim(-180, 180)
        return fig
    return (clplot2,)


if __name__ == "__main__":
    app.run()
