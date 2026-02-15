Ultimate PC Monitor

Ultimate PC Monitor is a full-stack real-time hardware monitoring system that visualizes live computer telemetry in a premium animated dashboard.

The project consists of a Python Flask backend that collects hardware metrics and a modern JavaScript frontend that renders them with animated charts and a reactive WebGL-style interface.

It monitors CPU, RAM, Disk, GPU and Network activity in real time and presents the data in a visually rich interface designed to feel modern, responsive and high-end.

The backend gathers system data using psutil and GPU libraries, exposes it through a REST API and streams live telemetry to the frontend.
The frontend periodically fetches this data and renders animated visualizations using Chart.js and GSAP with a custom interactive background.

Project structure:

backend/ — Flask hardware telemetry API
frontend/ — animated monitoring dashboard UI

This repository contains both parts of the system in a single full-stack project.

The project is functional and actively designed for further expansion such as historical metrics, alerts, multi-device monitoring and advanced GPU analytics.
