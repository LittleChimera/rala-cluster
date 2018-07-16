cmake_minimum_required(VERSION 3.2)
project(rala-cluster)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/lib)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/bin)

set(ALLOW_DUPLICATE_CUSTOM_TARGETS TRUE)

add_custom_target(minimap2 ALL
    COMMAND make
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/vendor/minimap2)
add_custom_target(mcl ALL
    COMMAND ./configure && make
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/vendor/mcl)
add_custom_target(ezra ALL
    COMMAND cmake . && make
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/vendor/ezra)
add_custom_target(rala ALL
    COMMAND cmake . && make
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}/vendor/rala)

set(minimap_path ${PROJECT_SOURCE_DIR}/vendor/minimap2/minimap2)
set(rala_path ${PROJECT_BINARY_DIR}/vendor/rala/bin/rala)
