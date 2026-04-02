# Smart Sustainable Campus Management System (SSC-MS)

## 1. Abstract
 
The Smart Sustainable Campus Management System (SSC-MS) is a comprehensive digital platform designed to address the pressing environmental challenges faced by modern educational institutions. Campuses are micro-cities that consume vast amounts of resources—including electricity and water—while generating significant waste and carbon emissions. This project implements a technological solution to systematically track, manage, and analyze these environmental metrics. By leveraging a robust web architecture, SSC-MS provides real-time data aggregation, automatic carbon emission calculations, and an interactive sustainability dashboard, empowering administrators to make data-driven decisions toward creating a greener, more sustainable campus environment.

---

## 2. Introduction

Monitoring sustainability is no longer optional for large institutions; it is a critical necessity. University campuses operate numerous facilities, laboratories, and residential halls, leading to high resource consumption and significant environmental footprints. Traditionally, the management of energy, water, and waste data has been fragmented, relying on manual entry or isolated spreadsheets. This lack of centralized monitoring makes it difficult to assess overall environmental impact or identify areas for improvement.

The Smart Sustainable Campus Management System (SSC-MS) introduces a centralized, digital approach to environmental management. By providing a unified platform for logging utility metrics and waste generation, the system transforms raw data into actionable insights through dynamic visualizations and automated sustainability scoring.

---

## 3. Sustainable Development Goals (SDGs)

This project directly aligns with and contributes to several of the United Nations Sustainable Development Goals (SDGs):

- **SDG 6 – Clean Water and Sanitation:** The system tracks water usage across different campus buildings, helping administrators identify leaks, reduce unnecessary consumption, and promote water conservation strategies.
- **SDG 7 – Affordable and Clean Energy:** By monitoring electricity consumption dynamically, the system highlights high-usage areas, encouraging energy efficiency and the potential transition to renewable energy sources.
- **SDG 11 – Sustainable Cities and Communities:** Treating the campus as a community, the platform fosters sustainable infrastructure management, minimizing the collective environmental footprint of the institution.
- **SDG 12 – Responsible Consumption and Production:** The waste management module tracks digital records of dry, wet, electronic, and plastic waste, promoting recycling initiatives and responsible disposal practices.
- **SDG 13 – Climate Action:** The system automatically converts energy usage into measurable carbon emissions, providing clear metrics to help the campus reduce its greenhouse gas output.

---

## 4. Problem Statement

Modern university campuses consume large amounts of electricity and water while producing extensive amounts of varied waste. Despite growing global awareness regarding climate change, most institutions lack integrated, centralized systems to monitor their daily sustainability data. Without a unified digital infrastructure, facility managers cannot effectively measure their carbon footprint, spot resource anomalies, or gauge the success of green initiatives. There is an urgent need for a cohesive digital solution capable of aggregating environmental data and presenting it in an understandable, actionable format.

---

## 5. Project Objectives

The primary objectives of the SSC-MS project are to:

- Track and log energy consumption (in kWh) across campus facilities.
- Monitor water usage (in Litres) continuously over time.
- Record and categorize waste generation (in kg) into specific types (e.g., dry, wet, plastic, e-waste).
- Calculate carbon emissions automatically utilizing standardized conversion formulas.
- Visualize campus sustainability metrics through a dynamic, interactive web dashboard.

---

## 6. System Overview

The SSC-MS operates as a centralized web application. The system supports distinct user roles (ADMIN and STAFF) to ensure secure data handling. Authorized personnel can input daily or monthly logs detailing how much energy or water a specific building consumed, or how much waste was generated.

Once data is submitted via the secure API, the backend processes the information—automatically calculating the resulting carbon emissions. This processed data is then fed into the Dashboard Analytics engine, which aggregates the campus's total resource usage, categorizes waste distribution, and generates a dynamic "Sustainability Score" to reflect the overall environmental health of the institution.

---

## 7. System Architecture

The architecture follows a streamlined, decoupled, three-tier structure:

- **Presentation Layer (Django Templates + Bootstrap + Chart.js):** Acts as the user interface. It renders the web dashboard, manages user interactions, and visualizes data using responsive charts and metric cards.
- **Application Layer (Django + Django REST Framework):** The core logic engine. It handles HTTP requests, enforces JWT (JSON Web Token) authentication, processes business logic (extracted to `utils.py` for cleanly scalable computation of scores and trends), and routes API data.
- **Data Layer (SQLite Database):** The persistence layer. Chosen for prototype simplicity, it safely stores all user accounts, environmental records, and relationships.

---

## 8. Technology Stack

- **Python:** The core backend programming language, chosen for its readability and strong ecosystem for data processing.
- **Django:** A high-level Python web framework that encourages rapid development and clean, pragmatic design.
- **Django REST Framework (DRF):** Utilized to build robust, secure API endpoints for data ingestion.
- **JWT Authentication (SimpleJWT):** Ensures secure, stateless API access, verifying that only authorized campus staff can manipulate data.
- **SQLite:** A lightweight, file-based relational database ideal for rapid prototyping and testing.
- **Bootstrap 5:** Integrated seamlessly alongside custom Vanilla CSS for robust grid responsiveness (`row`, `col`) without interfering with premium glassmorphism aesthetics.
- **Chart.js:** A JavaScript charting library used to render the interactive bar, line, and pie charts on the dashboard.

---

## 9. Database Design

The system relies on a relational database approach consisting of four primary models:

