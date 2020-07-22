# MFSDA: Multivariate Functional Shape Data Analysis

MFSDA_Python is a Python based package for statistical shape analysis.

A multivariate varying coefficient model is introduced to build the association between the multivariate shape measurements and demographic information and other clinical variables.

Statistical inference, i.e., hypothesis testing, is also included in this package, which can be used in investigating whether some covariates of interest are significantly associated with the shape information.

The hypothesis testing results are further used in clustering based analysis, i.e., significant suregion detection.

## Modules

### Loadable module

The project a Slicer loadable allowing to XXX that internally leverage invokes command line modules described below.


### CLI modules

| CLI Name           | Description |
|--------------------|-------------|
| [MFSDA_createShapes][MFSDA_createShapes]             | ??? |
| [MFSDA_run][MFSDA_run]                               |  ??? |
| [MFSDA_selectVariablesPCA][MFSDA_selectVariablesPCA] | Variable selection using Correlation with Principal Components. |

[MFSDA_createShapes]: https://github.com/DCBIA-OrthoLab/MFSDA_Python/blob/master/MFSDA/MFSDA_createShapes.xml
[MFSDA_run]: https://github.com/DCBIA-OrthoLab/MFSDA_Python/blob/master/MFSDA/MFSDA_run.xml
[MFSDA_selectVariablesPCA]: https://github.com/DCBIA-OrthoLab/MFSDA_Python/blob/master/MFSDA/Resources/Libraries/MFSDA_selectVariablesPCA.py


## History

This project was initially developed in early August 2017 by Chao Huang and Hongtu Zhu from
the [BIG-S2 lab](https://www.med.unc.edu/bigs2/) at the University of North Carolina at Chapel Hill School of Medicine.

Then, between November 2017 and June 2018, [Juan Carlos Prieto][juanprietob] from the School of Dentistry at the University Of Michigan contributed the script for generating shapes with pvalue maps, and [Loic Michoud][loic-michoud],
in the context of internship, contributed the MFSDA Slicer loadable module along with the initial infrastructure to
support distribution as a Slicer extension (developed in an independent branch available [here][support-slicer-extension]).

Then, in November 2018, in the context of an internship at [NIRAL][niral] (Neuro Image Research and Analysis Laboratories)
in the Department of Psychiatry at the University of North Carolina at Chapel Hill School of Medicine,  [Mateo Lopez][lopezmt] further improved the Slicer loadable module by improving the user interface, re-organizing files and renaming the
loadable module from `ShapeDistanceAnalyzer` to `MFSDA`.

Then, in 2019, [Juan Carlos Prieto][juanprietob] from [NIRAL][niral] added the script `MFSDA_selectVariablesPCA.py`
for performing the PCA of a set of variables and doing a correlation analysis with the N principal components.

Later, in 2019-2020, [Beatriz Paniagua][bpaniagua], [Jared Vicory][vicory], [Jean-Christophe Fillion-Robin][jcfr]
and [Sam Horvath][sjh26] from Kitware Inc. worked on improving the user interface and robustness, transitioning
to Python 3.x and revamping the build-system to support distribution as a Slicer extension.

[juanprietob]: https://github.com/juanprietob
[loic-michoud]: https://github.com/loic-michoud
[support-slicer-extension]: https://github.com/loic-michoud/MFSDA_Python/commits/SlicerExtension
[lopezmt]: https://github.com/lopezmt
[niral]: https://www.med.unc.edu/psych/research/niral/people-1/structural-and-dti-analysis-group/
[vicory]: https://github.com/vicory
[sjh26]: https://github.com/sjh26
[jcfr]: https://github.com/jcfr
[bpaniagua]: https://github.com/bpaniagua

