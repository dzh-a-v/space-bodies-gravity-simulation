#include "CollisionResolver.h"
#include "CollisionDetector.h"
#include "PhysicsConstants.h"
#include <algorithm>

namespace physics {

CollisionResolver::CollisionResolver() 
    : m_fragmentCount(10)  // Default fragment count
    , m_rng(std::random_device{}())
{
}

void CollisionResolver::setFragmentCount(int fragments) {
    m_fragmentCount = std::clamp(fragments, MIN_FRAGMENTS, MAX_FRAGMENTS);
}

double CollisionResolver::calculateMassRatio(const CelestialBody& body1,
                                              const CelestialBody& body2) {
    double minMass = std::min(body1.getMass(), body2.getMass());
    double maxMass = std::max(body1.getMass(), body2.getMass());
    
    if (maxMass <= 0.0) {
        return 1.0;
    }
    
    return minMass / maxMass;
}

double CollisionResolver::calculateEscapeVelocity(const CelestialBody& body1,
                                                   const CelestialBody& body2) {
    // Use the smaller body's escape velocity
    const CelestialBody* smallerBody = (body1.getMass() < body2.getMass()) 
                                        ? &body1 : &body2;
    return smallerBody->getEscapeVelocity();
}

CollisionResult CollisionResolver::resolve(const CelestialBody& body1,
                                            const CelestialBody& body2,
                                            int currentObjectCount) {
    double massRatio = calculateMassRatio(body1, body2);
    double relVelocity = CollisionDetector::calculateRelativeVelocity(body1, body2);
    double escapeVel = calculateEscapeVelocity(body1, body2);
    
    // Find indices (assume idx1 < idx2 for consistency)
    // These will be set by the caller in SimulationEngine
    
    if (massRatio < MERGE_RATIO_THRESHOLD) {
        // Always merge when mass ratio < 1/100
        // The smaller body merges into the larger one
        return createMerge(body1, body2, 0, 1);
    }
    else if (massRatio < PROBABILISTIC_RATIO_THRESHOLD) {
        // Probabilistic: probability of fragmentation proportional to mass ratio
        // P(fragment) = (ratio - 1/100) / (1/10 - 1/100) = (ratio - 0.01) / 0.09
        std::uniform_real_distribution<double> dist(0.0, 1.0);
        double fragmentProb = (massRatio - MERGE_RATIO_THRESHOLD) / 
                              (PROBABILISTIC_RATIO_THRESHOLD - MERGE_RATIO_THRESHOLD);
        
        if (dist(m_rng) < fragmentProb) {
            return createFragments(body1, body2, 0, 1, currentObjectCount);
        } else {
            return createMerge(body1, body2, 0, 1);
        }
    }
    else {
        // Mass ratio >= 1/10: depends on relative velocity
        if (relVelocity > escapeVel) {
            return createFragments(body1, body2, 0, 1, currentObjectCount);
        } else {
            return createMerge(body1, body2, 0, 1);
        }
    }
}

CollisionResult CollisionResolver::createMerge(const CelestialBody& body1,
                                                const CelestialBody& body2,
                                                size_t idx1, size_t idx2) {
    CollisionResult result;
    result.type = CollisionResult::MERGE;
    result.bodyToRemove1 = idx1;
    result.bodyToRemove2 = idx2;
    result.mergedBodyIndex = idx1;  // Store result in first body's position
    
    // Conservation of momentum: (m1*v1 + m2*v2) / (m1 + m2)
    double totalMass = body1.getMass() + body2.getMass();
    Vector3D totalMomentum = body1.getVelocity() * body1.getMass() 
                           + body2.getVelocity() * body2.getMass();
    Vector3D newVelocity = totalMomentum / totalMass;
    
    // Conservation of volume (assuming same density): V = V1 + V2
    // r_new = (r1³ + r2³)^(1/3)
    double newRadius = std::cbrt(std::pow(body1.getRadius(), 3) 
                               + std::pow(body2.getRadius(), 3));
    
    // Position: center of mass
    Vector3D newPos = (body1.getPosition() * body1.getMass() 
                     + body2.getPosition() * body2.getMass()) / totalMass;
    
    // Create merged body (will be applied by SimulationEngine)
    auto mergedBody = std::make_unique<CelestialBody>(
        body1.getName(),  // Keep the larger body's name (or could combine)
        totalMass,
        newRadius,
        newPos,
        newVelocity,
        Vector3D()  // Acceleration will be recalculated
    );
    
    // Preserve fragment capability from the larger body
    const CelestialBody* largerBody = (body1.getMass() >= body2.getMass()) 
                                       ? &body1 : &body2;
    mergedBody->setCanFragment(largerBody->canFragment());
    
    result.newBodies.push_back(std::move(mergedBody));
    
    return result;
}

CollisionResult CollisionResolver::createFragments(const CelestialBody& body1,
                                                    const CelestialBody& body2,
                                                    size_t idx1, size_t idx2,
                                                    int currentObjectCount) {
    CollisionResult result;
    result.type = CollisionResult::FRAGMENT;
    result.bodyToRemove1 = idx1;
    result.bodyToRemove2 = idx2;
    
    // Check if fragmentation is allowed
    double totalMass = body1.getMass() + body2.getMass();
    
    // Only fragment if total mass >= MIN_FRAGMENTATION_MASS
    if (totalMass < MIN_FRAGMENTATION_MASS) {
        // Fall back to merge
        return createMerge(body1, body2, idx1, idx2);
    }
    
    // Calculate how many fragments we can create
    int maxNewObjects = MAX_TOTAL_OBJECTS - currentObjectCount + 2;  // +2 because we remove 2
    int actualFragments = std::min(m_fragmentCount, maxNewObjects);
    
    if (actualFragments < MIN_FRAGMENTS) {
        // Not enough room for fragments, fall back to merge
        return createMerge(body1, body2, idx1, idx2);
    }
    
    // For simplicity, we fragment the larger body and merge the smaller into one fragment
    const CelestialBody* largerBody = (body1.getMass() >= body2.getMass()) 
                                       ? &body1 : &body2;
    const CelestialBody* smallerBody = (body1.getMass() >= body2.getMass()) 
                                        ? &body2 : &body1;
    
    // Add smaller body's mass to the fragmentation pool
    double fragmentMass = (largerBody->getMass() + smallerBody->getMass()) / actualFragments;
    
    // Generate fragments from the combined mass
    result.newBodies = generateFragments(*largerBody, actualFragments, MAX_TOTAL_OBJECTS);
    
    // Adjust fragment masses to include the smaller body
    for (auto& fragment : result.newBodies) {
        fragment->setMass(fragmentMass);
        // Recalculate radius for the new mass (assuming same density)
        double density = largerBody->getDensity();
        if (density > 0.0) {
            double volume = fragmentMass / density;
            double radius = std::cbrt(volume * 3.0 / (4.0 * M_PI));
            fragment->setRadius(radius);
        }
    }
    
    return result;
}

std::vector<std::unique_ptr<CelestialBody>> CollisionResolver::generateFragments(
    const CelestialBody& parent, int count, int maxTotalObjects) {
    
    std::vector<std::unique_ptr<CelestialBody>> fragments;
    fragments.reserve(count);
    
    // Calculate fragment properties
    double fragmentMass = parent.getMass() / count;
    double density = parent.getDensity();
    double fragmentVolume = fragmentMass / density;
    double fragmentRadius = std::cbrt(fragmentVolume * 3.0 / (4.0 * M_PI));
    
    // Create fragments with slight velocity dispersion
    std::normal_distribution<double> velocityDispersion(0.0, 10.0);  // m/s dispersion
    
    for (int i = 0; i < count; ++i) {
        std::string fragmentName = parent.getName() + "_" + std::to_string(i + 1);
        
        // Position: spread around parent position
        Vector3D parentPos = parent.getPosition();
        Vector3D fragmentPos(
            parentPos.x + velocityDispersion(m_rng) * fragmentRadius,
            parentPos.y + velocityDispersion(m_rng) * fragmentRadius,
            parentPos.z + velocityDispersion(m_rng) * fragmentRadius
        );
        
        // Velocity: parent velocity + small dispersion
        Vector3D fragmentVel(
            parent.getVelocity().x + velocityDispersion(m_rng),
            parent.getVelocity().y + velocityDispersion(m_rng),
            parent.getVelocity().z + velocityDispersion(m_rng)
        );
        
        auto fragment = std::make_unique<CelestialBody>(
            fragmentName,
            fragmentMass,
            fragmentRadius,
            fragmentPos,
            fragmentVel,
            Vector3D()
        );
        
        // Fragments cannot fragment again
        fragment->setCanFragment(false);
        
        fragments.push_back(std::move(fragment));
    }
    
    return fragments;
}

} // namespace physics
