cmake_minimum_required(VERSION 3.13.4)

project(MFSDA)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/DCBIA-OrthoLab/MFSDA_Python#readme")
set(EXTENSION_CATEGORY "Statistics")
set(EXTENSION_CONTRIBUTORS "Mateo Lopez (University of North Carolina), Juan Carlos Prieto (University of North Carolina) ")
set(EXTENSION_DESCRIPTION "Modules for statistical shape analysis. A multivariate varying coefficient model is introduced to build the association between the multivariate shape measurements and demographic information and other clinical variables. Statistical inference, i.e., hypothesis testing, is also included in this package, which can be used in investigating whether some covariates of interest are significantly associated with the shape information. The hypothesis testing results are further used in clustering based analysis.")
set(EXTENSION_ICONURL "")
set(EXTENSION_SCREENSHOTURLS "")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies)

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(MFSDA)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})

