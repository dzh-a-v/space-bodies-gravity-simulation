#pragma once

#include "physics/CelestialBody.h"
#include <vector>
#include <string>
#include <memory>

namespace io {

/**
 * @brief CSV serialization/deserialization for simulation scenarios
 * 
 * CSV Format:
 * name,mass,radius,pos_x,pos_y,pos_z,vel_x,vel_y,vel_z,acc_x,acc_y,acc_z
 */
class CSVSerializer {
public:
    /**
     * @brief Save bodies to a CSV file
     * @param filename Path to the CSV file
     * @param bodies Vector of bodies to save
     * @return true on success, false on failure
     */
    static bool saveToFile(const std::string& filename,
                           const std::vector<physics::CelestialBody*>& bodies);

    /**
     * @brief Load bodies from a CSV file
     * @param filename Path to the CSV file
     * @param bodies Output vector of loaded bodies
     * @return true on success, false on failure
     */
    static bool loadFromFile(const std::string& filename,
                             std::vector<std::unique_ptr<physics::CelestialBody>>& bodies);

    /**
     * @brief Serialize bodies to CSV string
     * @param bodies Vector of bodies to serialize
     * @return CSV formatted string
     */
    static std::string serialize(const std::vector<physics::CelestialBody*>& bodies);

    /**
     * @brief Deserialize bodies from CSV string
     * @param csv CSV formatted string
     * @param bodies Output vector of loaded bodies
     * @return true on success, false on failure
     */
    static bool deserialize(const std::string& csv,
                            std::vector<std::unique_ptr<physics::CelestialBody>>& bodies);

private:
    /**
     * @brief Parse a single CSV line into a CelestialBody
     */
    static std::unique_ptr<physics::CelestialBody> parseLine(const std::string& line);

    /**
     * @brief Convert a body to CSV line
     */
    static std::string toLine(const physics::CelestialBody& body);
};

} // namespace io
