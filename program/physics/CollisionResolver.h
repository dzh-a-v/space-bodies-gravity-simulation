#pragma once

#include "CelestialBody.h"
#include "CollisionDetector.h"
#include <vector>
#include <memory>
#include <random>

namespace physics {

/**
 * @brief Result of collision resolution
 */
struct CollisionResult {
    enum Type {
        MERGE,           // Bodies merge into one
        FRAGMENT,        // Bodies fragment into pieces
        PRE_FRAGMENT,    // Pre-collision fragmentation (bodies very close)
        NO_ACTION        // No action taken (bodies pass through)
    };

    Type type;
    std::vector<std::unique_ptr<CelestialBody>> newBodies;  // Created fragments
    size_t bodyToRemove1;  // Index of first body to remove
    size_t bodyToRemove2;  // Index of second body to remove
    size_t mergedBodyIndex; // Index of merged body (if MERGE)

    CollisionResult() : type(NO_ACTION), bodyToRemove1(0), bodyToRemove2(0),
                        mergedBodyIndex(0) {}
};

/**
 * @brief Resolves collisions between celestial bodies according to spec rules
 *
 * Rules:
 * - Mass ratio < 1/100: Always merge
 * - 1/100 <= ratio < 1/10: Probabilistic merge/fragment
 * - ratio >= 1/10:
 *   - v_rel > v_esc: Fragment
 *   - v_rel <= v_esc: Merge
 *
 * Pre-collision fragmentation:
 * - When bodies are very close (within 10% of combined radius) and approaching
 * - The smaller body fragments before actual contact
 */
class CollisionResolver {
public:
    CollisionResolver();

    /**
     * @brief Set the number of fragments to create on destruction
     * @param fragments Number of fragments (2-100)
     */
    void setFragmentCount(int fragments);

    /**
     * @brief Get current fragment count setting
     */
    int getFragmentCount() const { return m_fragmentCount; }

    /**
     * @brief Resolve a collision between two bodies
     * @param body1 First body
     * @param body2 Second body
     * @param currentObjectCount Current total objects in simulation
     * @return CollisionResult with action to take
     */
    CollisionResult resolve(const CelestialBody& body1, const CelestialBody& body2,
                            int currentObjectCount);

    /**
     * @brief Resolve a near-collision (pre-fragmentation)
     * @param event Collision event with distance/velocity info
     * @param body1 First body
     * @param body2 Second body
     * @param currentObjectCount Current total objects in simulation
     * @return CollisionResult with action to take
     */
    CollisionResult resolveNearCollision(const CollisionEvent& event,
                                         const CelestialBody& body1,
                                         const CelestialBody& body2,
                                         int currentObjectCount);

private:
    int m_fragmentCount;
    std::mt19937 m_rng;
    
    /**
     * @brief Calculate mass ratio (smaller/larger)
     */
    static double calculateMassRatio(const CelestialBody& body1, 
                                     const CelestialBody& body2);
    
    /**
     * @brief Calculate escape velocity of the smaller body
     */
    static double calculateEscapeVelocity(const CelestialBody& body1,
                                          const CelestialBody& body2);
    
    /**
     * @brief Create merge result (conservation of momentum)
     */
    CollisionResult createMerge(const CelestialBody& body1, const CelestialBody& body2,
                                size_t idx1, size_t idx2);
    
    /**
     * @brief Create fragment result
     */
    CollisionResult createFragments(const CelestialBody& body1, const CelestialBody& body2,
                                    size_t idx1, size_t idx2, int currentObjectCount);
    
    /**
     * @brief Generate fragment properties (mass, radius, velocity)
     */
    std::vector<std::unique_ptr<CelestialBody>> generateFragments(
        const CelestialBody& parent, int count, int maxTotalObjects);

    /**
     * @brief Generate fragments that inherit parent's velocity and acceleration
     */
    std::vector<std::unique_ptr<CelestialBody>> generateFragmentsWithParent(
        const CelestialBody& parent, int count,
        const Vector3D& inheritVelocity, const Vector3D& inheritAcceleration);
};

} // namespace physics
