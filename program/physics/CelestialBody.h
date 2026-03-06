#pragma once

#include "Vector3D.h"
#include <string>
#include <atomic>

namespace physics {

/**
 * @brief Represents a celestial body (point mass as uniform sphere)
 */
class CelestialBody {
public:
    CelestialBody();
    CelestialBody(const std::string& name, double mass, double radius,
                  const Vector3D& position, const Vector3D& velocity,
                  const Vector3D& acceleration = Vector3D());

    // Getters
    const std::string& getName() const { return m_name; }
    double getMass() const { return m_mass; }
    double getRadius() const { return m_radius; }
    const Vector3D& getPosition() const { return m_position; }
    const Vector3D& getVelocity() const { return m_velocity; }
    const Vector3D& getAcceleration() const { return m_acceleration; }

    // Setters
    void setName(const std::string& name) { m_name = name; }
    void setMass(double mass) { m_mass = mass; }
    void setRadius(double radius) { m_radius = radius; }
    void setPosition(const Vector3D& pos) { m_position = pos; }
    void setVelocity(const Vector3D& vel) { m_velocity = vel; }
    void setAcceleration(const Vector3D& acc) { m_acceleration = acc; }

    // State
    bool isDestroyed() const { return m_destroyed; }
    void markDestroyed() { m_destroyed = true; }

    bool canFragment() const { return m_canFragment; }
    void setCanFragment(bool can) { m_canFragment = can; }

    // Roche limit tracking
    double getTimeInsideRocheLimit() const { return m_timeInsideRocheLimit; }
    void addTimeInsideRocheLimit(double dt) { m_timeInsideRocheLimit += dt; }
    void resetTimeInsideRocheLimit() { m_timeInsideRocheLimit = 0.0; }

    // Density calculation (kg/m³)
    double getDensity() const;

    // Escape velocity from surface (m/s)
    double getEscapeVelocity() const;

    // Unique ID for internal tracking
    int getId() const { return m_id; }

private:
    std::string m_name;
    double m_mass;        // kg
    double m_radius;      // m
    Vector3D m_position;  // m
    Vector3D m_velocity;  // m/s
    Vector3D m_acceleration; // m/s²

    bool m_destroyed = false;
    bool m_canFragment = true;  // Fragments cannot fragment again

    double m_timeInsideRocheLimit = 0.0;  // seconds

    static std::atomic<int> s_nextId;
    int m_id;
};

} // namespace physics
