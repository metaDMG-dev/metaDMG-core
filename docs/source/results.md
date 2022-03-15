
# Results

The column names in the results and their explanation:

- General parameters:
  - `tax_id`: The tax ID. Categorical string.
  - `tax_name`: The tax name. Categorical string.
  - `tax_rank`: The tax rank. Categorical string.
  - `sample`: The name of the original sample. Categorical string.
  - `N_reads`: The number of reads. int64.
  - `N_alignments`: The number of alignments. int64.

- Fit related parameters:
  - `lambda_LR`: The likelihood ratio between the null model and the ancient damage model. This can be interpreted as the fit certainty, where higher values means higher certainty. float32.
  - `lambda_LR_P`: The likelihood ratio expressed as a probability. float32.
  - `lambda_LR_z`: The likelihood ratio expressed as number of ![](https://latex.codecogs.com/svg.image?%5Csigma). float32.
  - `D_max`: The estimated damage. This can be interpreted as the amount of damage in the specific taxa. float32.
  - `q`: The damage decay rate. float32.
  - `A`: The background independent damage. float32.
  - `c`: The background. float32.
  - `phi`: The concentration for a beta binomial distribution (parametrised by ![](https://latex.codecogs.com/svg.image?%5Cmu) and ![](https://latex.codecogs.com/svg.image?%5Cphi)). float32.
  - `rho_Ac`: The correlation between `A` and `c`. High values of this are often a sign of a bad fit. float32.
  - `valid`: Wether or not the fit is valid (defined by [iminuit](https://iminuit.readthedocs.io/en/stable/)). bool.
  - `asymmetry`: An estimate of the asymmetry of the forward and reverse fits. See below for more information. float32.
  - `XXX_std`: the uncertainty (standard deviation) of the variable `XXX` for `D_max`, `A`, `q`, `c`, and `phi`.
  - `forward__XXX`: The same description as above for variable `XXX`, but only for the forward read.
  - `reverse__XXX`: The same description as above for variable `XXX`, but only for the reverse read.

- Read related parameters
  - `mean_L`: The mean read length of all the individual, unique reads that map to the specific taxa. float64.
  - `std_L`: The standard deviation of the above. float64.
  - `mean_GC`: The mean GC content of all the individual, unique reads that map to the specific taxa. float64.
  - `std_GC`: The standard deviation of the above. float64.
  - `tax_path`: The taxanomic path from the LCA to the root through the phylogenetic tree. string.

- Count related paramters:
  - `N_x=1_forward`: The total number of _"trials"_, ![](https://latex.codecogs.com/svg.image?N), at position ![](https://latex.codecogs.com/svg.image?x=1): ![](https://latex.codecogs.com/svg.image?N(x=1)) in the forward direction. int64.
  - `N_x=1_reverse`:  Same as above, but for the reverse direction. int64.
  - `N_sum_forward`:  The sum of ![](https://latex.codecogs.com/svg.image?N) over all positions in the forward direction. int64.
  - `N_sum_reverse`: Same as above, but for the reverse direction. int64.
  - `N_sum_total`:  The total sum `N_sum_forward` and `N_sum_reverse`. int64.
  - `N_min`: The minimum of ![](https://latex.codecogs.com/svg.image?N) for all positions (forward and reverse alike). int64.
  - `k_sum_forward`:  The total number of _"successes"_, ![](https://latex.codecogs.com/svg.image?k), summed over all positions in the forward direction. int64.
  - `k_sum_reverse`: Same as above, but for the reverse direction. int64..
  - `k_sum_total`: The total sum `k_sum_forward` and `k_sum_reverse`. int64.
  - `k+i`: The number of _"successes"_, ![](https://latex.codecogs.com/svg.image?k) at position ![](https://latex.codecogs.com/svg.image?z=i): ![](https://latex.codecogs.com/svg.image?k(x=1)) in the forward direction. int64.
  - `k-i`: Same as above, but for the reverse direction. int64.
  - `N+i`: The number of _"trials"_, ![](https://latex.codecogs.com/svg.image?N) at position ![](https://latex.codecogs.com/svg.image?z=i): ![](https://latex.codecogs.com/svg.image?N(x=1)) in the forward direction. int64.
  - `N-i`: Same as above, but for the reverse direction. int64.
  - `f+i`: The fraction between ![](https://latex.codecogs.com/svg.image?k) and ![](https://latex.codecogs.com/svg.image?N) at position ![](https://latex.codecogs.com/svg.image?z=i) in the forward direction. int64.
  - `f-i`: Same as above, but for the reverse direction. int64.
