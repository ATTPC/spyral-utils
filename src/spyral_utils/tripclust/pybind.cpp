#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <vector>
#include "src/pointcloud.h"
#include "src/option.h"
#include "src/cluster.h"
#include "src/dnn.h"
#include "src/graph.h"
#include "src/postprocess.h"

namespace py = pybind11;

class tripclust {
private:
  Opt opt;
  PointCloud cloud_xyz;
  cluster_group cl_group;
  bool postprocess;
  int min_depth;

public:
  tripclust();
  void fill_pointcloud(py::array_t<double>);
  void perform_clustering();
  py::array_t<unsigned short> get_cluster(int);
  py::array_t<short> get_labels();
  int get_number_of_clusters();
  // neighbour distance for smoothing
  void set_r(const double value) {opt.r = value;}
  void set_rdnn(const bool value) {opt.rdnn = value;} // compute r with dnn
  // tested neighbours of triplet mid point
  void set_k(const size_t value) {opt.k = value;}
  // max number of triplets to one mid point
  void set_n(const size_t value) {opt.n = value;}
  // 1 - cos alpha, where alpha is the angle between the two triplet branches
  void set_a(const double value) {opt.a = value;}
  // distance scale factor in metric
  void set_s(const double value) {opt.s = value;}
  void set_sdnn(const bool value) {opt.sdnn = value;} // compute s with dnn
  // threshold for cdist in clustering
  void set_t(const double value) {opt.t = value;}
  void set_tauto(const bool value) {opt.tauto = value;} // auto generate t
  // maximum gap width
  void set_dmax(const double value) {opt.dmax = value;}
  void set_dmax_dnn(const bool value) {opt.dmax_dnn = value;} // use dnn for dmax
  void set_ordered(const bool value) {opt.ordered = value;} // points are in chronological order
  // linkage method for clustering
  void set_link(const Linkage value) {opt.link = value;}
  // min number of triplets per cluster
  void set_m(const size_t value) {opt.m = value;}
  // whether or not post processing should be enabled
  void set_postprocess(const bool value) {postprocess = value;}
  // minimum number of points making a branch in curve in post processing
  void set_min_depth(const int value) {min_depth = value;}
};

tripclust::tripclust() {
  Opt opt;
  PointCloud pc;
  cluster_group cg;
  this->opt = opt;
  this->cloud_xyz = pc;
  this->cl_group = cg;
  this->postprocess = false;
  this->min_depth = 25;
}

// Load cloud_xyz from numpy array
void tripclust::fill_pointcloud(py::array_t<double> arr) {
  py::buffer_info buf_info = arr.request();
  double *ptr = static_cast<double*>(buf_info.ptr);
  size_t ndim = buf_info.ndim;
  std::vector<ssize_t> shape = buf_info.shape;

  // The numpy array is assumed to be a 2D cloud array from Spyral
  for (size_t i = 0; i < shape[0]; i++) {
    Point point;
    point.x = ptr[i*shape[1]+0]; // x coordinate
    point.y = ptr[i*shape[1]+1]; // y coordinate
    point.z = ptr[i*shape[1]+2]; // z coordinate
    this->cloud_xyz.push_back(point);
  }
  // this->cloud.setOrdered(true);
  // this->cloud_xyz.set2d(false);
}

void tripclust::perform_clustering() {
  if (this->opt.needs_dnn()) {
    double dnn = std::sqrt(first_quartile(this->cloud_xyz));
    this->opt.set_dnn(dnn);
    if (dnn == 0.0) {
      return; // Need to throw some kind of error
    }
  }
  // Step 1) smoothing by position averaging of neighboring points
  PointCloud cloud_xyz_smooth;
  smoothen_cloud(this->cloud_xyz, cloud_xyz_smooth, this->opt.get_r());

  // Step 2) finding triplets of approximately collinear points
  std::vector<triplet> triplets;
  generate_triplets(cloud_xyz_smooth, triplets, this->opt.get_k(),
                    this->opt.get_n(), this->opt.get_a());

  // Step 3) single link hierarchical clustering of the triplets
  // cluster_group cl_group;
  compute_hc(cloud_xyz_smooth, this->cl_group, triplets, this->opt.get_s(),
             this->opt.get_t(), this->opt.is_tauto(), this->opt.get_dmax(),
             this->opt.is_dmax(), this->opt.get_linkage(), 0);

  // Step 4) pruning by removal of small clusters ...
  cleanup_cluster_group(this->cl_group, this->opt.get_m(), 0);
  cluster_triplets_to_points(triplets, this->cl_group);
  // .. and (optionally) by splitting up clusters at gaps > dmax
  if (this->opt.is_dmax()) {
    cluster_group cleaned_up_cluster_group;
    for (cluster_group::iterator cl = this->cl_group.begin(); cl != this->cl_group.end(); ++cl) {
      max_step(cleaned_up_cluster_group, *cl, this->cloud_xyz, this->opt.get_dmax(),
               this->opt.get_m() + 2);
    }
    this->cl_group = cleaned_up_cluster_group;
  }
  // store cluster labels in points
  add_clusters(this->cloud_xyz, this->cl_group, 0);
  // Step 5) Optionally perform post processing to find sub clusters
  if (this->postprocess) {
    int nchanged;
    nchanged = process_pointcloud(this->cloud_xyz, this->min_depth, 0);
  }
}

