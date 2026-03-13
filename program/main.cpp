#include "simulation/SimulationEngine.h"
#include "io/CSVSerializer.h"
#include "physics/PhysicsConstants.h"
#include <iostream>
#include <memory>

using namespace physics;
using namespace simulation;
using namespace io;

void printStats(const SimulationStats& stats) {
    std::cout << "=== Simulation Stats ===" << std::endl;
    std::cout << "Time: " << stats.currentTime << " s" << std::endl;
    std::cout << "Objects: " << stats.objectCount << std::endl;
    std::cout << "Collisions: " << stats.totalCollisions << std::endl;
    std::cout << "Mergers: " << stats.totalMergers << std::endl;
    std::cout << "Fragmentations: " << stats.totalFragmentations << std::endl;
    std::cout << "Roche destructions: " << stats.rocheDestructions << std::endl;
}

void runBasicTest() {
    std::cout << "\n=== Running Basic Simulation Test ===" << std::endl;

    // Create a simple two-body system (Earth-like and Moon-like)
    std::vector<std::unique_ptr<CelestialBody>> bodies;

    // Earth-like body (at origin)
    auto earth = std::make_unique<CelestialBody>(
        "Earth",
        5.972e24,  // kg
        6.371e6,   // m
        Vector3D(0, 0, 0),
        Vector3D(0, 0, 0)
    );

    // Moon-like body (at orbital distance, with orbital velocity)
    double moonDistance = 3.844e8;  // m
    double moonVelocity = 1022;     // m/s (approximate orbital velocity)
    
    auto moon = std::make_unique<CelestialBody>(
        "Moon",
        7.342e22,  // kg
        1.737e6,   // m
        Vector3D(moonDistance, 0, 0),
        Vector3D(0, moonVelocity, 0)
    );

    bodies.push_back(std::move(earth));
    bodies.push_back(std::move(moon));

    // Initialize simulation
    SimulationEngine engine;
    engine.initialize(std::move(bodies));

    // Run simulation for 1000 steps (1000 seconds)
    double dt = 1.0;  // 1 second per step
    int steps = 1000;

    std::cout << "Running " << steps << " steps with dt=" << dt << "s..." << std::endl;

    for (int i = 0; i < steps; ++i) {
        engine.step(dt);
        
        if (i % 100 == 0) {
            auto bodies = engine.getBodies();
            std::cout << "\n--- Step " << i << " ---" << std::endl;
            for (const auto& body : bodies) {
                const auto& pos = body->getPosition();
                std::cout << "  " << body->getName() 
                          << ": (" << pos.x / 1e6 << " Mm, "
                          << pos.y / 1e6 << " Mm, "
                          << pos.z / 1e6 << " Mm)" << std::endl;
            }
        }
    }

    // Print final stats
    printStats(engine.getStats());

    // Test CSV export
    std::cout << "\n=== Testing CSV Export ===" << std::endl;
    std::string csv = CSVSerializer::serialize(engine.getBodies());
    std::cout << "CSV output (first 300 chars):" << std::endl;
    std::cout << csv.substr(0, std::min(csv.size(), size_t(300))) << "..." << std::endl;
}

void runCollisionTest() {
    std::cout << "\n=== Running Collision Test ===" << std::endl;

    std::vector<std::unique_ptr<CelestialBody>> bodies;

    // Create two bodies on collision course
    auto body1 = std::make_unique<CelestialBody>(
        "Body1",
        1e20,  // kg
        1e6,   // m
        Vector3D(0, 0, 0),
        Vector3D(100, 0, 0)  // Moving right
    );

    auto body2 = std::make_unique<CelestialBody>(
        "Body2",
        1e20,  // kg
        1e6,   // m
        Vector3D(5e6, 0, 0),  // 5000 km away
        Vector3D(-100, 0, 0)  // Moving left
    );

    bodies.push_back(std::move(body1));
    bodies.push_back(std::move(body2));

    SimulationEngine engine;
    engine.initialize(std::move(bodies));

    // Run until collision or timeout
    double dt = 1.0;
    int maxSteps = 100000;
    
    for (int i = 0; i < maxSteps; ++i) {
        engine.step(dt);
        
        auto currentBodies = engine.getBodies();
        
        // Print status at intervals
        if (i % 10000 == 0 || currentBodies.size() > 2) {
            std::cout << "\n=== Step " << i << " ===" << std::endl;
            std::cout << "Object count: " << currentBodies.size() << std::endl;
            
            for (size_t j = 0; j < currentBodies.size(); ++j) {
                const auto& body = currentBodies[j];
                const auto& pos = body->getPosition();
                const auto& vel = body->getVelocity();
                std::cout << "  [" << j << "] " << body->getName() 
                          << ": pos=(" << pos.x / 1e3 << " km, " 
                          << pos.y / 1e3 << " km, " 
                          << pos.z / 1e3 << " km)"
                          << ", vel=(" << vel.x << ", " << vel.y << ", " << vel.z << ") m/s"
                          << ", mass=" << body->getMass() / 1e20 << "e20 kg"
                          << ", radius=" << body->getRadius() / 1e3 << " km"
                          << std::endl;
            }
            
            // Stop after fragmentation to avoid too much output
            if (currentBodies.size() > 2) {
                std::cout << "\n(Fragmentation occurred - stopping early)" << std::endl;
                break;
            }
        }
    }

    printStats(engine.getStats());
}

int main() {
    std::cout << "Gravity Simulator - Physics Engine Test" << std::endl;
    std::cout << "========================================" << std::endl;

    runBasicTest();
    runCollisionTest();

    std::cout << "\n=== All Tests Complete ===" << std::endl;
    return 0;
}
