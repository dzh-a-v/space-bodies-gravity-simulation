#include "CollisionDetector.h"
#include <cmath>

namespace physics {

bool CollisionDetector::areColliding(const CelestialBody& body1, 
                                      const CelestialBody& body2) {
    double distance = body1.getPosition().distanceTo(body2.getPosition());
    double combinedRadius = body1.getRadius() + body2.getRadius();
    
    return distance <= combinedRadius;
}

std::vector<std::pair<size_t, size_t>> CollisionDetector::findCollisions(
    const std::vector<CelestialBody*>& bodies) {
    
    std::vector<std::pair<size_t, size_t>> collisions;
    
    for (size_t i = 0; i < bodies.size(); ++i) {
        if (bodies[i]->isDestroyed()) continue;
        
        for (size_t j = i + 1; j < bodies.size(); ++j) {
            if (bodies[j]->isDestroyed()) continue;
            
            if (areColliding(*bodies[i], *bodies[j])) {
                collisions.emplace_back(i, j);
            }
        }
    }
    
    return collisions;
}

double CollisionDetector::calculateRelativeVelocity(const CelestialBody& body1,
                                                     const CelestialBody& body2) {
    Vector3D relVelocity = body1.getVelocity() - body2.getVelocity();
    return relVelocity.magnitude();
}

} // namespace physics
