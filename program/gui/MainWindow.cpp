#include "MainWindow.h"
#include "simulation/SimulationEngine.h"
#include "physics/CelestialBody.h"
#include <QApplication>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGridLayout>
#include <QSplitter>
#include <QGroupBox>
#include <QPainter>
#include <QPen>
#include <QBrush>
#include <QColor>
#include <QHeaderView>
#include <QMenuBar>
#include <QMenu>
#include <QAction>
#include <QStatusBar>
#include <QMessageBox>
#include <cmath>
#include <algorithm>

using namespace physics;
using namespace simulation;

namespace gui {

// ============================================================================
// SimulationView Implementation
// ============================================================================

SimulationView::SimulationView(Projection projection, QWidget* parent)
    : QWidget(parent)
    , m_projection(projection)
    , m_scale(1.0e7)  // Default: 10 million meters per pixel
    , m_offsetX(0)
    , m_offsetY(0)
{
    setMinimumSize(300, 300);
    setAutoFillBackground(true);
    QPalette pal = palette();
    pal.setColor(QPalette::Window, QColor(10, 10, 30));
    setPalette(pal);
}

void SimulationView::setBodies(const std::vector<CelestialBody*>& bodies) {
    m_bodies = bodies;
    update();
}

void SimulationView::paintEvent(QPaintEvent* event) {
    Q_UNUSED(event);

    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    // Clear background
    painter.fillRect(rect(), QColor(10, 10, 30));

    if (m_bodies.empty()) {
        // Draw "no data" text
        painter.setPen(QColor(100, 100, 100));
        QFont font = painter.font();
        font.setPointSize(14);
        painter.setFont(font);
        painter.drawText(rect(), Qt::AlignCenter, "No simulation data");
        return;
    }

    // Calculate bounding box for auto-scaling
    double minX = std::numeric_limits<double>::max();
    double maxX = std::numeric_limits<double>::lowest();
    double minY = std::numeric_limits<double>::max();
    double maxY = std::numeric_limits<double>::lowest();

    for (const auto* body : m_bodies) {
        Vector3D pos = body->getPosition();
        double x, y;

        switch (m_projection) {
            case Projection::XY: x = pos.x; y = pos.y; break;
            case Projection::XZ: x = pos.x; y = pos.z; break;
            case Projection::YZ: x = pos.y; y = pos.z; break;
        }

        minX = std::min(minX, x - body->getRadius());
        maxX = std::max(maxX, x + body->getRadius());
        minY = std::min(minY, y - body->getRadius());
        maxY = std::max(maxY, y + body->getRadius());
    }

    // Add padding
    double paddingX = (maxX - minX) * 0.1;
    double paddingY = (maxY - minY) * 0.1;
    minX -= paddingX;
    maxX += paddingX;
    minY -= paddingY;
    maxY += paddingY;

    // Calculate scale to fit
    if (maxX > minX && maxY > minY) {
        m_scale = std::min(width() / (maxX - minX), height() / (maxY - minY));
        m_scale = std::max(m_scale, 1.0e-9);  // Minimum scale
    }

    // Calculate center offset
    double centerX = (minX + maxX) / 2.0;
    double centerY = (minY + maxY) / 2.0;
    m_offsetX = width() / 2.0 - centerX * m_scale;
    m_offsetY = height() / 2.0 + centerY * m_scale;  // Flip Y for screen coords

    // Draw axes
    QPen axisPen(QColor(80, 80, 100));
    axisPen.setWidth(1);
    painter.setPen(axisPen);

    // X-axis (horizontal through center)
    int yAxis = static_cast<int>(m_offsetY + centerY * m_scale);
    painter.drawLine(0, yAxis, width(), yAxis);

    // Y-axis (vertical through center)
    int xAxis = static_cast<int>(m_offsetX - centerX * m_scale);
    painter.drawLine(xAxis, 0, xAxis, height());

    // Draw bodies
    for (const auto* body : m_bodies) {
        if (body->isDestroyed()) continue;

        Vector3D pos = body->getPosition();
        double x, y;

        switch (m_projection) {
            case Projection::XY: x = pos.x; y = pos.y; break;
            case Projection::XZ: x = pos.x; y = pos.z; break;
            case Projection::YZ: x = pos.y; y = pos.z; break;
        }

        // Transform to screen coordinates
        int screenX = static_cast<int>(x * m_scale + m_offsetX);
        int screenY = static_cast<int>(-y * m_scale + m_offsetY);  // Flip Y

        // Calculate radius (minimum 3 pixels for visibility)
        int screenRadius = std::max(3, static_cast<int>(body->getRadius() * m_scale));

        // Draw body with color based on mass (larger = more red)
        double mass = body->getMass();
        int red, green, blue;

        if (mass > 1e24) {
            // Star-like (yellow/orange)
            red = 255; green = 200; blue = 100;
        } else if (mass > 1e22) {
            // Planet-like (blue/green)
            red = 100; green = 150; blue = 255;
        } else {
            // Moon/asteroid-like (gray)
            red = 180; green = 180; blue = 180;
        }

        // Draw filled circle
        painter.setBrush(QBrush(QColor(red, green, blue)));
        painter.setPen(QPen(QColor(255, 255, 255), 1));
        painter.drawEllipse(QPoint(screenX, screenY), screenRadius, screenRadius);

        // Draw name label
        painter.setPen(QColor(255, 255, 255));
        QFont labelFont = painter.font();
        labelFont.setPointSize(8);
        painter.setFont(labelFont);
        QString name = QString::fromStdString(body->getName());
        painter.drawText(screenX + screenRadius + 5, screenY, name);
    }

    // Draw projection label
    painter.setPen(QColor(150, 150, 150));
    QFont labelFont = painter.font();
    labelFont.setPointSize(10);
    labelFont.setBold(true);
    painter.setFont(labelFont);

    QString label;
    switch (m_projection) {
        case Projection::XY: label = "XY Plane (Top View)"; break;
        case Projection::XZ: label = "XZ Plane (Front View)"; break;
        case Projection::YZ: label = "YZ Plane (Side View)"; break;
    }
    painter.drawText(rect().adjusted(10, 10, -10, -10), Qt::AlignTop | Qt::AlignLeft, label);
}

// ============================================================================
// ObjectInfoTable Implementation
// ============================================================================

ObjectInfoTable::ObjectInfoTable(QWidget* parent)
    : QTableWidget(parent)
{
    setupTable();
}

void ObjectInfoTable::setupTable() {
    setColumnCount(7);
    setHorizontalHeaderLabels({
        "Name", "Mass (kg)", "Radius (m)", "X (m)", "Y (m)", "Z (m)", "Velocity (m/s)"
    });

    horizontalHeader()->setStretchLastSection(true);
    horizontalHeader()->setSectionResizeMode(QHeaderView::ResizeToContents);
    verticalHeader()->setVisible(false);
    setAlternatingRowColors(true);
    setSelectionBehavior(QAbstractItemView::SelectRows);
    setSelectionMode(QAbstractItemView::SingleSelection);
    setEditTriggers(QAbstractItemView::NoEditTriggers);
}

void ObjectInfoTable::updateBodies(const std::vector<CelestialBody*>& bodies) {
    setRowCount(static_cast<int>(bodies.size()));

    int row = 0;
    for (const auto* body : bodies) {
        if (body->isDestroyed()) continue;

        Vector3D pos = body->getPosition();
        Vector3D vel = body->getVelocity();
        double velocity = std::sqrt(vel.x * vel.x + vel.y * vel.y + vel.z * vel.z);

        setItem(row, 0, new QTableWidgetItem(QString::fromStdString(body->getName())));
        setItem(row, 1, new QTableWidgetItem(QString::number(body->getMass(), 'e', 2)));
        setItem(row, 2, new QTableWidgetItem(QString::number(body->getRadius(), 'e', 2)));
        setItem(row, 3, new QTableWidgetItem(QString::number(pos.x, 'e', 2)));
        setItem(row, 4, new QTableWidgetItem(QString::number(pos.y, 'e', 2)));
        setItem(row, 5, new QTableWidgetItem(QString::number(pos.z, 'e', 2)));
        setItem(row, 6, new QTableWidgetItem(QString::number(velocity, 'e', 2)));

        row++;
    }

    setRowCount(row);
    horizontalHeader()->setSectionResizeMode(QHeaderView::ResizeToContents);
}

// ============================================================================
// MainWindow Implementation
// ============================================================================

MainWindow::MainWindow(QWidget* parent)
    : QMainWindow(parent)
    , m_engine(std::make_unique<SimulationEngine>())
    , m_timer(new QTimer(this))
    , m_running(false)
{
    setWindowTitle("Gravity Simulator");
    resize(1600, 900);

    setupUI();
    setupMenuBar();
    setupStatusBar();
    loadInitialSimulation();

    // Connect timer
    connect(m_timer, &QTimer::timeout, this, &MainWindow::updateSimulation);
    m_timer->start(16);  // ~60 FPS
}

MainWindow::~MainWindow() = default;

void MainWindow::setupUI() {
    // Create central widget and main layout
    QWidget* centralWidget = new QWidget(this);
    setCentralWidget(centralWidget);

    QVBoxLayout* mainLayout = new QVBoxLayout(centralWidget);
    mainLayout->setContentsMargins(5, 5, 5, 5);
    mainLayout->setSpacing(5);

    // Create splitter for two rows
    QSplitter* rowSplitter = new QSplitter(Qt::Vertical, centralWidget);
    rowSplitter->setHandleWidth(3);

    // ========== First Row ==========
    QWidget* firstRowWidget = new QWidget(rowSplitter);
    QHBoxLayout* firstRowLayout = new QHBoxLayout(firstRowWidget);
    firstRowLayout->setContentsMargins(0, 0, 0, 0);
    firstRowLayout->setSpacing(5);

    // Left segment: Object info table
    QGroupBox* tableGroup = new QGroupBox("Objects", firstRowWidget);
    QVBoxLayout* tableLayout = new QVBoxLayout(tableGroup);
    m_objectTable = new ObjectInfoTable(tableGroup);
    tableLayout->addWidget(m_objectTable);

    // Right segment: Placeholder button
    QGroupBox* buttonGroup = new QGroupBox("Controls", firstRowWidget);
    QVBoxLayout* buttonLayout = new QVBoxLayout(buttonGroup);
    m_placeholderButton = new QPushButton("Add Object", buttonGroup);
    m_placeholderButton->setMinimumHeight(40);
    buttonLayout->addWidget(m_placeholderButton);
    buttonLayout->addStretch();

    firstRowLayout->addWidget(tableGroup, 2);  // 2/3 width
    firstRowLayout->addWidget(buttonGroup, 1);  // 1/3 width

    // ========== Second Row ==========
    QWidget* secondRowWidget = new QWidget(rowSplitter);
    QHBoxLayout* secondRowLayout = new QHBoxLayout(secondRowWidget);
    secondRowLayout->setContentsMargins(0, 0, 0, 0);
    secondRowLayout->setSpacing(5);

    // Three projection views
    m_xyView = new SimulationView(SimulationView::Projection::XY, secondRowWidget);
    m_xzView = new SimulationView(SimulationView::Projection::XZ, secondRowWidget);
    m_yzView = new SimulationView(SimulationView::Projection::YZ, secondRowWidget);

    secondRowLayout->addWidget(m_xyView);
    secondRowLayout->addWidget(m_xzView);
    secondRowLayout->addWidget(m_yzView);

    // Add rows to splitter
    rowSplitter->addWidget(firstRowWidget);
    rowSplitter->addWidget(secondRowWidget);
    rowSplitter->setStretchFactor(0, 1);
    rowSplitter->setStretchFactor(1, 2);

    mainLayout->addWidget(rowSplitter);

    // Control buttons at bottom
    QHBoxLayout* controlLayout = new QHBoxLayout();
    QPushButton* playPauseBtn = new QPushButton("Play", this);
    QPushButton* resetBtn = new QPushButton("Reset", this);

    connect(playPauseBtn, &QPushButton::clicked, this, &MainWindow::onPlayPause);
    connect(resetBtn, &QPushButton::clicked, this, &MainWindow::onReset);

    controlLayout->addWidget(playPauseBtn);
    controlLayout->addWidget(resetBtn);
    controlLayout->addStretch();

    mainLayout->addLayout(controlLayout);
}

void MainWindow::setupMenuBar() {
    QMenuBar* menuBar = this->menuBar();

    QMenu* fileMenu = menuBar->addMenu("&File");
    QAction* exitAction = fileMenu->addAction("E&xit");
    connect(exitAction, &QAction::triggered, this, &QMainWindow::close);

    QMenu* simMenu = menuBar->addMenu("&Simulation");
    QAction* playAction = simMenu->addAction("&Play/Pause");
    connect(playAction, &QAction::triggered, this, &MainWindow::onPlayPause);

    QAction* resetAction = simMenu->addAction("&Reset");
    connect(resetAction, &QAction::triggered, this, &MainWindow::onReset);

    QMenu* helpMenu = menuBar->addMenu("&Help");
    QAction* aboutAction = helpMenu->addAction("&About");
    connect(aboutAction, &QAction::triggered, [this]() {
        QMessageBox::about(this, "About Gravity Simulator",
            "Gravity Simulator v1.0\n"
            "A space objects gravity simulation application.\n\n"
            "Built with Qt6 and C++20.");
    });
}

void MainWindow::setupStatusBar() {
    QStatusBar* statusBar = this->statusBar();

    m_timeLabel = new QLabel("Time: 0.00 s", statusBar);
    m_objectCountLabel = new QLabel("Objects: 0", statusBar);

    statusBar->addWidget(m_timeLabel);
    statusBar->addWidget(m_objectCountLabel);
}

void MainWindow::loadInitialSimulation() {
    // Create a simple solar system-like setup
    std::vector<std::unique_ptr<CelestialBody>> bodies;

    // Sun-like body at origin
    auto sun = std::make_unique<CelestialBody>(
        "Sun",
        1.989e30,  // kg
        6.9634e8,  // m
        Vector3D(0, 0, 0),
        Vector3D(0, 0, 0)
    );

    // Earth-like body
    double earthDistance = 1.496e11;  // 1 AU
    double earthVelocity = 29780;     // m/s

    auto earth = std::make_unique<CelestialBody>(
        "Earth",
        5.972e24,  // kg
        6.371e6,   // m
        Vector3D(earthDistance, 0, 0),
        Vector3D(0, earthVelocity, 0)
    );

    // Mars-like body
    double marsDistance = 2.279e11;  // 1.52 AU
    double marsVelocity = 24070;     // m/s

    auto mars = std::make_unique<CelestialBody>(
        "Mars",
        6.39e23,  // kg
        3.3895e6, // m
        Vector3D(marsDistance, 0, 0),
        Vector3D(0, marsVelocity, 0)
    );

    bodies.push_back(std::move(sun));
    bodies.push_back(std::move(earth));
    bodies.push_back(std::move(mars));

    m_engine->initialize(std::move(bodies));
}

void MainWindow::updateSimulation() {
    if (!m_running) return;

    // Step simulation (1 second per step)
    m_engine->step(1.0);

    // Get current bodies
    std::vector<CelestialBody*> bodies = m_engine->getBodies();

    // Update views
    m_objectTable->updateBodies(bodies);
    m_xyView->setBodies(bodies);
    m_xzView->setBodies(bodies);
    m_yzView->setBodies(bodies);

    // Update status bar
    SimulationStats stats = m_engine->getStats();
    m_timeLabel->setText(QString("Time: %1 s").arg(stats.currentTime, 0, 'f', 2));
    m_objectCountLabel->setText(QString("Objects: %1").arg(stats.objectCount));
}

void MainWindow::onPlayPause() {
    m_running = !m_running;
    m_engine->setPaused(!m_running);

    // Find the play/pause button in menu and update it
    QMenuBar* menuBar = this->menuBar();
    QMenu* simMenu = menuBar->findChild<QMenu*>("Simulation");
    if (simMenu) {
        QList<QAction*> actions = simMenu->actions();
        if (!actions.isEmpty()) {
            actions[0]->setText(m_running ? "&Pause" : "&Play");
        }
    }
}

void MainWindow::onReset() {
    m_running = false;
    m_engine->reset();

    // Reload initial simulation
    loadInitialSimulation();

    // Update views
    std::vector<CelestialBody*> bodies = m_engine->getBodies();
    m_objectTable->updateBodies(bodies);
    m_xyView->setBodies(bodies);
    m_xzView->setBodies(bodies);
    m_yzView->setBodies(bodies);

    // Update status bar
    SimulationStats stats = m_engine->getStats();
    m_timeLabel->setText(QString("Time: %1 s").arg(stats.currentTime, 0, 'f', 2));
    m_objectCountLabel->setText(QString("Objects: %1").arg(stats.objectCount));
}

} // namespace gui
