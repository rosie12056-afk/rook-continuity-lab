# Preregistered-analysis deviation log

The preregistration proposed ordinal mixed-effects models "where supported"
and required descriptive distributions plus bootstrap intervals if assumptions
or tooling failed.

The bundled local runtime did not provide an ordinal mixed-effects package or
`statsmodels`. No package was installed after outcomes were visible. The
primary inference therefore remains the preregistered paired bootstrap.

As a prespecified concern was unequal carrier tokenization, we additionally run
a fixed-effects OLS sensitivity analysis using only bundled NumPy/Pandas:

- carrier fixed effects;
- condition and framing terms fixed before fitting;
- provider-reported input tokens as a standardized covariate;
- percentile intervals from 2,000 scenario-cluster bootstrap resamples.

This sensitivity model does not replace the paired bootstrap and is reported as
a robustness check. The deviation was recorded before inspecting its
coefficients.
