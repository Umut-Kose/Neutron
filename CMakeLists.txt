cmake_minimum_required(VERSION 3.5 FATAL_ERROR)
project(AmBeSim)

option(WITH_GEANT4_UIVIS "Build example with Geant4 UI and Vis drivers" ON)
if(WITH_GEANT4_UIVIS)
  find_package(Geant4 REQUIRED gdml ui_all vis_all)
else()
  find_package(Geant4 REQUIRED gdml)
endif()

include(${Geant4_USE_FILE})
include_directories(${PROJECT_SOURCE_DIR}/include)

# Explicitly check if source directories exist
if(NOT EXISTS ${PROJECT_SOURCE_DIR}/src)
  file(MAKE_DIRECTORY ${PROJECT_SOURCE_DIR}/src)
endif()

if(NOT EXISTS ${PROJECT_SOURCE_DIR}/include)
  file(MAKE_DIRECTORY ${PROJECT_SOURCE_DIR}/include)
endif()

# Find source files
file(GLOB sources ${PROJECT_SOURCE_DIR}/src/*.cc)
file(GLOB headers ${PROJECT_SOURCE_DIR}/include/*.hh)

add_executable(AmBeSim 
    ${PROJECT_SOURCE_DIR}/main.cc 
    ${sources} 
    ${headers}
)
target_link_libraries(AmBeSim ${Geant4_LIBRARIES})
