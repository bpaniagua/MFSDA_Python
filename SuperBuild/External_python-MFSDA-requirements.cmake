set(proj python-MFSDA-requirements)

# Set dependency list
set(${proj}_DEPENDENCIES "")
if(Slicer_SOURCE_DIR)
  set(${proj}_DEPENDENCIES
    python
    python-numpy
    python-pip
    python-scipy
    python-setuptools
    python-wheel
    )
endif()

if(NOT DEFINED Slicer_USE_SYSTEM_${proj})
  set(Slicer_USE_SYSTEM_${proj} ${Slicer_USE_SYSTEM_python})
endif()

# Include dependent projects if any
ExternalProject_Include_Dependencies(${proj} PROJECT_VAR proj DEPENDS_VAR ${proj}_DEPENDENCIES)

if(Slicer_USE_SYSTEM_${proj})
  foreach(module_name IN ITEMS
      dateutil
      numpy
      patsy
      pytz
      pandas
      scipy
      statsmodels
      )
    ExternalProject_FindPythonPackage(
      MODULE_NAME "${module_name}"
      REQUIRED
      )
  endforeach()
endif()

if(NOT Slicer_USE_SYSTEM_${proj})

  set(requirements_file ${CMAKE_BINARY_DIR}/${proj}-requirements.txt)
  file(WRITE ${requirements_file} [===[
  # Hashes correspond to the following packages:
  # - python_dateutil-2.8.1-py2.py3-none-any.whl
  python-dateutil==2.8.1 --hash=sha256:75bb3f31ea686f1197762692a9ee6a7550b59fc6ca3a1f4b5d7e32fb98e2da2a
  # Hashes correspond to the following packages:
  # - pytz-2020.1-py2.py3-none-any.whl
  pytz==2020.1 --hash=sha256:a494d53b6d39c3c6e44c3bec237336e14305e4f29bbf800b599253057fbb79ed
  # Hashes correspond to the following packages:
  # - pandas-1.0.5-cp36-cp36m-win_amd64.whl 
  # - pandas-1.0.5-cp36-cp36m-macosx_10_9_x86_64.whl
  # - pandas-1.0.5-cp36-cp36m-manylinux1_x86_64.whl
  pandas==1.0.5 --hash=sha256:35b670b0abcfed7cad76f2834041dcf7ae47fd9b22b63622d67cdc933d79f453 \
                --hash=sha256:faa42a78d1350b02a7d2f0dbe3c80791cf785663d6997891549d0f86dc49125e \
                --hash=sha256:8778a5cc5a8437a561e3276b85367412e10ae9fff07db1eed986e427d9a674f8
  # Hashes correspond to the following packages:
  # - patsy-0.5.1-py2.py3-none-any.whl
  patsy==0.5.1 --hash=sha256:5465be1c0e670c3a965355ec09e9a502bf2c4cbe4875e8528b0221190a8a5d40
  # Hashes correspond to the following packages:
  # - statsmodels-0.11.1-cp36-none-win_amd64.whl
  # - statsmodels-0.11.1-cp36-cp36m-macosx_10_13_x86_64.whl
  # - statsmodels-0.11.1-cp36-cp36m-manylinux1_x86_64.whl
  statsmodels==0.11.1 --hash=sha256:49aa8ffbe0b0e2e86afa58dec6bd5c483898e9b8223d8a7d13b69b5ad144b674 \
                      --hash=sha256:5e7afc596164c1c7464ba3943721a9668aa0ce07853ce9881ac49d3a043784dd \
                      --hash=sha256:9efd2e27c08077330cecdbfb589cf84d735abface94e9a6387282a6a7c91362d
  ]===])

  set(pip_install_args)

  if(NOT Slicer_SOURCE_DIR)
    # Alternative python prefix for installing extension python packages
    set(python_packages_DIR "${CMAKE_BINARY_DIR}/python-packages-install")

    # Convert to native path to satisfy pip install command
    file(TO_NATIVE_PATH ${python_packages_DIR} python_packages_DIR_NATIVE_DIR)

    # Escape command argument for pip install command
    string(REGEX REPLACE "\\\\" "\\\\\\\\" python_packages_DIR_NATIVE_DIR "${python_packages_DIR_NATIVE_DIR}")

    list(APPEND pip_install_args
      --prefix ${python_packages_DIR_NATIVE_DIR}
      )
  endif()

  ExternalProject_Add(${proj}
    ${${proj}_EP_ARGS}
    DOWNLOAD_COMMAND ""
    SOURCE_DIR ${CMAKE_BINARY_DIR}/${proj}
    BUILD_IN_SOURCE 1
    CONFIGURE_COMMAND ""
    BUILD_COMMAND ""
    INSTALL_COMMAND ${PYTHON_EXECUTABLE} -m pip install --require-hashes -r ${requirements_file} ${pip_install_args}
    LOG_INSTALL 1
    DEPENDS
      ${${proj}_DEPENDENCIES}
    )

  ExternalProject_GenerateProjectDescription_Step(${proj}
    VERSION ${_version}
    )

  #-----------------------------------------------------------------------------
  # Launcher setting specific to build tree
  if(NOT Slicer_SOURCE_DIR)
    set(${proj}_PYTHONPATH_LAUNCHER_BUILD
      ${python_packages_DIR}/${PYTHON_STDLIB_SUBDIR}
      ${python_packages_DIR}/${PYTHON_STDLIB_SUBDIR}/lib-dynload
      ${python_packages_DIR}/${PYTHON_SITE_PACKAGES_SUBDIR}
      )
    mark_as_superbuild(
      VARS ${proj}_PYTHONPATH_LAUNCHER_BUILD
      LABELS "PYTHONPATH_LAUNCHER_BUILD"
      )

    mark_as_superbuild(python_packages_DIR:PATH)
  endif()

else()
  ExternalProject_Add_Empty(${proj} DEPENDS ${${proj}_DEPENDENCIES})
endif()
