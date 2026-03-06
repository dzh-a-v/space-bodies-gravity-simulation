#pragma once

#include "CelestialBody.h"
#include <vector>
#include <utility>

namespace physics {

/**
 * @brief Detects collisions between celestial bodies
 */
class CollisionDetector {
public:
    /**
     * @brief Check if two bodies are in contact (collision)
     * @param body1 First body
     * @param body2 Second body
     * @return true if distance <= R1 + R2
     */
    static bool areColliding(const CelestialBody& body1, const CelestialBody& body2);

    /**
     * @brief Find all colliding pairs in the system
     * @param bodies All bodies to check
     * @return Vector of pairs (indices of colliding bodies)
     */
    static std::vector<std::pair<size_t, size_t>> findCollisions(
        const std::vector<CelestialBody*>& bodies);

    /**
     * @brief Calculate relative velocity between two bodies
     * @param body1 First body
     * @param body2 Second body
     * @return |v1 - v2| (m/s)
     */
    static double calculateRelativeVelocity(const CelestialBody& body1, 
                                            const CelestialBody& body2);
};

} // namespace physics
