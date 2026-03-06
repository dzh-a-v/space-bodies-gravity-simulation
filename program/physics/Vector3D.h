#pragma once

#include <cmath>
#include <string>

namespace physics {

/**
 * @brief 3D vector class for position, velocity, and acceleration
 */
class Vector3D {
public:
    double x, y, z;

    Vector3D() : x(0.0), y(0.0), z(0.0) {}
    Vector3D(double x, double y, double z) : x(x), y(y), z(z) {}

    Vector3D operator+(const Vector3D& other) const {
        return Vector3D(x + other.x, y + other.y, z + other.z);
    }

    Vector3D operator-(const Vector3D& other) const {
        return Vector3D(x - other.x, y - other.y, z - other.z);
    }

    Vector3D operator*(double scalar) const {
        return Vector3D(x * scalar, y * scalar, z * scalar);
    }

    Vector3D operator/(double scalar) const {
        return Vector3D(x / scalar, y / scalar, z / scalar);
    }

    Vector3D& operator+=(const Vector3D& other) {
        x += other.x;
        y += other.y;
        z += other.z;
        return *this;
    }

    Vector3D& operator-=(const Vector3D& other) {
        x -= other.x;
        y -= other.y;
        z -= other.z;
        return *this;
    }

    Vector3D operator-() const {
        return Vector3D(-x, -y, -z);
    }

    double dot(const Vector3D& other) const {
        return x * other.x + y * other.y + z * other.z;
    }

    Vector3D cross(const Vector3D& other) const {
        return Vector3D(
            y * other.z - z * other.y,
            z * other.x - x * other.z,
            x * other.y - y * other.x
        );
    }

    double magnitude() const {
        return std::sqrt(x * x + y * y + z * z);
    }

    double magnitudeSquared() const {
        return x * x + y * y + z * z;
    }

    Vector3D normalized() const {
        double mag = magnitude();
        if (mag > 0.0) {
            return *this / mag;
        }
        return Vector3D();
    }

    double distanceTo(const Vector3D& other) const {
        return (*this - other).magnitude();
    }

    bool isZero() const {
        constexpr double EPSILON = 1e-15;
        return magnitudeSquared() < EPSILON;
    }

    std::string toString() const {
        return "(" + std::to_string(x) + ", " + std::to_string(y) + ", " + std::to_string(z) + ")";
    }
};

inline Vector3D operator*(double scalar, const Vector3D& vec) {
    return vec * scalar;
}

} // namespace physics
