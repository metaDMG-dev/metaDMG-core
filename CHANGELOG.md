# Changelog

<!--next-version-placeholder-->

## v0.17.0 (2022-02-14)
### Feature
* Add damage-mode "local" or "global" as options ([`5e153bb`](https://github.com/metaDMG/metaDMG/commit/5e153bb8dddacb32ac4cccad5903950a315c0175))
* Add temporary folders for LCA ([`21201c7`](https://github.com/metaDMG/metaDMG/commit/21201c71c5ce45dba384cb0e2ef9abd99aaa69f1))

### Documentation
* Update docs to reflect update in metadamage ([`72b055f`](https://github.com/metaDMG/metaDMG/commit/72b055ffb2623bdc0cef9bc46dcd17f7657570c6))

## v0.16.1 (2022-02-02)
### Fix
* Remove error when parsing taxes with apostrophe in tax name ([`e0e0405`](https://github.com/metaDMG/metaDMG/commit/e0e0405b1c719d5a06c64565e70a4872ab680374))
* Also remove lca.gz files ([`a8dbf91`](https://github.com/metaDMG/metaDMG/commit/a8dbf914b0b46382a15c309d5057daf933bda68c))

## v0.16.0 (2022-02-02)
### Feature
* Update dependencies for M1 macs ([`5f80629`](https://github.com/metaDMG/metaDMG/commit/5f80629b85d5515fa38350bccc216af985b47b9e))

## v0.15.0 (2022-01-31)
### Feature
* Add the option to include the fit predictions in the output csv files ([`a12d585`](https://github.com/metaDMG/metaDMG/commit/a12d585e53c2a8f497258a8706a2bfebe70d3520))

### Fix
* Read .gz zipped files ([`639873b`](https://github.com/metaDMG/metaDMG/commit/639873b505c564374b005cf4dd6fcdb4dd7c1241))
* Update dependencies ([`33f46fb`](https://github.com/metaDMG/metaDMG/commit/33f46fb1819864c5f66e426f760c70fa8ff67016))

### Documentation
* Update docs ([`202d484`](https://github.com/metaDMG/metaDMG/commit/202d48402d7eae06e011a620a3b96765542dabf3))

## v0.14.0 (2022-01-05)
### Feature
* Update dependencies (including metaDMG-viz) ([`ed281e5`](https://github.com/metaDMG/metaDMG/commit/ed281e564fefd279f3678c9f7b710225155a02dd))

## v0.13.4 (2021-11-10)
### Fix
* Add --long-name as bool flag to CLI ([`b2b64cb`](https://github.com/metaDMG/metaDMG/commit/b2b64cb528ab871ac73e91412616208b07c2d47a))

## v0.13.3 (2021-11-08)
### Fix
* Fix error when not doing progressbar in parallel Bayesian fits ([`097785a`](https://github.com/metaDMG/metaDMG/commit/097785a53e253789e4cdf248deab7a9b34bff3d6))

## v0.13.2 (2021-11-04)
### Fix
* Make update ([`f249210`](https://github.com/metaDMG/metaDMG/commit/f2492105460f354080593cf3edb789f4e90761d6))
* Add try except for MismatchFileError ([`76cc35c`](https://github.com/metaDMG/metaDMG/commit/76cc35c8c216c96a20cce5123a0096139a8441b7))
* Add MismatchFileError for when  mismatch.txt has error ([`a8662b0`](https://github.com/metaDMG/metaDMG/commit/a8662b08f8b732b0dd7f56c63d7aa974dcbd5c92))

## v0.13.1 (2021-10-27)
### Fix
* Fix error with forced and multiprocessing ([`fc8e4e0`](https://github.com/metaDMG/metaDMG/commit/fc8e4e0b35ace21c4f5586acf588e802c79221a6))

### Documentation
* Improve changelog ([`a065411`](https://github.com/metaDMG/metaDMG/commit/a06541165ffa5cfa9216a34b7dae0ad7d3defdc1))
## v0.13 (2021-10-26)
* Limit number of cores to be maximum the number of configs ([`60e4d92`](https://github.com/metaDMG/metaDMG/commit/60e4d92305e7a8973b1d65ffb836b745cee6e5c2))
* Add forced option to compute ([`ef01915`](https://github.com/metaDMG/metaDMG/commit/ef01915b1c4aaf647d3891835771b5bb372ae786))
* Add sample and tax_id information to the fits ([`c308262`](https://github.com/metaDMG/metaDMG/commit/c3082623fcfde23eb7ec04194543824add20693f))
* Remove Tax IDs with k_sum_total == 0 ([`5ec3058`](https://github.com/metaDMG/metaDMG/commit/5ec305810b3e76dd57222e06dafb0647ae2ea968))
* Delete files on KeyboardInterupt (clean up) ([`89d962b`](https://github.com/metaDMG/metaDMG/commit/89d962b04fb902678546ebf15a7f922e40de5074))
* Add hidden lines in log file and handle return code better ([`1762667`](https://github.com/metaDMG/metaDMG/commit/17626671f58081150e0cdc8e8b76e50fadd2e9fe))
* Improve error logging and messages for metadamage-cpp ([`73068ed`](https://github.com/metaDMG/metaDMG/commit/73068ed2c667e9770d1f9b2ad25ffd5c11fed568))
* Add mapDamage conversion command ([`b808fcd`](https://github.com/metaDMG/metaDMG/commit/b808fcd465f2ee7811c3b47c9786e51861efa1eb))
* Remove .bin files ([`c16364d`](https://github.com/metaDMG/metaDMG/commit/c16364d1201a443dc58a9fcc624eda1fc9a91630))
* Fix error with bad fits and mask them invalid ([`dd58c6c`](https://github.com/metaDMG/metaDMG/commit/dd58c6c3975bfd233b8573a43ab14a52aec6d97d))
* Update dashboard and include online example of dashboard ([`39ef8bb`](https://github.com/metaDMG/metaDMG/commit/39ef8bb42a8b5b8816ba29761eb0f1f682311a63))
* Add small fix to deal with old mismatch files that uses the old notation (|z| instead of |x|) ([`4093b0f`](https://github.com/metaDMG/metaDMG/commit/4093b0fcfa4c40e77f08da91c726ad474b511d37))
* Improve frequentists fits for forward and reverse fits ([`735d25c`](https://github.com/metaDMG/metaDMG/commit/735d25c742a9e627c4fded2cd86ff861fefe04c6))
* Fix ImportError in NumPyro ([`8245c57`](https://github.com/metaDMG/metaDMG/commit/8245c57a11c87c97117c5178ee958f97d9ea8809))
* Add metaDMG version to logging ([`12d968a`](https://github.com/metaDMG/metaDMG/commit/12d968a20b95ce0c520525f9a1e3b8b803137552))
* Add interactive dashboard to readme ([`61f3116`](https://github.com/metaDMG/metaDMG/commit/61f311668a372cabc960a4deb8bbca74c31a516b))
* Add --forced to readme ([`12a2114`](https://github.com/metaDMG/metaDMG/commit/12a211485d78727024017ed080973748c82ce8b0))
* Include mismatch-to-mapDamage in readme ([`29cbcf9`](https://github.com/metaDMG/metaDMG/commit/29cbcf9046aa0735af0e405d65f9335637e58bc5))
* Update readme with how to update ([`753b360`](https://github.com/metaDMG/metaDMG/commit/753b360ce4332d9ddd086d5529dd7e15d2f3c93e))



## v0.12 (2021-09-30)
* Update Dashboard to include pdf-plots and progressbar, and update Dash and dbc ([`fbf727c`](https://github.com/metaDMG/metaDMG/commit/fbf727c86c930d1675a31e9de61969323c2d8ec4))
* Add better handling of fit errors ([`4facb88`](https://github.com/metaDMG/metaDMG/commit/4facb88f1c25974adf73c3a20a546dfe859af3d9))
* Add progress bars when running single files or with a single core ([`11c8cdb`](https://github.com/metaDMG/metaDMG/commit/11c8cdbb8f9b74462cf031107beed043d0bdca37))
* Improve error logging while fitting ([`cce13ab`](https://github.com/metaDMG/metaDMG/commit/cce13ab4c4debce61a333c7fa686d452a0a29465))
* Memory leak of bayesian modelling ([`d04f5a8`](https://github.com/metaDMG/metaDMG/commit/d04f5a8e9e3ed8db30910e33f5d74f65944ca926))
* Log errors to see where they occur and skip them for now. ([`40d0387`](https://github.com/metaDMG/metaDMG/commit/40d038772882c08369504f408e32837d20c64c31))
* Allow running for old config files without cores_pr_fit being set ([`9a07f83`](https://github.com/metaDMG/metaDMG/commit/9a07f838a545348b8b29ec64250a7f3f1a793bf8))
* Add "cores-pr-fit" as config parameter ([`0a26847`](https://github.com/metaDMG/metaDMG/commit/0a26847c9e333697f5bece26d3239824018719e1))


## v0.11 (2021-09-20)
* Use random ports for logging to decrease risk of reusing same port ([`200eecc`](https://github.com/metaDMG/metaDMG/commit/200eecca3f7c45cbaab1246fe7694734494fffd4))
* Allow for multiple loggers (multiple jobs) ([`0ee5ce0`](https://github.com/metaDMG/metaDMG/commit/0ee5ce05ef9ca3b496759e7433bb223037b6cb18))
* Make null model more similar to damage model ([`74d575e`](https://github.com/metaDMG/metaDMG/commit/74d575e23c2faf54c62dc06e2de9d515d67fbd60))
* Refactor dashboard to only take a results dir as input ([`26608bb`](https://github.com/metaDMG/metaDMG/commit/26608bb6b532e6af9ff96b5b4697cb88a1b52732))
* Better parsing of read mode vs contig mode ([`06e3039`](https://github.com/metaDMG/metaDMG/commit/06e3039423a6138a8bed54cd812734489485b63e))

## v0.10 (2021-09-16)
* Add Bayesian computation of rho_Ac ([`db61f5d`](https://github.com/metaDMG/metaDMG/commit/db61f5d0d9bc49a5d537457178445a0bc7a100cb))
* Add uncertainty estimates to Bayesian results ([`21e81c7`](https://github.com/metaDMG/metaDMG/commit/21e81c7198c464937597ee1fa89bc471bae12685))
* Improve error messages for Bayesian fits ([`4e7beba`](https://github.com/metaDMG/metaDMG/commit/4e7beba224e05eaa2faef04f47aac1aa9d754932))

## v0.9 (2021-09-13)
* Include fitting as part of main package ([`14c2b7c`](https://github.com/metaDMG/metaDMG/commit/14c2b7c850f3b0c6a4d0c8423d20741521349378))
* Remove MetaDMG-cpp from github ([`bc5bd05`](https://github.com/metaDMG/metaDMG/commit/bc5bd0519c27be5faadee2c05141928e9b9bcbc4))
