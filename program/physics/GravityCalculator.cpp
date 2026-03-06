#include "GravityCalculator.h"
#include "PhysicsConstants.h"
#include <cmath>

namespace physics {

Vector3D GravityCalculator::calculateAcceleration(const CelestialBody& body1,
                                                   const CelestialBody& body2) {
    Vector3D r = body2.getPosition() - body1.getPosition();
    double distanceSquared = r.magnitudeSquared();
    
    if (distanceSquared <= 0.0) {
        return Vector3D();  // Bodies at same position, undefined force
    }
    
    double distance = std::sqrt(distanceSquared);
    
    // F = G * m1 * m2 / r²
    // a = F / m1 = G * m2 / r²
    double accelerationMagnitude = G * body2.getMass() / distanceSquared;
    
    // Direction is toward body2 (normalized r)
    Vector3D direction = r.normalized();
    
    return direction * accelerationMagnitude;
}

Vector3D GravityCalculator::calculateForce(const CelestialBody& body1,
                                            const CelestialBody& body2) {
    Vector3D r = body2.getPosition() - body1.getPosition();
    double distanceSquared = r.magnitudeSquared();
    
    if (distanceSquared <= 0.0) {
        return Vector3D();
    }
    
    double distance = std::sqrt(distanceSquared);
    
    // F = G * m1 * m2 / r²
    double forceMagnitude = G * body1.getMass() * body2.getMass() / distanceSquared;
    
    Vector3D direction = r.normalized();
    
    return direction * forceMagnitude;
}

Vector3D GravityCalculator::calculateTotalAcceleration(const CelestialBody& body,
                                                        const std::vector<CelestialBody*>& allBodies) {
    Vector3D totalAcceleration;
    
    for (const auto* otherBody : allBodies) {
        if (otherBody != &body && !otherBody->isDestroyed()) {
            totalAcceleration += calculateAcceleration(body, *otherBody);
        }
    }
    
    return totalAcceleration;
}

} // namespace physics
