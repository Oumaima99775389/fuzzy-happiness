# Smart Transport Box — Initial Architecture

## Objective
Monitor the conditions experienced by sensitive goods during transport.

## Components
- ESP32: collect sensor measurements.
- Raspberry Pi: run the local backend and persist journey data.
- MQTT: transport telemetry over the local Wi-Fi network.
- BLE: provide nearby readings to the driver's mobile app.
- Backend: validate measurements and detect threshold violations.
- Database: preserve readings, journeys, and events.
- ML: estimate future temperature-excursion risk.
- CI/CD: automate tests and build reproducible deployments.

## Initial development strategy
Develop and test the backend using simulated telemetry before
integrating the physical ESP32.

## Constraints
- Local-first deployment.
- No required paid cloud infrastructure.
- Missing data must not be treated as proof of safe conditions.