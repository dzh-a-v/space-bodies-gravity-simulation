#pragma once

namespace simulation {

/**
 * @brief Configuration for the simulation
 */
struct SimulationConfig {
    /// Time step in seconds
    double timeStep = 1.0;

    /// Simulation speed multiplier (1.0 = real time)
    double speedMultiplier = 1.0;

    /// Number of fragments to create on destruction (2-100)
    int fragmentCount = 10;

    /// Enable collision detection
    bool enableCollisions = true;

    /// Enable Roche limit destruction
    bool enableRocheLimit = true;

    /// Maximum number of objects allowed
    int maxObjects = 10000;
};

} // namespace simulation
