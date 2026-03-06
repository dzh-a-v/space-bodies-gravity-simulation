#include "CelestialBody.h"
#include "PhysicsConstants.h"

namespace physics {

std::atomic<int> CelestialBody::s_nextId{0};

CelestialBody::CelestialBody()
    : m_name("Body_" + std::to_string(s_nextId++))
    , m_mass(MIN_MASS)
    , m_radius(MIN_RADIUS)
    , m_position()
    , m_velocity()
    , m_acceleration()
    , m_id(s_nextId++)
{
}

CelestialBody::CelestialBody(const std::string& name, double mass, double radius,
                             const Vector3D& position, const Vector3D& velocity,
                             const Vector3D& acceleration)
    : m_name(name)
    , m_mass(mass)
    , m_radius(radius)
    , m_position(position)
    , m_velocity(velocity)
    , m_acceleration(acceleration)
    , m_id(s_nextId++)
{
}

double CelestialBody::getDensity() const {
    // Density = mass / volume
    // Volume of sphere = (4/3) * π * r³
    double volume = (4.0 / 3.0) * M_PI * std::pow(m_radius, 3);
    if (volume <= 0.0) {
        return 0.0;
    }
    return m_mass / volume;
}

double CelestialBody::getEscapeVelocity() const {
    // v_esc = sqrt(2 * G * m / r)
    if (m_radius <= 0.0) {
        return 0.0;
    }
    return std::sqrt(2.0 * G * m_mass / m_radius);
}

} // namespace physics
