# Changelog

<!--next-version-placeholder-->

## v0.12.15 (2021-10-26)
### Fix
* Add forced option to compute ([`ef01915`](https://github.com/metaDMG/metaDMG/commit/ef01915b1c4aaf647d3891835771b5bb372ae786))

### Documentation
* Add --forced to readme ([`12a2114`](https://github.com/metaDMG/metaDMG/commit/12a211485d78727024017ed080973748c82ce8b0))

## v0.12.14 (2021-10-26)
### Fix
* Add sample and tax_id information to the fits ([`c308262`](https://github.com/metaDMG/metaDMG/commit/c3082623fcfde23eb7ec04194543824add20693f))
* Remove Tax IDs with k_sum_total == 0 ([`5ec3058`](https://github.com/metaDMG/metaDMG/commit/5ec305810b3e76dd57222e06dafb0647ae2ea968))

## v0.12.13 (2021-10-25)
### Fix
* Delete files on KeyboardInterupt (clean up) ([`89d962b`](https://github.com/metaDMG/metaDMG/commit/89d962b04fb902678546ebf15a7f922e40de5074))
* Remove commented out code ([`5ecbddb`](https://github.com/metaDMG/metaDMG/commit/5ecbddbf4edbbf79ff6f8e546314e9ed03c85783))
* Add hidden lines in log file and handle return code better ([`1762667`](https://github.com/metaDMG/metaDMG/commit/17626671f58081150e0cdc8e8b76e50fadd2e9fe))

## v0.12.12 (2021-10-25)
### Fix
* Improve error logging and messages for metadamage-cpp ([`73068ed`](https://github.com/metaDMG/metaDMG/commit/73068ed2c667e9770d1f9b2ad25ffd5c11fed568))

## v0.12.11 (2021-10-21)
### Fix
* Fix 5p vs 3p back again ([`c44b8c1`](https://github.com/metaDMG/metaDMG/commit/c44b8c10f4d786f25cd218c75758fa636bc21942))
* Fix error with 3p and 5p convention ([`48b7636`](https://github.com/metaDMG/metaDMG/commit/48b7636660cc80ffecbc6bcd3ee92864fad0344c))

### Documentation
* Add mismatch-to-mapDamage ([`c4d1f47`](https://github.com/metaDMG/metaDMG/commit/c4d1f477da2a830f744582d0dd8b9ef5cbb76cc4))

## v0.12.10 (2021-10-21)
### Fix
* Update versions (including metaDMG-viz) ([`0545eea`](https://github.com/metaDMG/metaDMG/commit/0545eeae4bb84e2fc310a7b8df4c041e93be346b))
* Add mapDamage conversion command ([`b808fcd`](https://github.com/metaDMG/metaDMG/commit/b808fcd465f2ee7811c3b47c9786e51861efa1eb))

## v0.12.9 (2021-10-12)
### Fix
* Remove .bin files ([`c16364d`](https://github.com/metaDMG/metaDMG/commit/c16364d1201a443dc58a9fcc624eda1fc9a91630))

### Documentation
* Include mismatch-to-mapDamage in readme ([`29cbcf9`](https://github.com/metaDMG/metaDMG/commit/29cbcf9046aa0735af0e405d65f9335637e58bc5))

## v0.12.8 (2021-10-11)
### Fix
* Add CLI command to convert mismatch files to mapDamage format ([`c6e35a9`](https://github.com/metaDMG/metaDMG/commit/c6e35a9544760cbcec7478ce373ed98c07ca9e3e))

## v0.12.7 (2021-10-11)
### Fix
* Fix error with bad fits and mask them invalid ([`dd58c6c`](https://github.com/metaDMG/metaDMG/commit/dd58c6c3975bfd233b8573a43ab14a52aec6d97d))

## v0.12.6 (2021-10-07)
### Fix
* Update dashboard and include online example of dashboard ([`39ef8bb`](https://github.com/metaDMG/metaDMG/commit/39ef8bb42a8b5b8816ba29761eb0f1f682311a63))

### Documentation
* Add interactive dashboard to readme ([`61f3116`](https://github.com/metaDMG/metaDMG/commit/61f311668a372cabc960a4deb8bbca74c31a516b))

## v0.12.5 (2021-10-06)
### Fix
* Remove forced fitting ([`bbfe0dc`](https://github.com/metaDMG/metaDMG/commit/bbfe0dc938c673591e71abaebc1159a28317deb4))
* Add metaDMG version to logging ([`12d968a`](https://github.com/metaDMG/metaDMG/commit/12d968a20b95ce0c520525f9a1e3b8b803137552))

## v0.12.4 (2021-10-06)
### Fix
* Update packages ([`8fb48b5`](https://github.com/metaDMG/metaDMG/commit/8fb48b51b6bc357b7221d7fa8313f23545544974))

## v0.12.3 (2021-10-06)
### Fix
* Update dashboard ([`2fae93f`](https://github.com/metaDMG/metaDMG/commit/2fae93f0225691c68d7081edf8ae873298721b79))
* Add small fix to deal with old mismatch files that uses the old notation (|z| instead of |x|) ([`4093b0f`](https://github.com/metaDMG/metaDMG/commit/4093b0fcfa4c40e77f08da91c726ad474b511d37))

## v0.12.2 (2021-10-05)
### Fix
* Update dashboard ([`4667002`](https://github.com/metaDMG/metaDMG/commit/46670021bfc50813b884085fffbf8110cf33c34d))
* Improve frequentists fits for forward and reverse fits ([`735d25c`](https://github.com/metaDMG/metaDMG/commit/735d25c742a9e627c4fded2cd86ff861fefe04c6))

## v0.12.1 (2021-09-30)
### Fix
* Fix ImportError in NumPyro ([`8245c57`](https://github.com/metaDMG/metaDMG/commit/8245c57a11c87c97117c5178ee958f97d9ea8809))

### Documentation
* Update readme ([`fda4eef`](https://github.com/metaDMG/metaDMG/commit/fda4eefe5e341a0b6e10cf704eccccd20230fc0c))
* Update readme with how to update ([`753b360`](https://github.com/metaDMG/metaDMG/commit/753b360ce4332d9ddd086d5529dd7e15d2f3c93e))

## v0.12.0 (2021-09-30)
### Feature
* Update Dashboard to include pdf-plots and progressbar, and update Dash and dbc ([`fbf727c`](https://github.com/metaDMG/metaDMG/commit/fbf727c86c930d1675a31e9de61969323c2d8ec4))

## v0.11.4 (2021-09-24)
### Fix
* Add better handling of fit errors ([`4facb88`](https://github.com/metaDMG/metaDMG/commit/4facb88f1c25974adf73c3a20a546dfe859af3d9))

## v0.11.3 (2021-09-22)
### Fix
* Add progress bars when running single files or with a single core ([`11c8cdb`](https://github.com/metaDMG/metaDMG/commit/11c8cdbb8f9b74462cf031107beed043d0bdca37))
* Improve error logging while fitting ([`cce13ab`](https://github.com/metaDMG/metaDMG/commit/cce13ab4c4debce61a333c7fa686d452a0a29465))
* Memory leak of bayesian modelling ([`d04f5a8`](https://github.com/metaDMG/metaDMG/commit/d04f5a8e9e3ed8db30910e33f5d74f65944ca926))

## v0.11.2 (2021-09-21)
### Fix
* Log errors to see where they occur and skip them for now. ([`40d0387`](https://github.com/metaDMG/metaDMG/commit/40d038772882c08369504f408e32837d20c64c31))

## v0.11.1 (2021-09-20)
### Fix
* Allow running for old config files without cores_pr_fit being set ([`9a07f83`](https://github.com/metaDMG/metaDMG/commit/9a07f838a545348b8b29ec64250a7f3f1a793bf8))

## v0.11.0 (2021-09-20)
### Feature
* Add "cores-pr-fit" as config parameter ([`0a26847`](https://github.com/metaDMG/metaDMG/commit/0a26847c9e333697f5bece26d3239824018719e1))

## v0.10.6 (2021-09-20)
### Fix
* Use random ports for logging to decrease risk of reusing same port ([`200eecc`](https://github.com/metaDMG/metaDMG/commit/200eecca3f7c45cbaab1246fe7694734494fffd4))

## v0.10.5 (2021-09-17)
### Fix
* Allow for multiple loggers (multiple jobs) ([`0ee5ce0`](https://github.com/metaDMG/metaDMG/commit/0ee5ce05ef9ca3b496759e7433bb223037b6cb18))

## v0.10.4 (2021-09-17)
### Fix
* Update metaDMG-viz ([`7fc3878`](https://github.com/metaDMG/metaDMG/commit/7fc38788402599adb520eff75cbd364fc92fa147))
* Make null model more similar to damage model ([`74d575e`](https://github.com/metaDMG/metaDMG/commit/74d575e23c2faf54c62dc06e2de9d515d67fbd60))

## v0.10.3 (2021-09-17)
### Fix
* Refactor dashboard to only take a results dir as input ([`26608bb`](https://github.com/metaDMG/metaDMG/commit/26608bb6b532e6af9ff96b5b4697cb88a1b52732))

## v0.10.2 (2021-09-17)
### Fix
* Better parsing of read mode vs contig mode ([`06e3039`](https://github.com/metaDMG/metaDMG/commit/06e3039423a6138a8bed54cd812734489485b63e))

## v0.10.1 (2021-09-16)
### Fix
* Bump metaDMG-viz version ([`3bb8bae`](https://github.com/metaDMG/metaDMG/commit/3bb8bae1367c67232a39e3c64f213c59c0f7a87e))

## v0.10.0 (2021-09-16)
### Feature
* Add Bayesian computation of rho_Ac ([`db61f5d`](https://github.com/metaDMG/metaDMG/commit/db61f5d0d9bc49a5d537457178445a0bc7a100cb))

### Fix
* Update metaDMG-viz ([`931a9f1`](https://github.com/metaDMG/metaDMG/commit/931a9f15a71f6067708a5059f8e1322b47dfee61))
* Update logging text ([`a58e576`](https://github.com/metaDMG/metaDMG/commit/a58e576ab7e705c1ba72972a7d2c549a8fda8deb))
* Add uncertainty estimates to Bayesian results ([`21e81c7`](https://github.com/metaDMG/metaDMG/commit/21e81c7198c464937597ee1fa89bc471bae12685))
* Fix newest renaming bugs ([`e190114`](https://github.com/metaDMG/metaDMG/commit/e1901143dd2c5387314e5543a0bece86e400e215))

## v0.9.2 (2021-09-14)
### Fix
* Bump metaDMG-viz version ([`4a48962`](https://github.com/metaDMG/metaDMG/commit/4a48962592eefa358257097cd9dad942597bc389))
* Improve error messages for Bayesian fits ([`4e7beba`](https://github.com/metaDMG/metaDMG/commit/4e7beba224e05eaa2faef04f47aac1aa9d754932))

## v0.9.1 (2021-09-14)
### Fix
* Update metaDMG-viz dependency ([`b74212f`](https://github.com/metaDMG/metaDMG/commit/b74212f1da275aa5718dc58c023fd27a9fae5dc7))

## v0.9.0 (2021-09-13)
### Feature
* Include fitting as part of main package ([`14c2b7c`](https://github.com/metaDMG/metaDMG/commit/14c2b7c850f3b0c6a4d0c8423d20741521349378))

### Fix
* Remove MetaDMG-cpp from github ([`bc5bd05`](https://github.com/metaDMG/metaDMG/commit/bc5bd0519c27be5faadee2c05141928e9b9bcbc4))

## v0.8.0 (2021-09-09)
### Feature
* Better tests ([`536b1f7`](https://github.com/metaDMG/metaDMG/commit/536b1f732fdc1601c41e01342393975e1ed1ac67))


## v0.7.0 (2021-09-09)

### Build

Changed to automatic versioning.


## v0.6.0 (2021-09-09)

### Build

- Use semantic versioning
- Use src layout
