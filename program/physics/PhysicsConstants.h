#pragma once

// Define M_PI for MSVC before including cmath
#ifndef _USE_MATH_DEFINES
#define _USE_MATH_DEFINES
#endif

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#include <cmath>

namespace physics {

/// Gravitational constant in m³/(kg·s²)
constexpr double G = 6.67430e-11;

/// Minimum mass for objects (kg) - 0.1 Lunar masses
constexpr double MIN_MASS = 1e15;

/// Maximum mass for objects (kg) - 100 Solar masses
constexpr double MAX_MASS = 1e26;

/// Minimum radius for objects (m) - 0.1 Lunar radii
constexpr double MIN_RADIUS = 1e3;

/// Maximum radius for objects (m) - 10 Solar radii
constexpr double MAX_RADIUS = 2.0e7;

/// Maximum number of objects in simulation
constexpr int MAX_OBJECTS = 100000;

/// Minimum mass for fragmentation (kg)
constexpr double MIN_FRAGMENTATION_MASS = 2e15;

/// Minimum fragments per destruction event
constexpr int MIN_FRAGMENTS = 2;

/// Maximum fragments per destruction event
constexpr int MAX_FRAGMENTS = 100;

/// Maximum total objects (hard limit)
constexpr int MAX_TOTAL_OBJECTS = 10000;

/// Roche limit coefficient
constexpr double ROCHE_COEFFICIENT = 2.9;

/// Time inside Roche limit before destruction (seconds) - 24 hours
constexpr double ROCHE_DESTRUCTION_TIME = 24.0 * 3600.0;

/// Mass ratio threshold for guaranteed merge
constexpr double MERGE_RATIO_THRESHOLD = 1.0 / 100.0;

/// Mass ratio threshold for probabilistic merge/destroy
constexpr double PROBABILISTIC_RATIO_THRESHOLD = 1.0 / 10.0;

} // namespace physics
