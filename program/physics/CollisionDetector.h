#pragma once

#include "CelestialBody.h"
#include <vector>
#include <utility>

namespace physics {

/**
 * @brief Detected collision or near-collision event
 */
struct CollisionEvent {
    size_t bodyIdx1;
    size_t bodyIdx2;
    double distance;          // Current distance between centers
    double combinedRadius;    // R1 + R2
    double relativeVelocity;  // |v1 - v2|
    bool isApproaching;       // Are bodies getting closer?
    bool isContact;           // Are bodies actually touching?
    bool isNearContact;       // Are bodies very close (within 10% of combined radius)?
};

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
     * @return Vector of CollisionEvent structures
     */
    static std::vector<CollisionEvent> findCollisions(
        const std::vector<CelestialBody*>& bodies);

    /**
     * @brief Calculate relative velocity between two bodies
     * @param body1 First body
     * @param body2 Second body
     * @return |v1 - v2| (m/s)
     */
    static double calculateRelativeVelocity(const CelestialBody& body1,
                                            const CelestialBody& body2);

    /**
     * @brief Check if bodies are approaching each other
     * @param body1 First body
     * @param body2 Second body
     * @return true if distance is decreasing
     */
    static bool areApproaching(const CelestialBody& body1, const CelestialBody& body2);
};

} // namespace physics
