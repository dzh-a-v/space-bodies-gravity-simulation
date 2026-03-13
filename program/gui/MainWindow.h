#pragma once

#include <QMainWindow>
#include <QTimer>
#include <QTableWidget>
#include <QPushButton>
#include <QLabel>
#include <vector>
#include <memory>

namespace simulation {
    class SimulationEngine;
}

namespace physics {
    class CelestialBody;
}

namespace gui {

/**
 * @brief Simulation view widget for displaying celestial bodies in a specific projection
 */
class SimulationView : public QWidget {
    Q_OBJECT

public:
    enum class Projection {
        XY,  // Top view (Z-axis ignored)
        XZ,  // Front view (Y-axis ignored)
        YZ   // Side view (X-axis ignored)
    };

    explicit SimulationView(Projection projection, QWidget* parent = nullptr);
    void setBodies(const std::vector<physics::CelestialBody*>& bodies);

protected:
    void paintEvent(QPaintEvent* event) override;

private:
    Projection m_projection;
    std::vector<physics::CelestialBody*> m_bodies;
    double m_scale;  // meters per pixel
    double m_offsetX;
    double m_offsetY;
};

/**
 * @brief Object info table widget
 */
class ObjectInfoTable : public QTableWidget {
    Q_OBJECT

public:
    explicit ObjectInfoTable(QWidget* parent = nullptr);
    void updateBodies(const std::vector<physics::CelestialBody*>& bodies);

private:
    void setupTable();
};

/**
 * @brief Main application window
 */
class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    explicit MainWindow(QWidget* parent = nullptr);
    ~MainWindow();

private slots:
    void updateSimulation();
    void onPlayPause();
    void onReset();

private:
    void setupUI();
    void setupMenuBar();
    void setupStatusBar();
    void loadInitialSimulation();

    // Central widgets
    ObjectInfoTable* m_objectTable;
    QPushButton* m_placeholderButton;
    SimulationView* m_xyView;
    SimulationView* m_xzView;
    SimulationView* m_yzView;

    // Simulation
    std::unique_ptr<simulation::SimulationEngine> m_engine;
    QTimer* m_timer;
    bool m_running;

    // Status bar labels
    QLabel* m_timeLabel;
    QLabel* m_objectCountLabel;
};

} // namespace gui
