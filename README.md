<div align="center">
   <p align="center">
   <img src="./web/src/assets/imgs/logo-dark.svg" height="150" alt="logo"/>
</p>
   <h1 align="center" style="margin: 30px 0 30px; font-weight: bold;">FastapiCloud</h1>
   <h4 align="center">基于 Fastapi 和 Vue3 的前后端分离全栈 Web 应用框架。</h4>
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

## FastapiCloud项目介绍

### 项目概述

FastapiCloud是一个全栈开源项目，旨在帮助开发者快速构建Web应用。后端使用FastAPI + SQLModel + Alembic + JWT异步编程，提高并发能力，简化数据库操作，实现身份认证和授权，以及版本管理。前端采用Vue3 + Vite7 + Vue Router + Element Plus实现快速构建和响应式开发。它提供了一站式开发解决方案，高效便捷。

> 后端技术栈：

- **FastAPI**: 利用异步编程特性增强应用的并发处理能力。
- **SQLModel**: 一个简单易用的ORM工具，简化数据库操作。
- **Alembic**: 一个数据库迁移工具，用于管理数据库版本。
- **JWT**: 用于身份验证和授权。

> 前端技术栈：

- **Vue3**: 一个渐进式JavaScript框架，用于构建用户界面。
- **Vite7**: 一个快速的前端构建工具，支持热重载。
- **Vue Router**: Vue官方路由管理器。
- **Axios**: 一个基于Promise的HTTP客户端，用于发送请求。
- **Element Plus**: 一个基于Vue3的UI组件库，提供丰富的组件。

### 主要功能

- **易于上手**：提供完整的项目结构和示例代码，减少初始配置时间。
- **模块化设计**：每个组件独立开发，便于维护和扩展。
- **完善的文档**：详细的README和API文档，便于学习和参考。
- **社区支持**：完全开源，欢迎提交issue和pull request。

### 目录结构

```sh
fastapicloud/
├─ alembic/          # 数据库迁移工具
├─ apps/             # 后端应用代码
├─ core/             # 核心配置和工具
├─ static/           # 静态资源
├─ test/             # 测试代码
├─ utils/            # 工具函数
├─ web/              # 前端代码
├─ .env              # 环境变量配置
├─ alembic.ini       # Alembic配置
├─ main.py           # 后端入口文件
├─ requirements.txt  # 后端依赖
├─ README.en.md      # 英文文档
└─ README.md         # 中文文档
```

![服务截图](./web/src/assets/imgs/image.png)

### 快速开始

- 1. 克隆项目

  - git clone <https://gitee.com/tao__tao/FastapiCloud.git>

- 2. 安装依赖：

  - 后端依赖：
    - cd fastapicloud
    - pip install -r requirements.txt
  - 前端依赖：
    - cd fastapicloud/web
    - pnpm install

- 3. 启动项目：

  - 后端启动：
    - 生成并执行数据库迁移：python3 main.py migrate
    - 运行后端服务：python3 main.py run
  - 前端启动：
    - cd fastapicloud/web
    - pnpm dev

- 4. 访问项目：
  
  - 前端地址：<http://127.0.0.1:5173>
  - 后端API文档：<http://127.0.0.1:8000/docs>
  - 账号：`admin` 密码：`123456`

### 特别感谢

感谢以下项目的贡献和支持，使本项目能够顺利完成：

- [FastAPI 项目](https://github.com/fastapi/fastapi)
- [SqlModel 项目](https://github.com/fastapi/sqlmodel)
- [Alembic 项目](https://github.com/sqlalchemy/alembic)
- [PyJWT 项目](https://github.com/jpadilla/pyjwt)
- [Vue3 项目](https://github.com/vuejs/vue)
- [Vite 项目](https://github.com/vitejs/vite)
- [Element Plus 项目](https://github.com/element-plus/element-plus)

### 参与和支持

感谢您的关注和支持！如果您认为本项目对您有帮助，请给我们一个Star！您的支持是我们前进的动力。同时，欢迎所有开发者贡献代码，共同完善这个项目。

## 🎨 微信群

以下是交流群二维码，可用于技术交流和讨论项目使用过程中遇到的各种问题。真诚希望大家能够共同优化项目，积极讨论，互相支持！

### 群聊二维码

<table>
    <tr>
      <td><img src="https://gitee.com/tao__tao/FastDocs/raw/main/src/public/group.jpg"/></td>
      <td><img src="https://gitee.com/tao__tao/FastDocs/raw/main/src/public/wechatPay.jpg"/></td>
    </tr>
</table>
