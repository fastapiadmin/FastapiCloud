#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FastAPI Cloud 项目主入口
提供统一的服务管理和启动命令
"""

import typer
from typing import Optional
import subprocess
import sys
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent

# 创建Typer应用
app = typer.Typer(name="fastapicloud", help="FastAPI Cloud 项目管理工具")

# 可用服务列表
services = [
    "admin",
    "api-gateway",
    "config-service",
    "user-service"
]


@app.command(help="安装所有服务依赖")
def install():
    """安装所有服务依赖"""
    typer.echo("正在安装项目依赖...")
    
    # 安装根目录依赖
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        cwd=BASE_DIR,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        typer.echo(f"安装根目录依赖失败: {result.stderr}", err=True)
        sys.exit(1)
    
    typer.echo("根目录依赖安装成功")
    
    # 安装每个服务的特有依赖
    for service in services:
        service_dir = BASE_DIR / "services" / service
        requirements_file = service_dir / "requirements.txt"
        
        if requirements_file.exists():
            typer.echo(f"正在安装 {service} 服务依赖...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                cwd=service_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                typer.echo(f"安装 {service} 依赖失败: {result.stderr}", err=True)
            else:
                typer.echo(f"{service} 依赖安装成功")
        else:
            typer.echo(f"跳过 {service}，未找到 requirements.txt")
    
    typer.echo("所有依赖安装完成")


@app.command(help="启动指定服务")
def start(
    service: str = typer.Argument(..., help="要启动的服务名称"),
    host: str = typer.Option("0.0.0.0", help="服务监听地址"),
    port: Optional[int] = typer.Option(None, help="服务监听端口"),
    reload: bool = typer.Option(True, help="是否自动重载"),
    debug: bool = typer.Option(True, help="是否开启调试模式")
):
    """启动指定服务"""
    if service not in services:
        typer.echo(f"错误: 未知服务 '{service}'", err=True)
        typer.echo(f"可用服务: {', '.join(services)}")
        sys.exit(1)
    
    service_dir = BASE_DIR / "services" / service
    main_file = service_dir / "main.py"
    
    if not main_file.exists():
        typer.echo(f"错误: 服务 '{service}' 的 main.py 文件不存在")
        sys.exit(1)
    
    typer.echo(f"正在启动 {service} 服务...")
    
    # 构建启动命令
    cmd = [
        sys.executable,
        "-m", "uvicorn",
        "main:app",
        f"--host", host,
        f"--reload" if reload else "",
        f"--log-level", "debug" if debug else "info"
    ]
    
    # 添加端口参数（如果指定）
    if port:
        cmd.extend([f"--port", str(port)])
    
    # 过滤掉空字符串
    cmd = [arg for arg in cmd if arg]
    
    # 启动服务
    subprocess.run(cmd, cwd=service_dir)


@app.command(help="启动所有服务")
def start_all(
    host: str = typer.Option("0.0.0.0", help="服务监听地址"),
    reload: bool = typer.Option(True, help="是否自动重载")
):
    """启动所有服务"""
    typer.echo("正在启动所有服务...")
    
    for service in services:
        service_dir = BASE_DIR / "services" / service
        main_file = service_dir / "main.py"
        
        if main_file.exists():
            typer.echo(f"正在启动 {service} 服务...")
            
            # 构建启动命令
            cmd = [
                sys.executable,
                "-m", "uvicorn",
                "main:app",
                f"--host", host,
                f"--reload" if reload else "",
                f"--log-level", "info"
            ]
            
            # 过滤掉空字符串
            cmd = [arg for arg in cmd if arg]
            
            # 启动服务（后台运行）
            subprocess.Popen(cmd, cwd=service_dir)
        else:
            typer.echo(f"跳过 {service}，未找到 main.py 文件")
    
    typer.echo("所有服务启动完成")


@app.command(help="停止所有服务")
def stop_all():
    """停止所有服务"""
    typer.echo("正在停止所有服务...")
    
    # 使用 pkill 停止所有 uvicorn 进程
    subprocess.run(["pkill", "-f", "uvicorn"], capture_output=True, text=True)
    
    typer.echo("所有服务已停止")


@app.command(help="显示项目信息")
def info():
    """显示项目信息"""
    typer.echo("FastapiCloud 项目信息")
    typer.echo("=" * 30)
    typer.echo(f"项目根目录: {BASE_DIR}")
    typer.echo(f"可用服务: {', '.join(services)}")
    typer.echo(f"Python 版本: {sys.version}")
    typer.echo("=" * 30)


if __name__ == "__main__":
    app()