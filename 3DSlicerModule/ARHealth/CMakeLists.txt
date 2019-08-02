cmake_minimum_required(VERSION 3.5)

project(ARHealth)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/ARHealth")
set(EXTENSION_CATEGORY "AR Registration")
set(EXTENSION_CONTRIBUTORS "Rafael Moreta (Harvard Medical School), David Garcia (Universidad Carlos III de Madrid)")
set(EXTENSION_DESCRIPTION "This is an example of a simple extension")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/ARHealth.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/ARHealth/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(ARHealth)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