// Get an individual cluster array
py::array_t<unsigned short> tripclust::get_cluster(int clu) {
  std::vector<unsigned short> cluster;
  for (size_t i=0; i<this->cl_group[clu].size(); ++i)
    cluster.push_back(this->cl_group[clu][i]);
  return py::array_t<unsigned short>(cluster.size(), cluster.data());
}

// Get an array containing the cluster labels for each point
py::array_t<short> tripclust::get_labels() {
  std::vector<short> labels(this->cloud_xyz.size(), -1);
  for (size_t i=0; i<this->cloud_xyz.size(); ++i) {
    std::set<size_t>::iterator iterator=this->cloud_xyz[i].cluster_ids.begin();
    if (this->cloud_xyz[i].cluster_ids.size() > 0) labels[i] = *iterator; // Choose the first cluster id
  }
  //
  // for (size_t clu=0; clu<this->cl_group.size(); ++clu) {
  //   for (size_t i=0; i<this->cl_group[clu].size(); ++i) {
  //     labels[this->cl_group[clu][i]] = clu;
  //   }
  // }
  return py::array_t<short>(labels.size(), labels.data());
}

// Get the number of clusters
int tripclust::get_number_of_clusters(){
  int nclu = 0;
  std::vector<bool> test(this->cloud_xyz.size(), false);
  for (size_t i=0; i<this->cloud_xyz.size(); ++i) {
    for (std::set<size_t>::iterator j=this->cloud_xyz[i].cluster_ids.begin(); j!=this->cloud_xyz[i].cluster_ids.end(); ++j)
      test[*j] = true;
  }
  for (size_t i=0; i<test.size(); ++i) if (test[i]) nclu++;
  return nclu;
  // return this->cl_group.size();
}

PYBIND11_MODULE(tripclust, m, py::mod_gil_not_used()) {
  py::class_<tripclust>(m, "tripclust")
    .def(py::init())
    .def("fill_pointcloud", &tripclust::fill_pointcloud, "Fills point cloud")
    .def("perform_clustering", &tripclust::perform_clustering, "Performs the tripclust clustering")
    .def("get_number_of_clusters", &tripclust::get_number_of_clusters, "Get the number of clusters")
    .def("get_cluster", &tripclust::get_cluster, "Retrieves individual cluster")
    .def("get_labels", &tripclust::get_labels, "Returns an array containing the label for each point")
    .def("set_r", &tripclust::set_r, "neighbour distance for smoothing")
    .def("set_rdnn", &tripclust::set_rdnn, "compute r with dnn")
    .def("set_k", &tripclust::set_k, "tested neighbours of triplet mid point")
    .def("set_n", &tripclust::set_n, "max number of triplets to one mid point")
    .def("set_a", &tripclust::set_a, "1 - cos alpha, where alpha is the angle between the two triplet branches")
    .def("set_s", &tripclust::set_s, "distance scale factor in metric")
    .def("set_sdnn", &tripclust::set_sdnn, "compute s with dnn")
    .def("set_t", &tripclust::set_t, "threshold for cdist in clustering")
    .def("set_tauto", &tripclust::set_tauto, "auto generate t")
    .def("set_dmax", &tripclust::set_dmax, "maximum gap width")
    .def("set_dmax_dnn", &tripclust::set_dmax_dnn, "use dnn for dmax")
    .def("set_ordered", &tripclust::set_ordered, "points are in chronological order")
    .def("set_link", &tripclust::set_link, "linkage method for clustering")
    .def("set_m", &tripclust::set_m, "min number of triplets per cluster")
    .def("set_postprocess", &tripclust::set_postprocess, "whether or not post processing should be enabled")
    .def("set_min_depth", &tripclust::set_min_depth, "minimum number of points making a branch in curve in post processing");
}
