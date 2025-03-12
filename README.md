# SE_PROJECT Directory Structure

This document provides an overview of the directory structure for the SE_PROJECT Django application, detailing the functionality and contents of each directory.
SE_PROJECT/
├── indoor_sports/                # Core application modules (Django apps)
│   ├── indoor_sports/            # Main application, coordinating functionalities across other apps
│   │   ├── __init__.py           # Initialization file for the indoor_sports app
│   │   ├── asgi.py               # Configuration for ASGI (Asynchronous Server Gateway Interface) server
│   │   ├── settings.py           # Central configuration for the project (databases, middleware, installed apps, etc.)
│   │   ├── urls.py               # Routes URLs to the appropriate views across the project
│   │   ├── wsgi.py               # Configuration for WSGI server (used for communication with the web server)
│   │   ├── views.py              # Generic view functions coordinating various application requests
│   ├── accounts/                 # User account management app
│   │   ├── migrations/           # Database migration files for accounts
│   │   ├── __init__.py           # Initialization file for the accounts app
│   │   ├── admin.py              # Admin interface configuration for user accounts
│   │   ├── apps.py               # Application configuration class for the accounts app
│   │   ├── models.py             # ORM models for user account-related database tables
│   │   ├── tests/                # Unit tests for the accounts app
│   │   ├── urls.py               # Accounts-specific URL routing
│   │   ├── views.py              # View functions for user accounts
│   ├── bookings/                 # Booking and reservation management
│   │   ├── ...                   # Same structure as the accounts app
│   ├── dashboards/               # Features for data visualization and reporting
│   │   ├── ...                   # Same structure as the accounts app
│   ├── equipment/                # Equipment-related management
│   │   ├── ...                   # Same structure as the accounts app
│   ├── login/                    # User login and authentication mechanisms
│   │   ├── ...                   # Same structure as the accounts app
│   ├── memberships/              # Membership and user management 
│   │   ├── ...                   # Same structure as the accounts app
│   ├── my_referrals/             # Referral program management
│   │   ├── ...                   # Same structure as the accounts app
│   ├── notifications/            # Notifications-related management
│   │   ├── ...                   # Same structure as the accounts app
│   ├── payments/                 # Payment processing functionalities
│   │   ├── ...                   # Same structure as the accounts app
│   ├── ratings/                  # User ratings and reviews management
│   │   ├── ...                   # Same structure as the accounts app
│   ├── registration/             # User registration features
│   │   ├── ...                   # Same structure as the accounts app
│   ├── sports/                   # Sports-related management
│   │   ├── ...                   # Same structure as the accounts app
├── templates/                    # Project-wide templates for rendering web pages
│   ├── ...                       # Other app-specific templates
├── static/                       # Global static files shared across apps
│   ├── css/                      # Global stylesheets
│   ├── js/                       # Global JavaScript files
│   ├── img/                      # Global images
├── Planning Documents/           # Contains project planning documents
├── Minutes of Meeting/           # Meeting notes and records
├── .gitignore                    # Specifies files/directories to ignore in version control
├── README.md                     # General project overview and documentation


### Description of Key Components

1. indoor_sports/

        This is the core folder containing the main modules of your Django project. It coordinates functionalities across various feature-specific apps.

        indoor_sports/ (inner folder):

        __init__.py Indicates that the folder is a Python package, enabling module imports.

        asgi.py Configures the ASGI server. Useful for handling asynchronous requests and real-time features.

        settings.py Holds the central configuration for the whole project. This includes settings for databases, middleware, installed apps, static files, and more.

        urls.py Maps URL patterns to view functions. Acts as the routing table of your application.

        wsgi.py Sets up the WSGI communication between your web server and Django. This is key in production deployments.

        views.py Contains generic view functions that coordinate requests between different parts of the project. Although this file can be expanded or refactored into app-specific logic, it serves as a central hub for handling certain global actions.

2. accounts/

        This app is dedicated to user account management. It encompasses functionalities like user registration, profile updates, and administration of user data.

        Key Sub-components:

        migrations/ Houses files that record changes to the database schema. Essential for evolving your models without manual database intervention.

        __init__.py Marks the directory as a Python package.

        admin.py Registers models with Django’s admin interface for easier management of user accounts.

        apps.py Configures the app with settings such as the app name and label.

        models.py Contains the ORM models that define the structure for user data.

        urls.py Specific URL configurations that direct account-related web requests to the correct views.

        views.py Holds functions or class-based views to process and respond to user account actions.

        tests/ Contains unit tests that verify the correctness of your account functionalities.

