#include "CSVSerializer.h"
#include <fstream>
#include <sstream>
#include <iostream>

namespace io {

bool CSVSerializer::saveToFile(const std::string& filename,
                                const std::vector<physics::CelestialBody*>& bodies) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        return false;
    }

    // Write header
    file << "name,mass,radius,pos_x,pos_y,pos_z,vel_x,vel_y,vel_z,acc_x,acc_y,acc_z\n";

    // Write body data
    for (const auto* body : bodies) {
        if (!body->isDestroyed()) {
            file << toLine(*body) << "\n";
        }
    }

    file.close();
    return true;
}

bool CSVSerializer::loadFromFile(const std::string& filename,
                                  std::vector<std::unique_ptr<physics::CelestialBody>>& bodies) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        return false;
    }

    bodies.clear();
    std::string line;

    // Skip header line
    std::getline(file, line);

    // Read body data
    while (std::getline(file, line)) {
        if (line.empty()) continue;

        auto body = parseLine(line);
        if (body) {
            bodies.push_back(std::move(body));
        }
    }

    file.close();
    return true;
}

std::string CSVSerializer::serialize(const std::vector<physics::CelestialBody*>& bodies) {
    std::ostringstream oss;
    oss << "name,mass,radius,pos_x,pos_y,pos_z,vel_x,vel_y,vel_z,acc_x,acc_y,acc_z\n";

    for (const auto* body : bodies) {
        if (!body->isDestroyed()) {
            oss << toLine(*body) << "\n";
        }
    }

    return oss.str();
}

bool CSVSerializer::deserialize(const std::string& csv,
                                 std::vector<std::unique_ptr<physics::CelestialBody>>& bodies) {
    bodies.clear();
    std::istringstream iss(csv);
    std::string line;

    // Skip header line
    std::getline(iss, line);

    // Read body data
    while (std::getline(iss, line)) {
        if (line.empty()) continue;

        auto body = parseLine(line);
        if (body) {
            bodies.push_back(std::move(body));
        }
    }

    return true;
}

std::unique_ptr<physics::CelestialBody> CSVSerializer::parseLine(const std::string& line) {
    std::istringstream iss(line);
    std::string token;
    std::vector<std::string> tokens;

    // Split by comma
    while (std::getline(iss, token, ',')) {
        tokens.push_back(token);
    }

    // Expect 12 values: name, mass, radius, pos(3), vel(3), acc(3)
    if (tokens.size() < 12) {
        return nullptr;
    }

    try {
        std::string name = tokens[0];
        double mass = std::stod(tokens[1]);
        double radius = std::stod(tokens[2]);
        double posX = std::stod(tokens[3]);
        double posY = std::stod(tokens[4]);
        double posZ = std::stod(tokens[5]);
        double velX = std::stod(tokens[6]);
        double velY = std::stod(tokens[7]);
        double velZ = std::stod(tokens[8]);
        double accX = std::stod(tokens[9]);
        double accY = std::stod(tokens[10]);
        double accZ = std::stod(tokens[11]);

        return std::make_unique<physics::CelestialBody>(
            name,
            mass,
            radius,
            physics::Vector3D(posX, posY, posZ),
            physics::Vector3D(velX, velY, velZ),
            physics::Vector3D(accX, accY, accZ)
        );
    }
    catch (const std::exception& e) {
        return nullptr;
    }
}

std::string CSVSerializer::toLine(const physics::CelestialBody& body) {
    std::ostringstream oss;
    
    // Handle names with special characters by quoting if necessary
    std::string name = body.getName();
    bool needsQuotes = name.find(',') != std::string::npos || 
                       name.find('"') != std::string::npos ||
                       name.find('\n') != std::string::npos;
    
    if (needsQuotes) {
        // Escape quotes by doubling them
        std::string escaped;
        for (char c : name) {
            if (c == '"') escaped += "\"\"";
            else escaped += c;
        }
        oss << "\"" << escaped << "\"";
    } else {
        oss << name;
    }
    
    // Use scientific notation for very large/small numbers
    oss << std::scientific;
    oss << "," << body.getMass();
    oss << "," << body.getRadius();
    
    const auto& pos = body.getPosition();
    oss << "," << pos.x << "," << pos.y << "," << pos.z;
    
    const auto& vel = body.getVelocity();
    oss << "," << vel.x << "," << vel.y << "," << vel.z;
    
    const auto& acc = body.getAcceleration();
    oss << "," << acc.x << "," << acc.y << "," << acc.z;
    
    return oss.str();
}

} // namespace io
