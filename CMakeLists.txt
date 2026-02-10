cmake_minimum_required(VERSION 3.15...4.0)
project(tripclust LANGUAGES CXX)

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)

find_package (Eigen3 REQUIRED)
include_directories(${EIGEN3_INCLUDE_DIR})

pybind11_add_module(tripclust src/spyral_utils/tripclust/pybind.cpp src/spyral_utils/tripclust/src/postprocess.cpp src/spyral_utils/tripclust/src/directedgraph.cpp src/spyral_utils/tripclust/src/orthogonallsq.cpp src/spyral_utils/tripclust/src/pointcloud.cpp src/spyral_utils/tripclust/src/option.cpp src/spyral_utils/tripclust/src/cluster.cpp src/spyral_utils/tripclust/src/dnn.cpp src/spyral_utils/tripclust/src/graph.cpp src/spyral_utils/tripclust/src/triplet.cpp src/spyral_utils/tripclust/src/util.cpp src/spyral_utils/tripclust/src/hclust/fastcluster.cpp src/spyral_utils/tripclust/src/kdtree/kdtree.cpp)
install(TARGETS tripclust DESTINATION .)
