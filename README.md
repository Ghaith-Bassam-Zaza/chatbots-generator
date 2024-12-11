# Chatbots Generator

Welcome to the Chatbots Generator project! This project provides a comprehensive framework for creating, managing, and deploying AI-powered chatbots using Flask, OpenAI’s API, and PostgreSQL. With its scalable architecture and user-friendly interface, Chatbots Generator simplifies chatbot creation for various applications.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Demo](#demo)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Setup Steps](#setup-steps)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Creating a New Bot](#creating-a-new-bot)
  - [Managing Bots](#managing-bots)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Introduction

Chatbots Generator is designed to create custom chatbots by scraping website content from a provided URL and embedding the bot into a website. The bots utilize OpenAI's API for intelligent responses, making it easy to generate robust and context-aware chatbots tailored to specific website content.

## Features

- **User-Friendly Dashboard**: Manage chatbot creation and deployment through an intuitive interface.
- **Multi-User Support**: Supports multiple users with individual chatbot configurations.
- **Advanced NLP**: Leverages OpenAI’s API for highly intelligent chatbot responses.
- **Database Integration**: Uses PostgreSQL for reliable and scalable data management.
- **Easy Embedding**: Generate scripts to seamlessly integrate bots into any website.
- **Scalable and Secure**: Designed to handle multiple bots and user data securely.

## Demo

Watch the [Demo Video](https://drive.google.com/file/d/11eX9TuQooA7hC-SxRFeCuWjYZR0zgTEj/view?usp=sharing) to see the Chatbots Generator in action!

## Installation

### Prerequisites

Ensure you have the following installed:
- **Python** (3.7 or higher)
- **PostgreSQL**
- **Flask**
- **OpenAI API Key**

### Setup Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Ghaith-Bassam-Zaza/chatbots-generator.git
   cd chatbots-generator
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up PostgreSQL**:
   - Create two PostgreSQL databases: one for chatbot data (`DATABASE_URL`) and another for user management (`WEB_DATABASE_URL`).
   - Update the database configuration in `CONSTANTS.py`.

## Configuration

Update the `CONSTANTS.py` file in the project root with the following variables:

```python
FLASK_APP = "app.py"
FLASK_ENV = "development"
DATABASE_URL = "postgresql://<username>:<password>@localhost/<chatbot_db_name>"
WEB_DATABASE_URL = "postgresql://<username>:<password>@localhost/<web_db_name>"
OPENAI_API_KEY = "your_openai_api_key"
```

Replace `<username>`, `<password>`, `<chatbot_db_name>`, and `<web_db_name>` with your PostgreSQL credentials and respective database names.
the DATABASE_URL is the database that will store the chatbot data and the WEB_DATABASE_URL is the database that will store the user data.

## Usage

Run the application using:

```bash
flask run
```

The application will be accessible at `http://127.0.0.1:5000`.

### Creating a New Bot
1. Open the application in your web browser.
2. Log in and navigate to the chatbot creation page.
3. Enter the URL or required details to generate a new bot.
4. Copy the provided script to embed the chatbot into your website.

### Managing Bots
- Access the dashboard to view all your bots.
- Edit or delete bots as needed.

## Contributing

We welcome contributions! Follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contact

For questions or support, please contact Ghaith Bassam Zaza at [ghaith.zaza@outlook.com](mailto:ghaith.zaza@outlook.com).

