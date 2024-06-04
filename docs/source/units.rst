==============================
Units in various HOPS products
==============================

By Lindy Blackburn

Amplitude
---------

    the alist amplitude is taken directly from type 208 fringe summ
    the alist amplitude is in correlation coefficient with corrections applied to try to bring it to ideal analog correlation coefficient. this includes van-vleck correction and a small correction due to coherence loss from gridding

Signal-to-noise ratio
---------------------

    the signal to noise ratio should reflect the actual signal-to-noise of the measured amplitude, including all possible losses

Weights
-------

    weights in HOPS may reflect either the fractional number of samples used to form an average (degrees-of-freedom tracking), or a forward multiplicative amplitude correction factor. These are related but do not always affect amplitude, sigma, or S/N in the same way.

Phase
-----

    phase in alist is in degrees

Frequency
---------

    ref_freq in alist is in MHz
    ref_freq in control file is in MHz

u, v
----

    u, v coordinates in alist file are in 1e6 * lambda

delay
-----

    sbdelay and mbdelay in control file are in [us]
    sbdelay and mbdelay in alist file are in [us]
    sbdelay and mbdelay in type 208 are in [us]
    pc_delay in control file is in [ns]
    delay_offs in control file is in [ns]

rate
----

    delay_rate in control file is in [ps/s]
    delay_rate in alist file is in [ps/s]
    delay_rate in type 208 is [us/s]

time
----

    timetag is in DOY-HHMMSS, and has a variety of meanings
    length in alist is the processed data length [s]
    duration in alist is the scan nominal duration [s]
    offset in alist is the mean time minus scan time [s]
    scan_offset in alist is the timetag minus scan time [s]
    timestamp in adhoc phase is in [days] since beginning of year (starts at zero), and is offset by 1 AP
    scan time in control file selector is DOY-HHMM and includes possible adjustments from scan_offset

