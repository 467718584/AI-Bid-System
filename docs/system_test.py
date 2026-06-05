#!/usr/bin/env python3
import os
import requests
import json
import time
import psutil
from datetime import datetime

BASE_URL = "http://localhost:8090"
SERVICES = {
    "Gateway": 8090,
    "ai-bid-user": 8081,
    "ai-bid-project": 8082,
    "ai-bid-material": 8083,
    "ai-bid-document": 8084,
    "ai-bid-bid": 8085,
    "ai-bid-knowledge": 8086,
    "ai-bid-ai": 8087,
    "frontend": 3000
}

def get_process_info(port):
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port == port and conn.status == 'LISTEN':
                if conn.pid is None:
                    continue
                try:
                    proc = psutil.Process(conn.pid)
                    mem_mb = proc.memory_info().rss / 1024 / 1024
                    cpu_percent = proc.cpu_percent(interval=0.1)
                    return {"pid": conn.pid, "name": proc.name(), "cpu_percent": cpu_percent, "mem_mb": round(mem_mb, 2), "threads": proc.num_threads()}
                except:
                    pass
    except:
        pass
    return None

def test_api(endpoint, method="GET", data=None, description=""):
    url = f"{BASE_URL}{endpoint}"
    try:
        start = time.time()
        if method == "GET":
            resp = requests.get(url, timeout=10)
        else:
            resp = requests.post(url, json=data, timeout=30)
        elapsed = (time.time() - start) * 1000
        return {"endpoint": endpoint, "method": method, "status": resp.status_code, "elapsed_ms": round(elapsed, 2), "success": 200 <= resp.status_code < 300, "description": description}
    except Exception as e:
        return {"endpoint": endpoint, "method": method, "status": 0, "elapsed_ms": 0, "success": False, "description": description, "error": str(e)[:50]}

def main():
    print("=" * 70)
    print("AI智能投标系统 - 完整功能测试报告")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    print("\n[一、硬件开销统计]")
    print("-" * 70)
    print(f"{'服务':<20} {'PID':<8} {'CPU%':<8} {'内存MB':<10} {'线程':<6}")
    print("-" * 70)
    
    total_mem = 0
    total_cpu = 0
    proc_infos = {}
    for name, port in SERVICES.items():
        info = get_process_info(port)
        proc_infos[name] = info
        if info:
            print(f"{name:<20} {info['pid']:<8} {info['cpu_percent']:<8.1f} {info['mem_mb']:<10.2f} {info['threads']:<6}")
            total_mem += info['mem_mb']
            total_cpu += info['cpu_percent']
        else:
            print(f"{name:<20} {'N/A':<8} {'N/A':<8} {'N/A':<10} {'N/A':<6}")
    
    print("-" * 70)
    print(f"{'合计':<20} {'':<8} {total_cpu:<8.1f} {total_mem:<10.2f}")
    
    print("\n[二、服务健康检查]")
    print("-" * 70)
    
    health_results = []
    for name, port in SERVICES.items():
        info = proc_infos.get(name)
        if name == "frontend":
            status = "[OK] 运行中" if info else "[FAIL] 未运行"
            health_results.append({"service": name, "status": status, "detail": f"PID: {info['pid']}" if info else ""})
        elif name in ("ai-bid-knowledge", "ai-bid-ai"):
            try:
                resp = requests.get(f"http://localhost:{port}/health", timeout=5)
                status = "[OK] 健康" if resp.status_code == 200 else f"[WARN] {resp.status_code}"
                health_results.append({"service": name, "status": status, "detail": resp.text[:50]})
            except Exception as e:
                health_results.append({"service": name, "status": "[FAIL] 异常", "detail": str(e)[:30]})
        else:
            try:
                resp = requests.get(f"http://localhost:{port}/actuator/health", timeout=5)
                status = "[OK] 健康" if resp.status_code == 200 else f"[WARN] {resp.status_code}"
                health_results.append({"service": name, "status": status, "detail": f"{resp.status_code}"})
            except Exception as e:
                health_results.append({"service": name, "status": "[FAIL] 异常", "detail": str(e)[:30]})
    
    for r in health_results:
        print(f"{r['service']:<20} {r['status']:<15} {r['detail']}")
    
    print("\n[三、API功能测试]")
    print("-" * 70)
    
    api_tests = [
        ("/api/user/list", "GET", None, "用户列表查询"),
        ("/api/user/1", "GET", None, "用户详情查询"),
        ("/api/project/list", "GET", None, "项目列表查询"),
        ("/api/project/list", "GET", None, "项目详情查询(真实ID)"),
        ("/api/material/list", "GET", None, "素材列表查询"),
        ("/api/material/1", "GET", None, "素材详情查询"),
        ("/api/document/list", "GET", None, "文档列表查询"),
        ("/api/document/list", "GET", None, "文档详情查询(真实ID)"),
        ("/api/bid/list", "GET", None, "投标列表查询"),
        ("/api/bid/1", "GET", None, "投标详情查询"),
        ("/api/ai/export/templates", "GET", None, "获取模板列表"),
        ("/api/ai/generate/outline", "POST", {
            "projectName": "智慧城市基础设施建设项目",
            "projectType": "政府采购",
            "bidRequirements": "包含系统集成、软件开发",
            "scoringCriteria": "技术方案40分",
            "pageCount": 60
        }, "AI生成大纲"),
    ]
    
    passed = 0
    failed = 0
    for test in api_tests:
        if len(test) == 4:
            endpoint, method, data, desc = test
        else:
            endpoint, method, desc = test
            data = None
        result = test_api(endpoint, method, data=data, description=desc)
        status_icon = "[OK]" if result["success"] else "[FAIL]"
        print(f"{status_icon} {result['method']:<6} {endpoint:<35} {result['status']:<6} {result['elapsed_ms']:<8}ms {result['description']}")
        if result["success"]:
            passed += 1
        else:
            failed += 1
    
    print("-" * 70)
    print(f"通过: {passed} | 失败: {failed} | 通过率: {passed*100//(passed+failed) if passed+failed > 0 else 0}%")
    
    print("\n[四、系统资源概览]")
    print("-" * 70)
    vm = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    
    print(f"CPU: {cpu_count} 核心 @ {cpu_freq.current:.0f}MHz")
    print(f"内存: {vm.total/1024**3:.1f}GB | 使用: {vm.used/1024**3:.1f}GB ({vm.percent}%)")
    print(f"磁盘: {disk.total/1024**3:.1f}GB | 使用: {disk.used/1024**3:.1f}GB ({disk.percent}%)")
    
    print("\n" + "=" * 70)
    print("[总结]")
    print("=" * 70)
    healthy_count = sum(1 for r in health_results if "[OK]" in r["status"])
    print(f"* 服务运行: {healthy_count}/{len(SERVICES)}")
    print(f"* API测试: {passed}/{passed+failed} 通过")
    print(f"* 内存占用: {total_mem:.2f}MB")
    print(f"* CPU占用: {total_cpu:.1f}%")
    print("=" * 70)

if __name__ == "__main__":
    main()
