# Changelog

<!--next-version-placeholder-->

## v0.30.1 (2022-09-07)
### Fix
* Improve multiprocessing api ([`e196a53`](https://github.com/metaDMG-dev/metaDMG-core/commit/e196a5374809ebd5e7a1d77df13374b69f9c73c9))

## v0.30.0 (2022-09-06)
### Feature
* Update priors to be more conservative ([`cb98015`](https://github.com/metaDMG-dev/metaDMG-core/commit/cb980159820ff8f0f4e09e3e2677c97ca7683955))

## v0.29.1 (2022-09-06)
### Fix
* Use approximate conf. intervals for bayesian ([`e92f298`](https://github.com/metaDMG-dev/metaDMG-core/commit/e92f298fc6833076673244465ebb7b7a05ca4ce8))

## v0.29.0 (2022-09-04)
### Feature
* Add confidence intervals to Bayesian model ([`38c95d5`](https://github.com/metaDMG-dev/metaDMG-core/commit/38c95d5ea48ce59354eaa050e67f0a41166aad21))

## v0.28.6 (2022-08-18)
### Fix
* Fix issue with logging in parallel ([`9e065aa`](https://github.com/metaDMG-dev/metaDMG-core/commit/9e065aa5cf3af81ec670bcd039e964ca848574eb))

### Documentation
* Add docstring to workflow function ([`2ee4c6b`](https://github.com/metaDMG-dev/metaDMG-core/commit/2ee4c6b4b96bc3e269dd5a83fe716b3b2b389812))

## v0.28.5 (2022-08-18)
### Fix
* Improve logging messages ([`7a35b3a`](https://github.com/metaDMG-dev/metaDMG-core/commit/7a35b3a8899ab879df822444506521ebd52d6410))

## v0.28.4 (2022-08-17)
### Fix
* Handle empty data and better error handling ([`f2d27ff`](https://github.com/metaDMG-dev/metaDMG-core/commit/f2d27ff6b1c16a18736e9d2ac3078504e046abd6))

## v0.28.3 (2022-08-17)
### Fix
* Catch metaDMG-cpp error with unsorted files ([`7c42082`](https://github.com/metaDMG-dev/metaDMG-core/commit/7c42082b8ab3b531dce21613bcf5cc275d8d2ef0))

## v0.28.2 (2022-08-15)
### Fix
* Improve Bayesian D_max when few reads ([`35d7247`](https://github.com/metaDMG-dev/metaDMG-core/commit/35d7247d1822e8d82db4a4f43cc56c6019bf85ae))

## v0.28.1 (2022-08-12)
### Fix
* Improve low-damage fits ([`838143b`](https://github.com/metaDMG-dev/metaDMG-core/commit/838143b0eef0e469797d1049d6c32b12b0371bd5))

### Documentation
* Update the docstring for the PMD command ([`102f7aa`](https://github.com/metaDMG-dev/metaDMG-core/commit/102f7aa28957afa259e4bfd00734c13dea10deb2))

## v0.28.0 (2022-08-12)
### Feature
* Better fits for low-damage groups ([`793ffff`](https://github.com/metaDMG-dev/metaDMG-core/commit/793ffffab0fce83a61b14a0712ad98ad4cc8d2b8))

## v0.27.2 (2022-08-11)
### Fix
* Update dependencies ([`299a6c4`](https://github.com/metaDMG-dev/metaDMG-core/commit/299a6c4cd389b8673815df73a4e24915a1693805))

### Documentation
* Update PMD command ([`9bb6382`](https://github.com/metaDMG-dev/metaDMG-core/commit/9bb638248bedbb98351782afa4df378b7a625353))

## v0.27.1 (2022-08-10)
### Fix
* Fix PMD command handle errors and output csv ([`84c002f`](https://github.com/metaDMG-dev/metaDMG-core/commit/84c002f95e6c442157400307c501e437c039dc80))

### Documentation
* Update config-gui image in docs ([`9700d88`](https://github.com/metaDMG-dev/metaDMG-core/commit/9700d8822bd514a2678ab525ea4e3959acf181a4))
* Add config-gui image to docs ([`e62e603`](https://github.com/metaDMG-dev/metaDMG-core/commit/e62e603e2d968c0b0b3a5c4ecc0dee045a8d041c))

## v0.27.0 (2022-07-15)
### Feature
* Add config-gui to CLI ([`672fea7`](https://github.com/metaDMG-dev/metaDMG-core/commit/672fea743f64a4aa54ee3a90679afb72ab2bca1f))
* Use Rich with Typer for pretty CLI ([`3a960a5`](https://github.com/metaDMG-dev/metaDMG-core/commit/3a960a5bd584e16ab08e34ddea146d882ef2d0c5))

### Fix
* Add groups to CLI ([`8762292`](https://github.com/metaDMG-dev/metaDMG-core/commit/876229267d4805bb8a86e622945bf48aacf83098))
* Update dependencies ([`2f91c56`](https://github.com/metaDMG-dev/metaDMG-core/commit/2f91c567b0e6b1b019e1e9573ef85bf6cd0168f5))

### Documentation
* Include config-gui in docs ([`480f813`](https://github.com/metaDMG-dev/metaDMG-core/commit/480f813ad2d4bb229b9dda34e0306d4df0dacce2))

## v0.26.1 (2022-07-04)
### Fix
* Change alignment file in test dir ([`2beed66`](https://github.com/metaDMG-dev/metaDMG-core/commit/2beed66e16c6bf15517867d1b968af56bbbf2fcf))

### Documentation
* Add min-reads to onoine docs ([`0f74800`](https://github.com/metaDMG-dev/metaDMG-core/commit/0f74800a681a1fbe3dce85c4c02a364fae8802c6))

## v0.26.0 (2022-07-04)
### Feature
* Add minimum reads as an optional threshold ([`23f9c16`](https://github.com/metaDMG-dev/metaDMG-core/commit/23f9c16bd0291e41ff8fb59e22cf004ab8605e13))

## v0.25.0 (2022-07-04)
### Feature
* Disallow the usage of similarity scores and edit distances at the same time ([`bf7f941`](https://github.com/metaDMG-dev/metaDMG-core/commit/bf7f941209629a9e2e285117773003b15a344039))

### Fix
* Re-raise errors ([`9b08e76`](https://github.com/metaDMG-dev/metaDMG-core/commit/9b08e76d2fb27bf49fd8e11406cabeffc9798f51))
* Add better error message in the of unspecified custom database ([`a711a01`](https://github.com/metaDMG-dev/metaDMG-core/commit/a711a010e3a60f107970392636307f1284eacb6a))

## v0.24 (2022-06-14)
### Feature
* Add PMD command and include Configs in core ([`11eab19`](https://github.com/metaDMG-dev/metaDMG-core/commit/11eab1967f6ed957e87ea135285501c6061fa640))

### Fix
* Change "nreads" in non-LCA stats to N_alignments ([`85c033c`](https://github.com/metaDMG-dev/metaDMG-core/commit/85c033c9f0aeeb57c39f8a6297ffbca7570df73a))
* Fix bug with mismatch-to-mapDamage when forward-only mode ([`89670fa`](https://github.com/metaDMG-dev/metaDMG-core/commit/89670fa84efedf5460804fc55abf1c10e17d619c))
* Update dependencies ([`206c47b`](https://github.com/metaDMG-dev/metaDMG-core/commit/206c47b6cd5e97e10acdfa61d27b151e14eb2bf8))
* Allow mismatch_to_mapDamage to work with forward-only data ([`c59240f`](https://github.com/metaDMG-dev/metaDMG-core/commit/c59240f635c840623ba7ba83ef3d7843845f3668))
* Fix issue when using --add-fit-predictions together with forward_only ([`6c0126c`](https://github.com/metaDMG-dev/metaDMG-core/commit/6c0126c8790c9092373d92cf4469317da130295f))
* Fix issue with forward-only in dashboard ([`7d5310f`](https://github.com/metaDMG-dev/metaDMG-core/commit/7d5310f5fac4f5acb4d3362a1ed4f84441e59bf1))
* Improve marks in dashboard ([`f105fcf`](https://github.com/metaDMG-dev/metaDMG-core/commit/f105fcff5adbfc248e39e59de95893ccf2a26f6d))
* Allow for compressed files in convert. ([`aebdbff`](https://github.com/metaDMG-dev/metaDMG-core/commit/aebdbff86d657fb87d9bd2eb7700047ea19dd803))
* Infer metaDMG-cpp from config file in PMD ([`f38e3c6`](https://github.com/metaDMG-dev/metaDMG-core/commit/f38e3c677fcd322265eeedaab2d3b9c91f668b98))
* Include static folder in docs ([`dcbcfd9`](https://github.com/metaDMG-dev/metaDMG-core/commit/dcbcfd93357b240222e205f050877bddad1930ad))
* Continue to use Union in Python 3.9 ([`2a04213`](https://github.com/metaDMG-dev/metaDMG-core/commit/2a04213176b2d93fdbb13da24ab7def6af16e7e3))
* Update lock file ([`ecec382`](https://github.com/metaDMG-dev/metaDMG-core/commit/ecec38206036247cb15ed5cda4a150aac1ccf652))

### Documentation
* Update docs action ([`15a5a3b`](https://github.com/metaDMG-dev/metaDMG-core/commit/15a5a3ba2c324f670d2a0e4d2dcfeb155fde074e))
* Remove _static ([`1d08ccd`](https://github.com/metaDMG-dev/metaDMG-core/commit/1d08ccd898d1d1fc15b7ef60afdbdd8e15758466))
* Include PMD in docs ([`5e3e37d`](https://github.com/metaDMG-dev/metaDMG-core/commit/5e3e37d95c1607b20df18377adad0f6a394b30c1))
* Add dashboard styling to docs ([`bf6583d`](https://github.com/metaDMG-dev/metaDMG-core/commit/bf6583df7190aa1eed97903c8a2f280ceba1d7e6))
* Update dashboard section ([`38a7689`](https://github.com/metaDMG-dev/metaDMG-core/commit/38a76896b4843c30c73ab5e4a61a4193165df950))
* Update SSH flowchart ([`edc420a`](https://github.com/metaDMG-dev/metaDMG-core/commit/edc420a3072754c2d04de771732e646c8aa7c3cd))
* Add logo to readme at github ([`ec7a3b3`](https://github.com/metaDMG-dev/metaDMG-core/commit/ec7a3b320d2502a920827be1bc2e8e32dda15be8))
* Add logo ([`2a45e57`](https://github.com/metaDMG-dev/metaDMG-core/commit/2a45e57cc6b9590646880a3e8f34cb9ba3aaa557))

## v0.23 (2022-03-29)


### Feature
* Add metaDMG.main ([`fc89050`](https://github.com/metaDMG/metaDMG/commit/fc89050db794c1c88261ca723c4461f8ebe8f3a4))

### Fix
* Update old configs in convert and filter CLI ([`c7fad7c`](https://github.com/metaDMG/metaDMG/commit/c7fad7c91bd5e41c3cd1650e9fc895f4179e9c27))

### Documentation
* Add more advanced tutorial (KapK) ([`8596c43`](https://github.com/metaDMG/metaDMG/commit/8596c433aece791a6e4a060274c2311bd95680b8))
* Add github pages action ([`d2a5b7f`](https://github.com/metaDMG-dev/metaDMG-core/commit/d2a5b7f8e23813ad73cea4d66a52e8e1a77ece27))
* Update CLI doc ([`5ad0851`](https://github.com/metaDMG/metaDMG/commit/5ad0851248f52c3b0880287dccf38d6ee0d11406))
* Add mermaid diagram to tutorial ([`93ac0c0`](https://github.com/metaDMG/metaDMG/commit/93ac0c09e1358d245103874612b310f5cf527e6a))

## v0.22 (2022-03-28)
### Feature
* Add --overwrite as option in config ([`f73bda3`](https://github.com/metaDMG/metaDMG/commit/f73bda3239f2f6ecf4f216554f0312dd42f23593))
* Add D_max significance and variance_scaling ([`4c5f7f7`](https://github.com/metaDMG/metaDMG/commit/4c5f7f74ef473538f33c3989ba71ea962a6ea6ee))
* Add test data to package ([`a522623`](https://github.com/metaDMG/metaDMG/commit/a5226230fc21246eb5fa4fa7921b656f07ecd466))
### Fix
* Test CI-CD workflow ([`02636a9`](https://github.com/metaDMG/metaDMG/commit/02636a9738345e45d9b9a0d5f0c3f87d628f5023))
* Add tqdm to viz ([`87f670b`](https://github.com/metaDMG/metaDMG/commit/87f670b44462c4c39276ede0a5b48e5059edcbb1))
* Update tests ([`f3ab9ae`](https://github.com/metaDMG/metaDMG/commit/f3ab9ae1de9dca6ee4cedff486714ea2b512b3d3))
* Inlcude helper functions in metaDMG.main ([`e8fc27d`](https://github.com/metaDMG/metaDMG/commit/e8fc27d828af2a629d27eaf67201682eb154274b))
* Auto-update old config files, but raise warning ([`b3b8f32`](https://github.com/metaDMG/metaDMG/commit/b3b8f32ad3e6412289a36f50ba6054d921812bd3))
* Check BAM size ([`982d2d4`](https://github.com/metaDMG/metaDMG/commit/982d2d4a62522e76a91bec8e1930b7d9e9bf1567))
* Use dependency groups for dev tools ([`e1c010a`](https://github.com/metaDMG/metaDMG/commit/e1c010aa4c9cb6130c93539f80deb926c774d9a1))
* Pre-commit ([`b1fd695`](https://github.com/metaDMG/metaDMG/commit/b1fd695ed4db1cafc52d0a0930cc77cf79c93ed8))

### Documentation
* Include Python version in the requirements ([`ced545b`](https://github.com/metaDMG/metaDMG/commit/ced545bb1ca5b79309e754e750d6cf8f3999afa0))


## v0.21 (2022-03-17)
### Feature
* Merge viz (dashboard) ([`28e56bc`](https://github.com/metaDMG/metaDMG/commit/28e56bc0007a3b0c05c747adabf897b218e28f67))
* Add slimmer base install of metaDMG (with fit, viz, and all as extras) ([`75b4ecc`](https://github.com/metaDMG/metaDMG/commit/75b4ecc3879d340260a5d4764aa088c738819107))
* Change default install ([`d8cc434`](https://github.com/metaDMG/metaDMG/commit/d8cc434585ccd597d5f19d7ddeb7d5e4af43d506))
* Make fitting part of package optional ([`5efd447`](https://github.com/metaDMG/metaDMG/commit/5efd447a92a0a0f78e3ebfefa880df9d782c7e44))

### Fix
* Try to fix action ([`6c736a0`](https://github.com/metaDMG/metaDMG/commit/6c736a0314daf434704cd9321d617f932d4b5804))
* Fix actions ([`e1e6e8d`](https://github.com/metaDMG/metaDMG/commit/e1e6e8d5bb53fc448ca9491f6aac7cdfef20d573))
* Disable auto-reloading in dashboard to allow for debugging ([`8a4e845`](https://github.com/metaDMG/metaDMG/commit/8a4e8453f93b98c9869f9144ed87268727a77305))
* Move CLI-related code to cli folder ([`6ad0293`](https://github.com/metaDMG/metaDMG/commit/6ad0293d8f684deee20a11e6093527a6154d21b1))

## v0.20 (2022-03-16)

### Feature
* Update dashboard to also work with non-LCA ([`0495d81`](https://github.com/metaDMG/metaDMG/commit/0495d811a179bb6842b2c9d6afafe8f0d6baa1d4))
* Allow for non-LCA mode ([`2bd5901`](https://github.com/metaDMG/metaDMG/commit/2bd5901ced1897dd71cf9a5ee9c6dabfff00789a))

### Fix
* Update dependencies (inlcuding dashboard= ([`003e0c8`](https://github.com/metaDMG/metaDMG/commit/003e0c8f119096aee3dca40e261e4e9036271623))
* Fix issue with dashboard and old parquet files ([`0506d5a`](https://github.com/metaDMG/metaDMG/commit/0506d5a387c4b302389abc320d42a2af435d7eed))
* Improve Paths parsing ([`1ab3cd1`](https://github.com/metaDMG/metaDMG/commit/1ab3cd170bfb000ad64a8898b9f66c1fe5b5bf56))
* Parse metaDMG-cpp path as str ([`0943a29`](https://github.com/metaDMG/metaDMG/commit/0943a291b7c244599168313c59b4e761f649cc57))
* Fix error with attrs / dataclass ([`8a507b9`](https://github.com/metaDMG/metaDMG/commit/8a507b9f81ea2860558b7923e90ba050f0d7da5e))
* Use Python v3.9 ([`b93d97c`](https://github.com/metaDMG/metaDMG/commit/b93d97cee763d2c39c2b2e2b1050822ce2d38c08))
* Fix error with mapDamage formats ([`c8746ce`](https://github.com/metaDMG/metaDMG/commit/c8746cecb96ff42842765ac316646fb79d95a10e))
* Fix parsing with metaDMG-lca binary ([`f69e5f0`](https://github.com/metaDMG/metaDMG/commit/f69e5f0d87ccd492dc3ad57c7180a429403b7299))
* Fix error with Path and metaDMG-lca ([`c7a57c1`](https://github.com/metaDMG/metaDMG/commit/c7a57c128877bebe97a4bd6d1c6d451aa9d52fba))
* Adding type hints, rewrite config files and adding confirmation prompt ([`a046687`](https://github.com/metaDMG/metaDMG/commit/a046687af4339429f5b73aebfe2d0c329ebca11a))
* Make all tax_ids to strings ([`fc1fee4`](https://github.com/metaDMG/metaDMG/commit/fc1fee463a6d70e79de6a5dd39471c1ab5edb62b))

### Documentation
* Fix permalink icon ([`271b912`](https://github.com/metaDMG/metaDMG/commit/271b9129737f7cb2b372ef6e4460cad5e193e00a))
* Use sphinx_book_theme ([`0b3d377`](https://github.com/metaDMG/metaDMG/commit/0b3d377c9c559bac4725655cd7301f2c17d1cad7))
* Add viewcode ([`980aa65`](https://github.com/metaDMG/metaDMG/commit/980aa65b8bce82eb3f02619960c69b6b90209e95))
* Add auto doc summary ([`88345f8`](https://github.com/metaDMG/metaDMG/commit/88345f86cf8bc99f8944f470fd4a49268ccb2ebd))
* Working version ([`d43b46e`](https://github.com/metaDMG/metaDMG/commit/d43b46ea3f835b33f3fdea48775f1243ea63b15d))
* Add working autodoc for markdown ([`31212d6`](https://github.com/metaDMG/metaDMG/commit/31212d6b3f1e7bae8deedd8d99fc9b1b1cc46514))
* Working autodocs ([`dacb0d2`](https://github.com/metaDMG/metaDMG/commit/dacb0d251e10dcf4dc604aeef0d29ae85b156edc))
* Remove types from docstrings ([`1b24266`](https://github.com/metaDMG/metaDMG/commit/1b242660e8ab1f8e38eafcdc3d89e18485b4d86a))
* Add autodocs for utils ([`7f31196`](https://github.com/metaDMG/metaDMG/commit/7f31196dc736132ccb3b083c56be9de9c10ff11e))
* Update docs ([`6e0767a`](https://github.com/metaDMG/metaDMG/commit/6e0767a4a695f67509f6c8a231780d73b049e502))
* Add first version of docs ([`72a23d9`](https://github.com/metaDMG/metaDMG/commit/72a23d949e7fc88a062d7207933d892a9627db60))
* Try to add docs ([`f683151`](https://github.com/metaDMG/metaDMG/commit/f6831512878f63d14cf2aafa9ca7b6c0ededc814))
* Add docstrings ([`bbc6fd3`](https://github.com/metaDMG/metaDMG/commit/bbc6fd35f213e6470d15f444bd27e98f79dea5e6))

## v0.19 (2022-03-09)
### Feature
* Allow forward-only ([`c0a8cb1`](https://github.com/metaDMG/metaDMG/commit/c0a8cb148d17e37fcb369e70356fdb8d99677f0a))

### Fix
* Update dashboard to allow the use of forward-only ([`35eeebc`](https://github.com/metaDMG/metaDMG/commit/35eeebc81010737a3add302ad76a13680e4452f5))

### Documentation
* Update readme to reflect the forward-only use ([`5f0e760`](https://github.com/metaDMG/metaDMG/commit/5f0e760e4ea7f3884f6e6bdc94e2a5c515c7b29c))
* Update changelog ([`b32a0dd`](https://github.com/metaDMG/metaDMG/commit/b32a0dd3368ca9300b8dc2fc319ba6ebec8b2ae7))

## v0.18 (2022-03-08)

## v0.17 (2022-03-08)
* Add damage-mode "local" or "global" as options ([`5e153bb`](https://github.com/metaDMG/metaDMG/commit/5e153bb8dddacb32ac4cccad5903950a315c0175))
* Make --names, nodes and acc2tax mandatory for LCA but not for local and global ([`b2ae2a2`](https://github.com/metaDMG/metaDMG/commit/b2ae2a29dbca5b7b8b9b947da8aade7dc6cc6575))
* Improve readme regarding non-LCA mode ([`bbb36b5`](https://github.com/metaDMG/metaDMG/commit/bbb36b53a2a7fc9ab93d66666a6ec79a9f8b8e89))
* Add temporary folders for LCA ([`21201c7`](https://github.com/metaDMG/metaDMG/commit/21201c71c5ce45dba384cb0e2ef9abd99aaa69f1))
* Update logger-tt dependency ([`30814f7`](https://github.com/metaDMG/metaDMG/commit/30814f7f67867fd543c07eba241bb7aa1ce4e458))
* Update logging port ([`e193985`](https://github.com/metaDMG/metaDMG/commit/e193985f004dfd839dc40f8f88265bafea62699f))
* Update metaDMG_viz ([`48b1838`](https://github.com/metaDMG/metaDMG/commit/48b1838f24062d8bdf417f753541c7f400d4503e))
* Add jackknife possibility for computing z error ([`a486431`](https://github.com/metaDMG/metaDMG/commit/a486431af2bb706378086747161828bba6b5c7e9))
* Update dependencies ([`a1d04e3`](https://github.com/metaDMG/metaDMG/commit/a1d04e34103887ce6457eb2c06f0019f4e550d42))
* Fix bug when concatenating two dataframes when appending fit predictions ([`ac3bd67`](https://github.com/metaDMG/metaDMG/commit/ac3bd67d1d5a889a47a91e2bc51b8314b0291b57))
* Fix CLI bug ([`d8c1dee`](https://github.com/metaDMG/metaDMG/commit/d8c1dee44b49f6d834bca7cc95178e14d5b8c942))
* Update docs to reflect update in metadamage ([`72b055f`](https://github.com/metaDMG/metaDMG/commit/72b055ffb2623bdc0cef9bc46dcd17f7657570c6))

## v0.16 (2022-02-02)
* Remove error when parsing taxes with apostrophe in tax name ([`e0e0405`](https://github.com/metaDMG/metaDMG/commit/e0e0405b1c719d5a06c64565e70a4872ab680374))
* Also remove lca.gz files ([`a8dbf91`](https://github.com/metaDMG/metaDMG/commit/a8dbf914b0b46382a15c309d5057daf933bda68c))
* Update dependencies for M1 macs ([`5f80629`](https://github.com/metaDMG/metaDMG/commit/5f80629b85d5515fa38350bccc216af985b47b9e))

## v0.15 (2022-01-31)
* Add the option to include the fit predictions in the output csv files ([`a12d585`](https://github.com/metaDMG/metaDMG/commit/a12d585e53c2a8f497258a8706a2bfebe70d3520))
* Read .gz zipped files ([`639873b`](https://github.com/metaDMG/metaDMG/commit/639873b505c564374b005cf4dd6fcdb4dd7c1241))
* Update dependencies ([`33f46fb`](https://github.com/metaDMG/metaDMG/commit/33f46fb1819864c5f66e426f760c70fa8ff67016))
* Update docs ([`202d484`](https://github.com/metaDMG/metaDMG/commit/202d48402d7eae06e011a620a3b96765542dabf3))

## v0.14 (2022-01-05)
* Update dependencies (including metaDMG-viz) ([`ed281e5`](https://github.com/metaDMG/metaDMG/commit/ed281e564fefd279f3678c9f7b710225155a02dd))

## v0.13 (2021-11-10)
* Add --long-name as bool flag to CLI ([`b2b64cb`](https://github.com/metaDMG/metaDMG/commit/b2b64cb528ab871ac73e91412616208b07c2d47a))
* Fix error when not doing progressbar in parallel Bayesian fits ([`097785a`](https://github.com/metaDMG/metaDMG/commit/097785a53e253789e4cdf248deab7a9b34bff3d6))
* Make update ([`f249210`](https://github.com/metaDMG/metaDMG/commit/f2492105460f354080593cf3edb789f4e90761d6))
* Add try except for MismatchFileError ([`76cc35c`](https://github.com/metaDMG/metaDMG/commit/76cc35c8c216c96a20cce5123a0096139a8441b7))
* Add MismatchFileError for when  mismatch.txt has error ([`a8662b0`](https://github.com/metaDMG/metaDMG/commit/a8662b08f8b732b0dd7f56c63d7aa974dcbd5c92))
* Fix error with forced and multiprocessing ([`fc8e4e0`](https://github.com/metaDMG/metaDMG/commit/fc8e4e0b35ace21c4f5586acf588e802c79221a6))
* Improve changelog ([`a065411`](https://github.com/metaDMG/metaDMG/commit/a06541165ffa5cfa9216a34b7dae0ad7d3defdc1))
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
* Allow running for old config files without cores_per_fit being set ([`9a07f83`](https://github.com/metaDMG/metaDMG/commit/9a07f838a545348b8b29ec64250a7f3f1a793bf8))
* Add "cores-per-sample" as config parameter ([`0a26847`](https://github.com/metaDMG/metaDMG/commit/0a26847c9e333697f5bece26d3239824018719e1))


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
