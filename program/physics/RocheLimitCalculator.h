#pragma once

#include "CelestialBody.h"
#include <vector>

namespace physics {

/**
 * @brief Calculates Roche limit and tracks time satellites spend inside it
 * 
 * Roche limit formula:
 * d_Roche = 2.9 * R_primary * cbrt(ρ_primary / ρ_satellite)
 * 
 * Destruction occurs only after >= 24 hours inside the limit.
 */
class RocheLimitCalculator {
public:
    /**
     * @brief Calculate Roche limit distance for a satellite around a primary body
     * @param primary The primary (larger) body
     * @param satellite The satellite (smaller) body
     * @return Roche limit distance in meters
     */
    static double calculateRocheLimit(const CelestialBody& primary, 
                                      const CelestialBody& satellite);

    /**
     * @brief Check if a satellite is inside the Roche limit of a primary
     * @param primary The primary body
     * @param satellite The satellite body
     * @return true if distance < Roche limit
     */
    static bool isInsideRocheLimit(const CelestialBody& primary,
                                   const CelestialBody& satellite);

    /**
     * @brief Find all satellites inside their respective Roche limits
     * @param bodies All bodies in the system
     * @return Vector of body indices that are inside a Roche limit
     */
    static std::vector<size_t> findBodiesInsideRocheLimit(
        const std::vector<CelestialBody*>& bodies);

    /**
     * @brief Check if a body should be destroyed (spent enough time inside Roche limit)
     * @param body The body to check
     * @return true if body should fragment due to Roche limit
     */
    static bool shouldDestroyByRocheLimit(const CelestialBody& body);
};

} // namespace physics
