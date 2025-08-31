cmake_minimum_required(VERSION 3.15...4.0)
project(tripclust LANGUAGES CXX)

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)

find_package (Eigen3 REQUIRED)
include_directories(${EIGEN3_INCLUDE_DIR})

pybind11_add_module(tripclust pybind.cpp src/postprocess.cpp src/directedgraph.cpp src/orthogonallsq.cpp src/pointcloud.cpp src/option.cpp src/cluster.cpp src/dnn.cpp src/graph.cpp src/triplet.cpp src/util.cpp src/hclust/fastcluster.cpp src/kdtree/kdtree.cpp)
install(TARGETS tripclust DESTINATION .)
