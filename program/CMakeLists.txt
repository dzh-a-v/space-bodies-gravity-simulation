cmake_minimum_required(VERSION 3.16)
project(GravitySimulator VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Qt6 is optional for now (needed only for GUI phase)
set(USE_QT6 OFF CACHE BOOL "Use Qt6 for GUI")

if(USE_QT6)
    set(CMAKE_AUTOMOC ON)
    set(CMAKE_AUTORCC ON)
    set(CMAKE_AUTOUIC ON)
    find_package(Qt6 REQUIRED COMPONENTS Widgets)
endif()

set(PHYSICS_SOURCES
    physics/Vector3D.cpp
    physics/CelestialBody.cpp
    physics/GravityCalculator.cpp
    physics/VerletIntegrator.cpp
    physics/CollisionDetector.cpp
    physics/CollisionResolver.cpp
    physics/RocheLimitCalculator.cpp
)

set(PHYSICS_HEADERS
    physics/Vector3D.h
    physics/CelestialBody.h
    physics/GravityCalculator.h
    physics/VerletIntegrator.h
    physics/CollisionDetector.h
    physics/CollisionResolver.h
    physics/RocheLimitCalculator.h
    physics/PhysicsConstants.h
)

set(SIMULATION_SOURCES
    simulation/SimulationEngine.cpp
)

set(SIMULATION_HEADERS
    simulation/SimulationEngine.h
    simulation/SimulationConfig.h
)

set(IO_SOURCES
    io/CSVSerializer.cpp
)

set(IO_HEADERS
    io/CSVSerializer.h
)

set(SOURCES
    main.cpp
    ${PHYSICS_SOURCES}
    ${SIMULATION_SOURCES}
    ${IO_SOURCES}
)

set(HEADERS
    ${PHYSICS_HEADERS}
    ${SIMULATION_HEADERS}
    ${IO_HEADERS}
)

add_executable(${PROJECT_NAME} ${SOURCES} ${HEADERS})

if(USE_QT6)
    target_link_libraries(${PROJECT_NAME} PRIVATE Qt6::Widgets)
endif()

target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_SOURCE_DIR})
