# Build & Run

## 1. Install Qt6
Download: https://www.qt.io/download-qt-installer

## 2. Build
```cmd
cd program\build
cmake -DUSE_QT6=ON ..
cmake --build . --config Debug
```

## 3. Run
```cmd
build\Debug\GravitySimulator.exe
```

## If DLL errors:
```cmd
cd program\build\Debug
windeployqt GravitySimulator.exe
```
