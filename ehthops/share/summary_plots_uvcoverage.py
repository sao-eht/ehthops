import marimo

__generated_with = "0.19.4"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # UV coverage of sources

    __Changelog:__ [L. Blackburn, Sep 2018; rewritten for Python 3.9 Dec 2022; as marimo notebook with Python 3.10 Jan 2026]

    The purpose of this summary is to show UV coverage of detections and upper limits of all sources.
    """)
    return


@app.cell
def _(hops, os, util):
    # define and load data

    alistf = 'alist.v6'
    datadir = os.environ['DATADIR']

    a = util.noauto(hops.read_alist(os.path.join(datadir, alistf)))

    # Pre-process the alist dataframe
    util.unwrap_mbd(a)
    util.add_days(a)
    util.add_delayerr(a)
    util.add_path(a)
    util.add_scanno(a)
    return (a,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Since ALMA-APEX (A-X), SMA-JCMT (S-J), and SMAR-SMAW (R-S, only for 2017) are co-located, treat them as interchangeable.
    """)
    return


@app.cell
def _(a, util):
    # reduce baseline complexity
    a['baseline'] = a.baseline.str.translate(str.maketrans('XJR', 'ASS'))
    util.fix(a)
    return


@app.cell
def _(a, hu, plt):
    figures_uv = []
    for src in sorted(set(a.source)):
        hu.uvplot(a, src)
        fig = plt.gcf()
        figures_uv.append(fig)
        plt.close(fig)

    figures_uv
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
    from eat.io import hops, util
    from eat.hops import util as hu
    import matplotlib.pyplot as plt
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
    return


if __name__ == "__main__":
    app.run()