1.  **User:** A custom authentication model that extends Django's base user to include a specific `role` field (ADMIN or STAFF).
2.  **EnergyUsage:** Stores `building_name`, `units_consumed` (kWh, protected by `MinValueValidator`), `month`, and the `created_by` relationship. It includes an overridden save method to automatically deduce carbon output.
3.  **WaterUsage:** Stores `building_name`, `litres_consumed` (protected by `MinValueValidator`), `date`, and the `created_by` relationship.
4.  **WasteRecord:** Stores `waste_type` (restricted via choices), `quantity_kg` (protected by `MinValueValidator`), `date`, and the `created_by` relationship.

**Carbon Emission Calculation:**
When an `EnergyUsage` record is saved, the database automatically calculates and stores the carbon emission using the formula:

> `carbon_emission = units_consumed × 0.82`

---

## 10. System Modules

- **Authentication Module:** Manages secure login flows, JWT token lifecycle (access/refresh), and ensures only ADMINs can register new STAFF accounts.
- **Energy Monitoring Module:** Provides secure endpoints to create, read, update, and delete electricity usage logs.
- **Water Monitoring Module:** Handles the ingestion and tracking of campus water consumption data.
- **Waste Management Module:** Logs waste generation events, explicitly categorizing them to track recycling and disposal metrics.
- **Dashboard and Analytics Module:** Aggregates data across all physical modules, returning mathematical totals and historical arrays for frontend visualization.

---

## 11. Dashboard Analytics

The central dashboard acts as the primary viewing pane for stakeholders, displaying:

- **Total Energy Consumption:** The sum of all recorded electricity usage in kWh.
- **Total Water Usage:** The sum of all recorded water consumption in Litres.
- **Waste Distribution:** A categorized breakdown of waste types in kg.
- **Carbon Emissions:** The total calculated campus carbon footprint in kg of CO2.
- **Sustainability Score & Status:** A dynamic health metric out of 100, visually mapped to an actionable Green (Good), Yellow (Moderate), or Red (Poor) status indicator. The dashboard also features contextual environmental tips.

**Sustainability Score Formula:**
The campus begins with a perfect score of 100, which is reduced based on environmental penalties:

> `Score = 100 - (carbon_emission × 0.01 + total_waste × 0.02)`

---

## 12. User Roles and Permissions

Security and data integrity are maintained through strict Role-Based Access Control (RBAC):

- **ADMIN:** Has full read and write access across the entire system. Only ADMINs can create new STAFF users, and only ADMINs are permitted to delete existing environmental records.
- **STAFF:** Can securely log in, view the dashboard, and create/submit new environmental records. However, they are strictly prohibited from deleting records or creating new users.

---

## 13. Features of the System

- **Environmental Data Logging:** Seamless digital entry for utility and waste metrics with robust model validation prohibiting negative entries.
- **Automated Carbon Emission Calculation:** Eliminates manual estimation errors.
- **Dynamic Sustainability Score:** Provides an instant, understandable metric of campus health along with dynamic text indicator prompts.
- **Search & Filter:** Debounce-controlled text inputs enable instant building keyword filtering alongside historical month and waste-type toggles.
- **CSV Exporter:** Directly download the seamlessly filtered records into CSV format for downstream Excel evaluation.
- **Interactive Charts:** Trend visualization over time for all three core metrics using Chart.js.
- **Role-Based Access Control (RBAC):** Hierarchical data security.
- **Centralized Web Dashboard:** A beautiful, single pane of glass for all campus sustainability insights, natively leveraging a Bootstrap responsive grid.

---

## 14. How to Run the Project

To execute the application locally, ensure Python is installed, then follow these steps from the project root directory:

1. **Activate Virtual Environment (if applicable):**
   ```bash
   .\venv\Scripts\Activate
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run Database Migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
4. **Create a Superuser (ADMIN):**
   ```bash
   python manage.py createsuperuser
   ```
5. **Start the Development Server:**
   ```bash
   python manage.py runserver
   ```
   Access the application by navigating to `http://127.0.0.1:8000/` in a web browser.

---

## 15. Testing and Validation

The SSC-MS was subjected to rigorous end-to-end verification utilizing multiple testing strategies:

- **API Testing:** Django Test Clients were used to validate HTTP response codes, endpoint isolation, JWT enforcement, and model saving logic.
- **Manual Blackbox Testing:** A simulated end-user directly navigated the frontend UI, executing the login workflow, form submissions, and data interaction without encountering backend tracebacks.
- **Browser Testing:** Confirmed cross-browser rendering compatibility for Bootstrap 5 components and Chart.js graphics.
- **Dashboard Verification:** Mathematical aggregation and UI state persistence (including empty-database failsafes) were heavily inspected and validated.

---

## 16. Future Improvements

While this prototype handles core tracking efficiently, future production-ready iterations could implement:

- **IoT Sensor Integration:** Automatically pulling real-time water and energy data from smart campus meters directly into the backend.
- **AI-based Sustainability Predictions:** Utilizing machine learning to forecast future energy spikes or waste overflow, allowing preemptive scaling.
- **Mobile Application:** A React Native counterpart to allow facility managers to log data directly on-site using their phones.
- **Multi-Campus Support:** Upgrading the database structure to a Multi-Tenant architecture so institutional networks can compare sustainability across various geographic campuses.

---

## 17. Conclusion

The Smart Sustainable Campus Management System (SSC-MS) successfully bridges the gap between environmental science and computer science. By digitizing the monitoring of critical resources—energy, water, and waste—the application provides a scalable, automated solution to environmental tracking. Through dynamic visualization and mathematical scoring, the system empowers academic institutions to actively understand their ecological footprint, definitively proving that modern web architecture can be a powerful tool for driving meaningful climate action and sustainability.
