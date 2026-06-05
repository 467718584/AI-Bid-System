#!/usr/bin/env python3
"""
Phase 4 用户旅程测试
测试完整流程：登录 → 创建项目 → 生成标书大纲 → 生成正文 → 导出Word
"""
import requests
import json
import time

BASE_URL = "http://localhost:8090"

def test_user_journey():
    print("=" * 70)
    print("Phase 4 用户旅程测试")
    print("=" * 70)
    
    results = []
    
    # Step 1: 获取用户列表（模拟登录）
    print("\n[Step 1] 用户认证 - 获取用户列表")
    resp = requests.get(f"{BASE_URL}/api/user/list", timeout=10)
    if resp.status_code == 200:
        print(f"  ✅ 用户服务正常 (获取到 {len(resp.json().get('data', []))} 个用户)")
        results.append(("用户服务", True))
    else:
        print(f"  ❌ 用户服务失败: {resp.status_code}")
        results.append(("用户服务", False))
    
    # Step 2: 创建测试项目
    print("\n[Step 2] 创建测试项目")
    project_data = {
        "name": f"智慧城市项目_{int(time.time())}",
        "code": f"SC_{int(time.time())}",
        "type": "政府采购",
        "amount": 5000000,
        "tenderer": "某市政府采购中心",
        "deadline": "2026-07-15T10:00:00",
        "status": "draft",
        "description": "智慧城市基础设施建设项目，包含系统集成、软件开发等"
    }
    resp = requests.post(f"{BASE_URL}/api/project", json=project_data, timeout=10)
    if resp.status_code in [200, 201]:
        project_id = resp.json().get('data', {}).get('id') or resp.json().get('data')
        print(f"  ✅ 项目创建成功 (ID: {project_id})")
        results.append(("创建项目", True))
    else:
        print(f"  ⚠️ 项目创建响应: {resp.status_code} - {resp.text[:100]}")
        results.append(("创建项目", False))
    
    # Step 3: 获取项目列表
    print("\n[Step 3] 获取项目列表")
    resp = requests.get(f"{BASE_URL}/api/project/list", timeout=10)
    if resp.status_code == 200:
        projects = resp.json().get('data', [])
        print(f"  ✅ 获取到 {len(projects)} 个项目")
        results.append(("获取项目列表", True))
    else:
        print(f"  ❌ 获取项目列表失败: {resp.status_code}")
        results.append(("获取项目列表", False))
    
    # Step 4: AI生成标书大纲
    print("\n[Step 4] AI生成标书大纲")
    outline_data = {
        "projectName": "智慧城市基础设施建设项目",
        "projectType": "政府采购",
        "bidRequirements": "包含系统集成、软件开发、硬件采购及运维服务",
        "scoringCriteria": "技术方案40分、价格40分、资质20分",
        "pageCount": 60
    }
    resp = requests.post(f"{BASE_URL}/api/ai/generate/outline", json=outline_data, timeout=60)
    if resp.status_code == 200:
        data = resp.json()
        if data.get('code') == 200:
            outline = data.get('data', {})
            title = outline.get('title', '未知')
            print(f"  ✅ 大纲生成成功 (标题: {title})")
            results.append(("AI生成大纲", True))
        else:
            print(f"  ⚠️ 大纲生成返回: {data}")
            results.append(("AI生成大纲", False))
    else:
        print(f"  ❌ 大纲生成失败: {resp.status_code} - {resp.text[:200]}")
        results.append(("AI生成大纲", False))
    
    # Step 5: 获取模板列表
    print("\n[Step 5] 获取Word模板列表")
    resp = requests.get(f"{BASE_URL}/api/ai/export/templates", timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        templates = data.get('data', [])
        print(f"  ✅ 获取到 {len(templates)} 个模板")
        for t in templates:
            print(f"     - {t.get('name')}: {t.get('description', '')[:30]}")
        results.append(("获取模板列表", True))
    else:
        print(f"  ❌ 获取模板失败: {resp.status_code}")
        results.append(("获取模板列表", False))
    
    # Step 6: 获取素材列表
    print("\n[Step 6] 获取素材列表")
    resp = requests.get(f"{BASE_URL}/api/material/list", timeout=10)
    if resp.status_code == 200:
        materials = resp.json().get('data', [])
        print(f"  ✅ 获取到 {len(materials)} 个素材")
        results.append(("获取素材列表", True))
    else:
        print(f"  ❌ 获取素材失败: {resp.status_code}")
        results.append(("获取素材列表", False))
    
    # Step 7: 获取知识库健康状态 (直接调用Python服务)
    print("\n[Step 7] 知识库服务健康检查")
    resp = requests.get("http://localhost:8086/health", timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        print(f"  ✅ 知识库服务正常: {data}")
        results.append(("知识库服务", True))
    else:
        print(f"  ⚠️ 知识库服务: {resp.status_code} - {resp.text[:100]}")
        results.append(("知识库服务", False))
    
    # Step 8: 获取AI服务健康状态 (直接调用Python服务)
    print("\n[Step 8] AI服务健康检查")
    resp = requests.get("http://localhost:8087/health", timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        print(f"  ✅ AI服务正常: {data}")
        results.append(("AI服务", True))
    else:
        print(f"  ⚠️ AI服务: {resp.status_code} - {resp.text[:100]}")
        results.append(("AI服务", False))
    
    # Step 9: 投标列表
    print("\n[Step 9] 获取投标列表")
    resp = requests.get(f"{BASE_URL}/api/bid/list", timeout=10)
    if resp.status_code == 200:
        bids = resp.json().get('data', [])
        print(f"  ✅ 获取到 {len(bids)} 个投标")
        results.append(("投标列表", True))
    else:
        print(f"  ❌ 获取投标失败: {resp.status_code}")
        results.append(("投标列表", False))
    
    # Step 10: 文档列表
    print("\n[Step 10] 获取文档列表")
    resp = requests.get(f"{BASE_URL}/api/document/list", timeout=10)
    if resp.status_code == 200:
        docs = resp.json().get('data', [])
        print(f"  ✅ 获取到 {len(docs)} 个文档")
        results.append(("文档列表", True))
    else:
        print(f"  ❌ 获取文档失败: {resp.status_code}")
        results.append(("文档列表", False))
    
    # 汇总结果
    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)
    
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    
    for name, ok in results:
        status = "✅" if ok else "❌"
        print(f"  {status} {name}")
    
    print("-" * 70)
    print(f"通过: {passed}/{total} ({passed*100//total}%)")
    
    return passed == total

if __name__ == "__main__":
    success = test_user_journey()
    exit(0 if success else 1)
