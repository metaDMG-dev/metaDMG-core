# Results

The column names in the results and their explanation:

## General parameters
  - `tax_id`: The tax ID. Categorical string.
  - `tax_name`: The tax name. Categorical string.
  - `tax_rank`: The tax rank. Categorical string.
  - `sample`: The name of the original sample. Categorical string.
  - `N_reads`: The number of reads. int64.
  - `N_alignments`: The number of alignments. int64.

## Fit related parameters
  - `damage`: The estimated damage in the specific taxa, $D$. float64.
  - `significance`: The number of sigmas that the damage is away from 0, i.e. how certain one should be about there being non-zero damage. float64.
  - `q`: The damage decay rate. float64.
  - `A`: The background independent damage. float64.
  - `c`: The background. float64.
  - `phi`: The concentration for a beta binomial distribution (parametrised by $\mu$ and $\phi$). float64.
  - `rho_Ac`: The correlation between $A$ and $c$, $\rho_{Ac}$. High values of this are often a sign of a bad fit. float64.
  - `XXX_std`: the uncertainty (standard deviation) of the variable `XXX` for $D$, $A$, $q$, $c$, and $\phi$.
  - `MAP_valid`: Whether or not the MAP fit is valid (defined by [iminuit](https://iminuit.readthedocs.io/en/stable/)). bool.

## Read related parameters
  - `mean_L`: The mean read length of all the individual, unique reads that map to the specific taxa. float64.
  - `std_L`: The standard deviation of the above. float64.
  - `mean_GC`: The mean GC content of all the individual, unique reads that map to the specific taxa. float64.
  - `std_GC`: The standard deviation of the above. float64.
  - `tax_path`: The taxanomic path from the LCA to the root through the phylogenetic tree. string.

## Count related paramters
  - `N_x=1_forward`: The total number of _"trials"_, $N$, at the first position in the forward direction, $N(x=1)$. int64.
  - `N_x=1_reverse`:  Same as above, but for the reverse direction, $N(x=-1)$. int64.
  - `N_sum_forward`:  The sum of $N$ over all positions in the forward direction, $\sum_i N(x=i)$. int64.
  - `N_sum_reverse`: Same as above, but for the reverse direction, $\sum_{-i} N(x=i)$. int64.
  - `N_sum_total`:  The total sum `N_sum_forward` and `N_sum_reverse`. int64.
  - `N_min`: The minimum of $N$ for all positions (forward and reverse). int64.
  - `k_sum_forward`:  The total number of _"successes"_, $k$, summed over all positions in the forward direction, $\sum_i k(x=i)$. int64.
  - `k_sum_reverse`: Same as above, but for the reverse direction, $\sum_{-i} k(x=i)$. int64..
  - `k_sum_total`: The total sum `k_sum_forward` and `k_sum_reverse`. int64.
  - `k+i`: The number of _"successes"_, $k$ at position $x=i$: $k(x=i)$ in the forward direction. int64.
  - `k-i`: Same as above, but for the reverse direction. int64.
  - `N+i`: The number of _"trials"_, $N$ at position $x=i$: $N(x=i)$ in the forward direction. int64.
  - `N-i`: Same as above, but for the reverse direction. int64.
  - `f+i`: The damage frequency, $f$, given $k$ and $N$: $f(x) = k(x) / N(x)$, at position $x=i$ in the forward direction. int64.
  - `f-i`: Same as above, but for the reverse direction. int64.
