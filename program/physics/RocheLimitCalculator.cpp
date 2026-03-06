#include "RocheLimitCalculator.h"
#include "PhysicsConstants.h"
#include <cmath>
#include <algorithm>

namespace physics {

double RocheLimitCalculator::calculateRocheLimit(const CelestialBody& primary,
                                                  const CelestialBody& satellite) {
    double primaryDensity = primary.getDensity();
    double satelliteDensity = satellite.getDensity();
    
    if (primaryDensity <= 0.0 || satelliteDensity <= 0.0) {
        return 0.0;
    }
    
    // d_Roche = 2.9 * R_primary * cbrt(ρ_primary / ρ_satellite)
    double densityRatio = primaryDensity / satelliteDensity;
    return ROCHE_COEFFICIENT * primary.getRadius() * std::cbrt(densityRatio);
}

bool RocheLimitCalculator::isInsideRocheLimit(const CelestialBody& primary,
                                               const CelestialBody& satellite) {
    double distance = primary.getPosition().distanceTo(satellite.getPosition());
    double rocheLimit = calculateRocheLimit(primary, satellite);
    
    return distance < rocheLimit && rocheLimit > 0.0;
}

std::vector<size_t> RocheLimitCalculator::findBodiesInsideRocheLimit(
    const std::vector<CelestialBody*>& bodies) {
    
    std::vector<size_t> insideRoche;
    
    for (size_t i = 0; i < bodies.size(); ++i) {
        if (bodies[i]->isDestroyed() || !bodies[i]->canFragment()) {
            continue;
        }
        
        // Find the most massive body that could be the primary
        for (size_t j = 0; j < bodies.size(); ++j) {
            if (i == j || bodies[j]->isDestroyed()) {
                continue;
            }
            
            // Only check if body[j] is significantly more massive (potential primary)
            if (bodies[j]->getMass() > bodies[i]->getMass() * 10) {
                if (isInsideRocheLimit(*bodies[j], *bodies[i])) {
                    insideRoche.push_back(i);
                    break;  // Only need to find one primary
                }
            }
        }
    }
    
    return insideRoche;
}

bool RocheLimitCalculator::shouldDestroyByRocheLimit(const CelestialBody& body) {
    // Destruction only occurs after >= 24 hours inside Roche limit
    return body.getTimeInsideRocheLimit() >= ROCHE_DESTRUCTION_TIME 
           && body.canFragment()
           && body.getMass() >= MIN_FRAGMENTATION_MASS;
}

} // namespace physics