sign convention in control file
-------------------------------

    positive delay_offs for REM station results in positive slope of baseline phase vs frequency (within band)
    positive pc_delay for REM station results in positive slope of baseline phase vs frequency (between bands)
    positive pc_phases for REM station results in positive baseline phase shift
    positive adhoc phases for REM station results in positive baseline phase shift
    "The delay on baseline AB is positive if the signal arrives at station B after station A (Rogers et al. 1974). The phase is positive as well, modulo 2π ambiguities." ((link)[https://eht-wiki.haystack.mit.edu/@api/deki/files/45/=sign-of-phases.pdf])

Type 212 data
-------------

    - Since fourfit type 212 data is what gets translated to the UVFITS output, it is important to understand what goes into them
    - UVFITS conversion process:
        - read in type 212 data directly
        - calculate SIGMA_mean as type208.amp / type208.snr in Whitneys (units of 10^-4)
        - convert to SIGMA_i = SIGMA_mean x sqrt(N)  (actually use true weights ~1)
        - use 1/SIGMA_i^2 as UVFITS WEIGHT (back to units of 1e0)
    - The assumption is that type212 data amplitudes represent ideal analog correlation coefficients in Whitneys, in which case it will be related to the total time-frequency integration and attempt to account for various losses like Van Vleck correction.
        - 1e4 / np.sqrt(116 Msps * 1.0 second) / 0.881 = 1.054

HOPS alist amplitude/SNR

    1. Stepping backward through fourfit:
    2. alist amplitude and SNR comes directly from type_208
    3. `fill_208.c`:
    
       .. code-block:: c
          
          struct type_status *status,
          t208->amplitude = status->delres_max/10000.
          t208->snr = status->snr;
    4. `fill_fringe_info.c`:

       .. code-block:: c
          
          extern struct type_status status;
          error += fill_208 (pass, &param, &status, &t202, &t208);
    5. `output.c`:

       .. code-block:: c
          
          fill_fringe_info (root, pass, fringe_name)
    6. The SNR is actually calculated in `make_plotdata`, from first principles, `delres_max` and `amp_corr_fact` (just to undo the fact that is was previously applied to `delres_max`)
    7. `make_plotdata.c`:

       .. code-block:: c
          
          extern struct type_status status;
          eff_npol = pass->npols > 2 ? 2 : pass->npols;
                                        /*  Signal to Noise Ratio */
          status.snr = status.delres_max * param.inv_sigma * sqrt((double)status.total_ap_frac * eff_npol) / (1.0E4 * status.amp_corr_fact);
    8. `search.c`:

       .. code-block:: c
          
          fftplan = fftw_plan_dft_1d (status.grid_points, data, data, FFTW_FORWARD, FFTW_MEASURE);
          mb_delay[i] = cabs (data[j]);
          amps[mbd_index][dr_index] = mb_delay[mbd_index] / status.total_ap_frac;
          max_amp[lag] = amps[mbd_index][dr_index];
          global_max = max_amp[lag]
          update (pass, max_mbd_cell, global_max, max_lag, max_dr_cell, GLOBAL);
    9. `update.c`:

       .. code-block:: c
          
          extern struct type_status status;
          update (struct type_pass* pass, int mbd_cell, double max_val, int lag, int drate_cell, int flag)
          status.delres_max = max_val;
    10. `norm_fx.c`:

        .. code-block:: c
          
           status.total_ap_frac   += datum->usbfrac;
    11. `amp_corr_fact` includes the correction for `fringe rate`, and folded into `delres_max`
    12. `interp.c`:

        .. code-block:: c
          
           struct freq_corel *frq;
           frq = pass->pass_data + fr; // frq is just a pointer to pass_data
           X = frq->data[ap].sbdelay[sbd] * vrot (ap, dr, mbd, fr, 0, pass);
           frac = frq->data[ap].usbfrac;
           X = X * frac;
           z = z + X;
           z = z * 1.0 / status.total_ap_frac;
           drf[isbd][imbd][idr] = cabs (z);
           max555 (drf, xlim, xi, &drfmax);
           // Amplitude correction due to non-zero delay rate
           theta = status.dr_max_global * param.ref_freq * param.acc_period * M_PI;
           status.amp_rate_corr = (fabs (theta) > 0.001)? theta / sin (theta) : 1.0;
           status.amp_corr_fact = status.amp_rate_corr;
           status.delres_max = drfmax * status.amp_corr_fact;

But what about the **type 212** data?

    1. `make_plotdata.c`:

       .. code-block:: c
          
          struct freq_corel *pdata;
          struct data_corel *datum;
          pdata = pass->pass_data;
          for (fr = 0; fr < pass->nfreq; fr++)
            for (ap = pass->ap_off; ap < pass->ap_off+pass->num_ap; ap++)
              datum = pdata[fr].data + ap;
              Z = datum->sbdelay[status.max_delchan] // presumably this is supersampled FFT of SB
          // norm_fx: (static complex xcor[4*MAXLAG], S[4*MAXLAG], xlag[4*MAXLAG];)
                * vrot(ap,status.dr_max_global,status.mbd_max_global,fr,datum->sband,pass); // then rotated by MBD and RATE
              plot.phasor[fr][ap] = Z;
          // generate data for sum over all channels (note this is not filled in type 212)
          for (ap = pass->ap_off; ap < pass->ap_off+pass->num_ap; ap++)
             {
             plot.phasor[pass->nfreq][ap] = sum_ap[ap];
             plot.weights[pass->nfreq][ap] = ap_cnt[ap];
             }
    2. `fill_fringe_info.c`:

       .. code-block:: c
          
          for (fr=0; fr<pass->nfreq; fr++)
            error += fill_212 (pass, &status, &param, fr, fringe.t212[fr]);
    3. `fill_212.c`:

       .. code-block:: c

          fill_212 (
          struct type_pass *pass,  // pass is only used for meta-data
          struct type_status *status,
          struct type_param *param,
          int fr,
          struct type_212 *t212)
          extern struct type_plot plot;
          t212->data[ap_212].amp = cabs (plot.phasor[fr][ap]) * status->amp_corr_fact;
          t212->data[ap_212].phase = carg (plot.phasor[fr][ap]);
          t212->data[ap_212].weight = plot.weights[fr][ap];