3. bookings/

        Handles the booking and reservation processes. The structure mirrors that of the accounts app to maintain consistency.

        Functionalities:

        Managing reservations or event scheduling.

        Defining models related to booking details.

        Handling the booking process through view functions.

        Providing URL routes dedicated to booking pages and operations.

        Testing modules to ensure booking logic remains robust.

4. dashboards/

        This app focuses on data visualization and reporting, providing insights based on user activities and usage statistics.

        Functionalities:

        Aggregating data for charts and dashboards.

        Defining models for storing computed metrics.

        Crafting views that render statistical summaries.

        Serving up dashboards through dedicated URL endpoints.

5. equipment/

        Manages all aspects of equipment-related information, such as inventory tracking and maintenance schedules.

        Functionalities:

        Recording equipment details via models.

        Providing tools for checking equipment availability.

        Routing requests to views that help manage equipment reservations and status updates.

        Writing tests to protect against faulty operations or incorrect status updates.

6. login/

        This app handles user authentication mechanisms.

        Functionalities:

        Managing login forms and sessions.

        Integrating with accounts for authentication.

        Ensuring secure login via standardized testing and middleware (if any).

7. memberships/

        Deals with membership functionalities and extended user management.

        Functionalities:

        Setting up membership tiers or different access levels.

        Managing membership subscriptions, renewals, and cancellations.

        Testing membership logic to ensure consistency with business rules.

8. my_referrals/

        Focuses on referral program management—tracking referrals and rewarding users.

        Functionalities:

        Storing referral data in dedicated models.

        Handling business logic in view functions.

        Routing referral-related URLs for proper link tracking.

        Testing the referral paths and rewards logic.

9. notifications/

        Responsible for sending, storing, and managing notifications to users.

        Functionalities:

        Defining notification models to log in-app or external alerts.

        Coordinating with views to dispatch notifications.

        Testing that notifications are correctly triggered on specific events.

10. payments/

        Handles all payment processing and management.

        Functionalities:

        Managing transactions using secure payment gateways.

        Recording paid orders or subscriptions in models.

        Routing payment-related requests.

        Incorporating thorough testing for payment flows and error-checking.

11. ratings/

        Manages user ratings and reviews.

        Functionalities:

        Setting up models to capture and store reviews.

        Including views that allow users to submit and view ratings.

        Providing URL endpoints for rating interactions.

        Testing to ensure the rating system works as expected.

12. registration/

        Manages user sign-up processes.

        Functionalities:

        Handling forms and their validation for new user registrations.

        Integrating with accounts for profile creation.

        Routing registration-related URLs.

        Testing registration workflows to prevent issues during sign-up.

13. sports/

        Handles management of sports-related functionalities.

        Functionalities:

        Recording details of sports, leagues, or events in models.

        Providing interfaces for users to browse or select sports.

        Routing sports-specific URLs.

        Testing that sports data integrates seamlessly with overall booking and dashboard modules.

14. templates/

        This directory contains project-wide HTML templates for rendering web pages.

        Details:

        Global Templates: Files like base.html serve as a layout foundation across the site.

        App-Specific Templates: Can include subfolders for dedicated views or UI components linked to specific apps.

15. static/

        Hosts global static files that are shared across apps.

        Sub-directories:

        css/: Global stylesheets.

        js/: Global JavaScript files.

        img/: Global images and icons used by various templates.

        These files enhance front-end interactivity and styling while keeping resource management centralized.

16. Planning Documents/

        Contains project planning and specification files.

        Details:

        Projects’ feature plans, architectural designs, and technical specifications are documented here.

        Acts as a reference point for current and future development phases.

17. Minutes of Meeting/

        Logs records of project meetings.

        Details:

        Each meeting’s notes, decisions, action items, and deadlines.

        Useful for tracking progress and ensuring accountability throughout team discussions.

18. .gitignore

        Specifies which files and directories should not be tracked in version control.

        Purpose:

        Keeps temporary files, compiled code, and sensitive configuration details out of your Git history.

19. README.md

        Provides a general overview of the project.

        Details:

        Includes setup instructions, architectural overviews, and general documentation.

        Serves as the starting guide for new developers and stakeholders.


