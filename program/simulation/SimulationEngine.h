#pragma once

#include "physics/CelestialBody.h"
#include "physics/CollisionResolver.h"
#include "simulation/SimulationConfig.h"
#include <vector>
#include <memory>
#include <functional>
#include <iostream>
#include <iomanip>

namespace simulation {

/**
 * @brief Statistics about the current simulation state
 */
struct SimulationStats {
    double currentTime;         // Total simulated time (seconds)
    int objectCount;            // Current number of active objects
    int totalCollisions;        // Total collisions resolved
    int totalMergers;           // Total merger events
    int totalFragmentations;    // Total fragmentation events
    int rocheDestructions;      // Total Roche limit destructions
};

/**
 * @brief Main simulation engine that orchestrates all physics components
 */
class SimulationEngine {
public:
    SimulationEngine();
    ~SimulationEngine();

    // Prevent copying
    SimulationEngine(const SimulationEngine&) = delete;
    SimulationEngine& operator=(const SimulationEngine&) = delete;

    /**
     * @brief Initialize simulation with given bodies
     */
    void initialize(std::vector<std::unique_ptr<physics::CelestialBody>> bodies);

    /**
     * @brief Perform one simulation step
     * @param dt Time delta (seconds), adjusted by speed multiplier
     */
    void step(double dt);

    /**
     * @brief Reset simulation to initial state
     */
    void reset();

    /**
     * @brief Clear all bodies
     */
    void clear();

    /**
     * @brief Add a new body to the simulation
     */
    void addBody(std::unique_ptr<physics::CelestialBody> body);

    /**
     * @brief Remove a body by index
     */
    void removeBody(size_t index);

    /**
     * @brief Get all bodies (non-owning pointers)
     */
    std::vector<physics::CelestialBody*> getBodies() const;

    /**
     * @brief Get configuration
     */
    const SimulationConfig& getConfig() const { return m_config; }

    /**
     * @brief Set configuration
     */
    void setConfig(const SimulationConfig& config);

    /**
     * @brief Set fragment count
     */
    void setFragmentCount(int count);

    /**
     * @brief Get current simulation statistics
     */
    SimulationStats getStats() const;

    /**
     * @brief Get current simulated time
     */
    double getCurrentTime() const { return m_currentTime; }

    /**
     * @brief Check if simulation is paused
     */
    bool isPaused() const { return m_paused; }

    /**
     * @brief Set pause state
     */
    void setPaused(bool paused) { m_paused = paused; }

    /**
     * @brief Toggle pause state
     */
    void togglePause() { m_paused = !m_paused; }

private:
    std::vector<std::unique_ptr<physics::CelestialBody>> m_bodies;
    SimulationConfig m_config;
    double m_currentTime;
    bool m_paused;

    // Statistics
    int m_totalCollisions;
    int m_totalMergers;
    int m_totalFragmentations;
    int m_rocheDestructions;

    // Collision resolver
    physics::CollisionResolver m_collisionResolver;

    /**
     * @brief Calculate total acceleration on a body
     */
    physics::Vector3D calculateAcceleration(physics::CelestialBody* body, size_t index);

    /**
     * @brief Handle collisions
     */
    void handleCollisions();

    /**
     * @brief Handle Roche limit destruction
     */
    void handleRocheLimit(double dt);

    /**
     * @brief Clean up destroyed bodies
     */
    void cleanupDestroyedBodies();
};

} // namespace simulation
