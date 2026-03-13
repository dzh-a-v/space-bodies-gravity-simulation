#include "CollisionDetector.h"
#include <cmath>

namespace physics {

bool CollisionDetector::areColliding(const CelestialBody& body1, 
                                      const CelestialBody& body2) {
    double distance = body1.getPosition().distanceTo(body2.getPosition());
    double combinedRadius = body1.getRadius() + body2.getRadius();
    
    return distance <= combinedRadius;
}

bool CollisionDetector::areApproaching(const CelestialBody& body1,
                                        const CelestialBody& body2) {
    // Vector from body1 to body2
    Vector3D r = body2.getPosition() - body1.getPosition();
    
    // Relative velocity
    Vector3D vRel = body2.getVelocity() - body1.getVelocity();
    
    // If dot product of r and vRel is negative, they're approaching
    // (distance is decreasing)
    double dot = r.dot(vRel);
    return dot < 0;
}

std::vector<CollisionEvent> CollisionDetector::findCollisions(
    const std::vector<CelestialBody*>& bodies) {
    
    std::vector<CollisionEvent> events;
    
    for (size_t i = 0; i < bodies.size(); ++i) {
        if (bodies[i]->isDestroyed()) continue;
        
        for (size_t j = i + 1; j < bodies.size(); ++j) {
            if (bodies[j]->isDestroyed()) continue;
            
            double distance = bodies[i]->getPosition().distanceTo(bodies[j]->getPosition());
            double combinedRadius = bodies[i]->getRadius() + bodies[j]->getRadius();
            double relVelocity = calculateRelativeVelocity(*bodies[i], *bodies[j]);
            bool approaching = areApproaching(*bodies[i], *bodies[j]);
            
            CollisionEvent event;
            event.bodyIdx1 = i;
            event.bodyIdx2 = j;
            event.distance = distance;
            event.combinedRadius = combinedRadius;
            event.relativeVelocity = relVelocity;
            event.isApproaching = approaching;
            event.isContact = (distance <= combinedRadius);
            event.isNearContact = (distance <= combinedRadius * 1.1) && approaching;
            
            // Only report if contacting or very close and approaching
            if (event.isContact || event.isNearContact) {
                events.push_back(event);
            }
        }
    }
    
    return events;
}

double CollisionDetector::calculateRelativeVelocity(const CelestialBody& body1,
                                                     const CelestialBody& body2) {
    Vector3D relVelocity = body1.getVelocity() - body2.getVelocity();
    return relVelocity.magnitude();
}

} // namespace physics
