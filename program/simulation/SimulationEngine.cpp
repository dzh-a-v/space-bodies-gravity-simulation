#include "SimulationEngine.h"
#include "physics/GravityCalculator.h"
#include "physics/VerletIntegrator.h"
#include "physics/CollisionDetector.h"
#include "physics/RocheLimitCalculator.h"
#include "physics/PhysicsConstants.h"
#include <algorithm>

namespace simulation {

SimulationEngine::SimulationEngine()
    : m_currentTime(0.0)
    , m_paused(false)
    , m_totalCollisions(0)
    , m_totalMergers(0)
    , m_totalFragmentations(0)
    , m_rocheDestructions(0)
{
}

SimulationEngine::~SimulationEngine() = default;

void SimulationEngine::initialize(std::vector<std::unique_ptr<physics::CelestialBody>> bodies) {
    m_bodies = std::move(bodies);
    m_currentTime = 0.0;
    m_paused = false;
    m_totalCollisions = 0;
    m_totalMergers = 0;
    m_totalFragmentations = 0;
    m_rocheDestructions = 0;

    // Calculate initial accelerations
    for (size_t i = 0; i < m_bodies.size(); ++i) {
        if (!m_bodies[i]->isDestroyed()) {
            auto bodyPtrs = getBodies();
            auto accel = physics::GravityCalculator::calculateTotalAcceleration(
                *m_bodies[i], bodyPtrs);
            m_bodies[i]->setAcceleration(accel);
        }
    }
}

void SimulationEngine::step(double dt) {
    if (m_paused || dt <= 0.0) {
        return;
    }

    // Apply speed multiplier
    double effectiveDt = dt * m_config.speedMultiplier;

    // Clean up any previously destroyed bodies
    cleanupDestroyedBodies();

    // Handle Roche limit tracking and destruction
    if (m_config.enableRocheLimit) {
        handleRocheLimit(effectiveDt);
    }

    // Perform Verlet integration step
    auto bodyPtrs = getBodies();
    auto accelFunc = [this, &bodyPtrs](physics::CelestialBody* body, size_t index) {
        (void)index;
        return physics::GravityCalculator::calculateTotalAcceleration(*body, bodyPtrs);
    };

    physics::VerletIntegrator::step(bodyPtrs, effectiveDt, accelFunc);

    // Handle collisions
    if (m_config.enableCollisions) {
        handleCollisions();
    }

    // Update simulation time
    m_currentTime += effectiveDt;
}

void SimulationEngine::reset() {
    m_currentTime = 0.0;
    m_paused = false;
    // Note: We don't reset statistics on reset, only on initialize
}

void SimulationEngine::clear() {
    m_bodies.clear();
    m_currentTime = 0.0;
    m_paused = false;
}

void SimulationEngine::addBody(std::unique_ptr<physics::CelestialBody> body) {
    m_bodies.push_back(std::move(body));
}

void SimulationEngine::removeBody(size_t index) {
    if (index < m_bodies.size()) {
        m_bodies.erase(m_bodies.begin() + index);
    }
}

std::vector<physics::CelestialBody*> SimulationEngine::getBodies() const {
    std::vector<physics::CelestialBody*> result;
    result.reserve(m_bodies.size());
    
    for (const auto& body : m_bodies) {
        if (!body->isDestroyed()) {
            result.push_back(body.get());
        }
    }
    
    return result;
}

void SimulationEngine::setConfig(const SimulationConfig& config) {
    m_config = config;
    m_collisionResolver.setFragmentCount(config.fragmentCount);
}

void SimulationEngine::setFragmentCount(int count) {
    m_config.fragmentCount = std::clamp(count, physics::MIN_FRAGMENTS, physics::MAX_FRAGMENTS);
    m_collisionResolver.setFragmentCount(m_config.fragmentCount);
}

SimulationStats SimulationEngine::getStats() const {
    SimulationStats stats;
    stats.currentTime = m_currentTime;
    stats.objectCount = static_cast<int>(getBodies().size());
    stats.totalCollisions = m_totalCollisions;
    stats.totalMergers = m_totalMergers;
    stats.totalFragmentations = m_totalFragmentations;
    stats.rocheDestructions = m_rocheDestructions;
    return stats;
}

physics::Vector3D SimulationEngine::calculateAcceleration(physics::CelestialBody* body,
                                                           size_t index) {
    (void)index;  // Unused parameter for now
    auto bodyPtrs = getBodies();
    return physics::GravityCalculator::calculateTotalAcceleration(*body, bodyPtrs);
}

void SimulationEngine::handleCollisions() {
    auto bodyPtrs = getBodies();
    auto collisions = physics::CollisionDetector::findCollisions(bodyPtrs);
    
    if (collisions.empty()) {
        return;
    }

    // Track which bodies have been processed this step
    std::vector<bool> processed(m_bodies.size(), false);
    
    for (const auto& [idx1, idx2] : collisions) {
        if (processed[idx1] || processed[idx2]) {
            continue;  // One of these bodies was already handled
        }

        if (m_bodies[idx1]->isDestroyed() || m_bodies[idx2]->isDestroyed()) {
            continue;
        }

        auto result = m_collisionResolver.resolve(
            *m_bodies[idx1], *m_bodies[idx2], 
            static_cast<int>(m_bodies.size()));

        m_totalCollisions++;

        if (result.type == physics::CollisionResult::MERGE) {
            m_totalMergers++;
            
            // Mark bodies for removal
            m_bodies[idx1]->markDestroyed();
            m_bodies[idx2]->markDestroyed();
            
            // Add merged body
            if (!result.newBodies.empty()) {
                // Update the merged body with correct position/velocity from result
                auto& mergedBody = result.newBodies[0];
                
                // Calculate merged properties
                double totalMass = m_bodies[idx1]->getMass() + m_bodies[idx2]->getMass();
                physics::Vector3D totalMomentum = m_bodies[idx1]->getVelocity() * m_bodies[idx1]->getMass()
                                       + m_bodies[idx2]->getVelocity() * m_bodies[idx2]->getMass();
                physics::Vector3D newVel = totalMomentum / totalMass;

                physics::Vector3D newPos = (m_bodies[idx1]->getPosition() * m_bodies[idx1]->getMass()
                                 + m_bodies[idx2]->getPosition() * m_bodies[idx2]->getMass())
                                / totalMass;

                mergedBody->setPosition(newPos);
                mergedBody->setVelocity(newVel);
                mergedBody->setAcceleration(physics::Vector3D());
                
                m_bodies.push_back(std::move(mergedBody));
            }
            
            processed[idx1] = true;
            processed[idx2] = true;
        }
        else if (result.type == physics::CollisionResult::FRAGMENT) {
            m_totalFragmentations++;
            
            // Mark bodies for removal
            m_bodies[idx1]->markDestroyed();
            m_bodies[idx2]->markDestroyed();
            
            // Add fragments
            for (auto& fragment : result.newBodies) {
                m_bodies.push_back(std::move(fragment));
            }
            
            processed[idx1] = true;
            processed[idx2] = true;
        }
    }
}

void SimulationEngine::handleRocheLimit(double dt) {
    auto bodyPtrs = getBodies();
    auto insideRoche = physics::RocheLimitCalculator::findBodiesInsideRocheLimit(bodyPtrs);

    // Reset timer for bodies not inside Roche limit
    for (size_t i = 0; i < m_bodies.size(); ++i) {
        bool found = std::find(insideRoche.begin(), insideRoche.end(), i) != insideRoche.end();
        if (!found) {
            m_bodies[i]->resetTimeInsideRocheLimit();
        }
    }

    // Update timer for bodies inside Roche limit
    for (size_t idx : insideRoche) {
        if (m_bodies[idx]->isDestroyed() || !m_bodies[idx]->canFragment()) {
            continue;
        }

        m_bodies[idx]->addTimeInsideRocheLimit(dt);

        // Check if destruction condition is met
        if (physics::RocheLimitCalculator::shouldDestroyByRocheLimit(*m_bodies[idx])) {
            m_rocheDestructions++;

            // Create fragments
            double parentMass = m_bodies[idx]->getMass();
            int fragmentCount = m_config.fragmentCount;

            // Check object limit
            int maxNewObjects = m_config.maxObjects - static_cast<int>(m_bodies.size()) + 1;
            fragmentCount = std::min(fragmentCount, maxNewObjects);

            if (fragmentCount >= physics::MIN_FRAGMENTS &&
                parentMass >= physics::MIN_FRAGMENTATION_MASS) {

                double fragmentMass = parentMass / fragmentCount;
                double density = m_bodies[idx]->getDensity();
                double fragmentVolume = fragmentMass / density;
                double fragmentRadius = std::cbrt(fragmentVolume * 3.0 / (4.0 * M_PI));

                std::normal_distribution<double> velocityDispersion(0.0, 10.0);
                std::mt19937 rng(std::random_device{}());

                for (int i = 0; i < fragmentCount; ++i) {
                    std::string fragName = m_bodies[idx]->getName() + "_r" + std::to_string(i + 1);

                    physics::Vector3D parentPos = m_bodies[idx]->getPosition();
                    physics::Vector3D fragPos(
                        parentPos.x + velocityDispersion(rng) * fragmentRadius,
                        parentPos.y + velocityDispersion(rng) * fragmentRadius,
                        parentPos.z + velocityDispersion(rng) * fragmentRadius
                    );

                    physics::Vector3D fragVel(
                        m_bodies[idx]->getVelocity().x + velocityDispersion(rng),
                        m_bodies[idx]->getVelocity().y + velocityDispersion(rng),
                        m_bodies[idx]->getVelocity().z + velocityDispersion(rng)
                    );
                    
                    auto fragment = std::make_unique<physics::CelestialBody>(
                        fragName, fragmentMass, fragmentRadius, fragPos, fragVel, physics::Vector3D()
                    );
                    fragment->setCanFragment(false);  // Fragments can't fragment again
                    
                    m_bodies.push_back(std::move(fragment));
                }
            }
            
            // Mark parent for destruction
            m_bodies[idx]->markDestroyed();
        }
    }
}

void SimulationEngine::cleanupDestroyedBodies() {
    m_bodies.erase(
        std::remove_if(m_bodies.begin(), m_bodies.end(),
            [](const std::unique_ptr<physics::CelestialBody>& body) {
                return body->isDestroyed();
            }),
        m_bodies.end()
    );
}

} // namespace simulation
