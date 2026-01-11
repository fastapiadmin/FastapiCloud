<div align="center">
   <p align="center">
   <img src="./web/src/assets/imgs/logo-dark.svg" height="150" alt="logo"/>
</p>
   <h1 align="center" style="margin: 30px 0 30px; font-weight: bold;">FastapiCloud</h1>
   <h4 align="center">A full-stack web application framework with separated front-end and back-end, based on Fastapi and Vue3.</h4>
   <p align="center">
      <a href="https://gitee.com/tao__tao/FastapiCloud.git">
         <img src="https://gitee.com/tao__tao/FastapiCloud/badge/star.svg?theme=dark">
      </a>
      <a href="https://github.com/1014TaoTao/FastapiCloud.git">
         <img src="https://img.shields.io/github/stars/1014TaoTao/FastapiCloud?style=social">
      </a>
      <a href="https://gitee.com/tao__tao/FastapiCloud/blob/master/LICENSE">
         <img src="https://img.shields.io/badge/License-MIT-orange">
      </a>
      <img src="https://img.shields.io/badge/Python-≥3.10-blue">
   </p>
</div>

English | [Chinese](./README.md)

## Introduction to the FastapiCloud Project

### Project Overview

FastapiCloud is a full-stack open-source project aimed at helping developers quickly build web applications. The backend uses FastAPI + SQLModel + Alembic + JWT asynchronous programming to improve concurrency, simplify database operations, implement authentication and authorization, and manage versions. The frontend adopts Vue3 + Vite7 + Vue Router + Element Plus to achieve rapid construction and responsive development. It provides an all-in-one development solution, being efficient and convenient.

> Backend Technology Stack:

- **FastAPI**: Utilizes asynchronous programming features to enhance the application's concurrent processing capabilities.
- **SQLModel**: A simple and easy-to-use ORM tool that simplifies database operations.
- **Alembic**: A database migration tool for managing database versions.
- **JWT**: Used for authentication and authorization.

> Frontend Technology Stack:

- **Vue3**: A progressive JavaScript framework for building user interfaces.
- **Vite7**: A fast frontend build tool that supports hot reloading.
- **Vue Router**: Vue official router manager.
- **Axios**: A Promise-based HTTP client for sending requests.
- **Element Plus**: A Vue3-based UI component library that provides rich components.

### Main Features

- **Easy to Get Started**: Provides a complete project structure and sample code to reduce initial configuration time.
- **Modular Design**: Each component is developed independently for easy maintenance and expansion.
- **Comprehensive Documentation**: Detailed README and API documentation for easy learning and reference.
- **Community Support**: Completely open source. Welcome to submit issues and pull requests.

### Directory Structure

```sh
fastapicloud/
├─ alembic/          # Database migration tool
├─ apps/             # Backend application code
├─ core/             # Core configuration and utilities
├─ static/           # Static resources
├─ test/             # Test code
├─ utils/            # Utility functions
├─ web/              # Frontend code
├─ .env              # Environment variables
├─ alembic.ini       # Alembic configuration
├─ main.py           # Backend entry point
├─ requirements.txt  # Backend dependencies
├─ README.en.md      # English documentation
└─ README.md         # Chinese documentation
```

![service screenshot](./web/src/assets/imgs/image.png)

### Quick Start

- 1. Clone the project

  - git clone <https://gitee.com/tao__tao/FastapiCloud.git>

- 2. Install dependencies:

  - Backend dependencies:
    - cd fastapicloud
    - pip install -r requirements.txt
  - Frontend dependencies:
    - cd fastapicloud/web
    - pnpm install

- 3. Start the project:

  - Backend startup:
    - Generate and apply database migrations: python3 main.py migrate
    - Run backend service: python3 main.py run
  - Frontend startup:
    - cd fastapicloud/web
    - pnpm dev

- 4. Access the project:
  
  - Frontend address: <http://127.0.0.1:5173>
  - Backend API documentation: <http://127.0.0.1:8000/docs>
  - Username: `admin` Password: `123456`

### Special Thanks

Thanks to the contributions and support of the following projects, which have enabled the successful completion of this project:

- [FastAPI Project](https://github.com/fastapi/fastapi)
- [SqlModel Project](https://github.com/fastapi/sqlmodel)
- [Alembic Project](https://github.com/sqlalchemy/alembic)
- [PyJWT Project](https://github.com/jpadilla/pyjwt)
- [Vue3 Project](https://github.com/vuejs/vue)
- [Vite Project](https://github.com/vitejs/vite)
- [Element Plus Project](https://github.com/element-plus/element-plus)

### Participation and Support

Thank you for your attention and support! If you find this project helpful, please give us a Star! Your support is our driving force. At the same time, all developers are welcome to contribute and jointly improve this project.

## 🎨 WeChat Group

Below are the group QR codes, which can be used for technical exchanges and discussions on various issues encountered during the project usage. We sincerely hope that everyone can work together to optimize the project, actively discuss, and support each other!

### Group QR Codes

<table>
    <tr>
      <td><img src="https://gitee.com/tao__tao/FastDocs/raw/main/src/public/group.jpg"/></td>
      <td><img src="https://gitee.com/tao__tao/FastDocs/raw/main/src/public/wechatPay.jpg"/></td>
    </tr>
</table>
