cmake_minimum_required(VERSION 3.13.4)

project(MFSDA)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "")
set(EXTENSION_CATEGORY "Statistics")
set(EXTENSION_CONTRIBUTORS "Mateo Lopez (University of North Carolina), Juan Carlos Prieto (University of North Carolina) ")
set(EXTENSION_DESCRIPTION " ")
set(EXTENSION_ICONURL "")
set(EXTENSION_SCREENSHOTURLS "")
set(EXTENSION_DEPENDS )

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(MFSDA)
## NEXT_MODULE


#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
