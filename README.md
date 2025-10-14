![onette_full](https://github.com/alteredgenome/orchenet/blob/main/onette_full.png?raw=true)
# **OrcheNet \- The Network Orchestrator**

## **📖 Overview**

**OrcheNet** is a self-hosted, web-based management tool designed to centrally manage a fleet of network devices from various vendors. Its core architectural principle is an agent-based "phone home" model, which allows devices to be managed securely without requiring public IP addresses or inbound firewall rules.  
Configuration is king. OrcheNet treats device configurations as the source of truth, representing them in a structured, vendor-agnostic **YAML format**. This allows for easy versioning, backup, and consistent application of settings across your infrastructure.  
The project is designed to be highly modular, with initial support for **MikroTik RouterOS** and a clear path to integrate other major vendors.

## **✨ Core Features**

* **Agent-Based Communication:** Devices actively check in with the server to fetch tasks, eliminating the need for direct access from the central server.  
* **YAML Configuration:** Manage complex device settings through simple, human-readable YAML files.  
* **Vendor Agnostic:** A flexible abstraction layer allows for easy expansion to support new hardware vendors.  
* **Web-Based UI:** A clean and modern frontend for viewing device status, editing configurations, and monitoring tasks.  
* **Secure:** Communication between the agent and server is handled over HTTPS.

## **🛠️ Technology Stack**

* **Backend:** **Python** with **FastAPI** for a high-performance, asynchronous API.  
* **Database:** **SQLAlchemy ORM** with an initial **SQLite** backend for simplicity, designed for easy migration to PostgreSQL.  
* **Frontend:** A modern, responsive single-page application (SPA) built with **Svelte** or **React**.  
* **Agent:** A lightweight **Python** script deployed on each managed device.

## **📂 Project Structure**

The repository is organized into three main components:  
orchenet/  
├── backend/       \# FastAPI server, API logic, database models, and vendor modules.  
├── frontend/      \# Svelte/React SPA for the user interface.  
└── agent/         \# Python agent script to be deployed on managed devices.

## **🚀 Project Roadmap**

OrcheNet is currently in the initial development phase. The high-level implementation plan is as follows:

1. **\[✔️\] Step 1: Initialize Project Structure**  
2. **\[ \] Step 2: Backend \- Database Models & Vendor Abstraction**  
3. **\[ \] Step 3: Backend \- Core API Endpoints**  
4. **\[ \] Step 4: Agent \- Scaffolding & Server Check-in Logic**  
5. **\[ \] Step 5: Initial Integration Testing**  
6. **\[ \] Step 6: Backend \- YAML-to-Command Translation Logic**  
7. **\[ \] Step 7: Frontend \- Scaffolding and Device Listing**  
8. **\[ \] Step 8: Implement Full End-to-End Configuration Feature**

The ultimate goal is to support the following vendors:

* MikroTik (RouterOS) \- *Initial Target*  
* Fortinet (FortiGate, FortiSwitch, FortiAP)  
* WatchGuard (Firebox, APs)  
* Ubiquiti (UDM, UAP, USW)

## **🤝 Contributing**

*(Details on how to contribute will be added once the initial project structure is more mature.)*
