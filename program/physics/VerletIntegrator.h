#pragma once

#include "CelestialBody.h"
#include "Vector3D.h"
#include <vector>

namespace physics {

/**
 * @brief Velocity Verlet integrator for numerical time stepping
 * 
 * The Velocity Verlet algorithm:
 * 1. x(t+Δt) = x(t) + v(t)Δt + 0.5*a(t)Δt²
 * 2. Calculate a(t+Δt) from new positions
 * 3. v(t+Δt) = v(t) + 0.5*(a(t) + a(t+Δt))Δt
 */
class VerletIntegrator {
public:
    /**
     * @brief Perform one integration step for all bodies
     * @param bodies All bodies to integrate
     * @param dt Time step (seconds)
     * @param gravityCalculator Functor to calculate accelerations
     */
    template<typename AccelerationFunc>
    static void step(std::vector<CelestialBody*>& bodies, double dt, 
                     AccelerationFunc&& calculateAcceleration);

    /**
     * @brief Perform one integration step for a single body
     * @param body The body to integrate
     * @param dt Time step (seconds)
     * @param newAcceleration The acceleration at the new position
     */
    static void stepBody(CelestialBody& body, double dt, const Vector3D& newAcceleration);
};

// Template implementation
template<typename AccelerationFunc>
void VerletIntegrator::step(std::vector<CelestialBody*>& bodies, double dt,
                             AccelerationFunc&& calculateAcceleration) {
    if (dt <= 0.0) {
        return;
    }

    // Store old accelerations
    std::vector<Vector3D> oldAccelerations;
    oldAccelerations.reserve(bodies.size());

    // Step 1: Update positions using old acceleration
    for (auto* body : bodies) {
        if (body->isDestroyed()) continue;

        Vector3D oldAccel = body->getAcceleration();
        oldAccelerations.push_back(oldAccel);

        // x(t+Δt) = x(t) + v(t)Δt + 0.5*a(t)Δt²
        Vector3D newPos = body->getPosition() 
                        + body->getVelocity() * dt 
                        + oldAccel * (0.5 * dt * dt);
        body->setPosition(newPos);
    }

    // Step 2: Calculate new accelerations from new positions
    for (size_t i = 0; i < bodies.size(); ++i) {
        if (bodies[i]->isDestroyed()) continue;

        Vector3D newAccel = calculateAcceleration(bodies[i], i);
        
        // Step 3: Update velocities
        // v(t+Δt) = v(t) + 0.5*(a(t) + a(t+Δt))Δt
        Vector3D newVel = bodies[i]->getVelocity() 
                        + (oldAccelerations[i] + newAccel) * (0.5 * dt);
        bodies[i]->setVelocity(newVel);
        bodies[i]->setAcceleration(newAccel);
    }
}

inline void VerletIntegrator::stepBody(CelestialBody& body, double dt, const Vector3D& newAcceleration) {
    if (dt <= 0.0 || body.isDestroyed()) {
        return;
    }

    Vector3D oldAccel = body.getAcceleration();

    // x(t+Δt) = x(t) + v(t)Δt + 0.5*a(t)Δt²
    Vector3D newPos = body.getPosition() 
                    + body.getVelocity() * dt 
                    + oldAccel * (0.5 * dt * dt);

    // v(t+Δt) = v(t) + 0.5*(a(t) + a(t+Δt))Δt
    Vector3D newVel = body.getVelocity() 
                    + (oldAccel + newAcceleration) * (0.5 * dt);

    body.setPosition(newPos);
    body.setVelocity(newVel);
    body.setAcceleration(newAcceleration);
}

} // namespace physics
