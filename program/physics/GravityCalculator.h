#pragma once

#include "Vector3D.h"
#include "CelestialBody.h"
#include <vector>

namespace physics {

/**
 * @brief Calculates gravitational forces between celestial bodies
 */
class GravityCalculator {
public:
    /**
     * @brief Calculate gravitational acceleration on body1 due to body2
     * @param body1 The body experiencing the force
     * @param body2 The body causing the force
     * @return Acceleration vector on body1 (m/s²)
     */
    static Vector3D calculateAcceleration(const CelestialBody& body1, 
                                          const CelestialBody& body2);

    /**
     * @brief Calculate gravitational force between two bodies
     * @param body1 First body
     * @param body2 Second body
     * @return Force vector on body1 (N)
     */
    static Vector3D calculateForce(const CelestialBody& body1, 
                                   const CelestialBody& body2);

    /**
     * @brief Calculate total gravitational acceleration on a body from all other bodies
     * @param body The body experiencing forces
     * @param allBodies All bodies in the system
     * @return Total acceleration vector (m/s²)
     */
    static Vector3D calculateTotalAcceleration(const CelestialBody& body,
                                               const std::vector<CelestialBody*>& allBodies);
};

} // namespace physics
