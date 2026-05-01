#include <cmath>
#include <stdexcept>

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

using ArrayD = py::array_t<double, py::array::c_style | py::array::forcecast>;

py::array_t<double> compute_accelerations(ArrayD masses_array, ArrayD positions_array, double g) {
    auto masses = masses_array.unchecked<1>();
    auto positions = positions_array.unchecked<2>();

    if (positions.shape(0) != masses.shape(0) || positions.shape(1) != 3) {
        throw std::invalid_argument("masses must be (N,) and positions must be (N, 3)");
    }

    const py::ssize_t n = masses.shape(0);
    py::array_t<double> accelerations_array({n, static_cast<py::ssize_t>(3)});
    auto accelerations = accelerations_array.mutable_unchecked<2>();

    for (py::ssize_t i = 0; i < n; ++i) {
        accelerations(i, 0) = 0.0;
        accelerations(i, 1) = 0.0;
        accelerations(i, 2) = 0.0;
    }

    for (py::ssize_t i = 0; i < n; ++i) {
        for (py::ssize_t j = i + 1; j < n; ++j) {
            const double dx = positions(j, 0) - positions(i, 0);
            const double dy = positions(j, 1) - positions(i, 1);
            const double dz = positions(j, 2) - positions(i, 2);
            const double distance_squared = dx * dx + dy * dy + dz * dz;
            if (distance_squared == 0.0) {
                continue;
            }

            const double distance_cubed = distance_squared * std::sqrt(distance_squared);
            const double left_factor = g * masses(j) / distance_cubed;
            const double right_factor = g * masses(i) / distance_cubed;

            accelerations(i, 0) += left_factor * dx;
            accelerations(i, 1) += left_factor * dy;
            accelerations(i, 2) += left_factor * dz;

            accelerations(j, 0) -= right_factor * dx;
            accelerations(j, 1) -= right_factor * dy;
            accelerations(j, 2) -= right_factor * dz;
        }
    }

    return accelerations_array;
}

py::tuple step_exact(
    ArrayD masses_array,
    ArrayD positions_array,
    ArrayD velocities_array,
    double dt,
    double g
) {
    auto masses = masses_array.unchecked<1>();
    auto positions = positions_array.unchecked<2>();
    auto velocities = velocities_array.unchecked<2>();

    if (
        positions.shape(0) != masses.shape(0) ||
        velocities.shape(0) != masses.shape(0) ||
        positions.shape(1) != 3 ||
        velocities.shape(1) != 3
    ) {
        throw std::invalid_argument("masses must be (N,), positions and velocities must be (N, 3)");
    }

    const py::ssize_t n = masses.shape(0);
    py::array_t<double> old_accelerations_array = compute_accelerations(masses_array, positions_array, g);
    auto old_accelerations = old_accelerations_array.unchecked<2>();

    py::array_t<double> next_positions_array({n, static_cast<py::ssize_t>(3)});
    auto next_positions = next_positions_array.mutable_unchecked<2>();

    for (py::ssize_t i = 0; i < n; ++i) {
        for (py::ssize_t axis = 0; axis < 3; ++axis) {
            next_positions(i, axis) =
                positions(i, axis) + velocities(i, axis) * dt + 0.5 * old_accelerations(i, axis) * dt * dt;
        }
    }

    py::array_t<double> new_accelerations_array = compute_accelerations(masses_array, next_positions_array, g);
    auto new_accelerations = new_accelerations_array.unchecked<2>();

    py::array_t<double> next_velocities_array({n, static_cast<py::ssize_t>(3)});
    auto next_velocities = next_velocities_array.mutable_unchecked<2>();

    for (py::ssize_t i = 0; i < n; ++i) {
        for (py::ssize_t axis = 0; axis < 3; ++axis) {
            next_velocities(i, axis) =
                velocities(i, axis) + 0.5 * (old_accelerations(i, axis) + new_accelerations(i, axis)) * dt;
        }
    }

    return py::make_tuple(next_positions_array, next_velocities_array, new_accelerations_array);
}

PYBIND11_MODULE(_cpp_backend, module) {
    module.doc() = "Exact Newtonian gravity backend for gravity_sim";
    module.def("compute_accelerations", &compute_accelerations);
    module.def("step_exact", &step_exact);
}
