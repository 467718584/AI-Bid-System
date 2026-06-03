# AI智能投标系统 - 问题解决模式库

## 前端Vue组件模式

### 1. el-tree数据转换模式
**问题**: el-tree期望格式与API返回不匹配
**解决**: 使用computed转换

```javascript
const outlineData = computed(() => {
  const convert = (nodes) => {
    return nodes.map((node, index) => ({
      id: `node-${index}-${Date.now()}`,
      title: node.title,
      pageCount: node.pageCount,
      children: node.children ? convert(node.children) : []
    }))
  }
  return convert(props.outline)
})
```

### 2. 编辑状态管理模式
**问题**: 需要双击编辑表格单元格
**解决**: 使用editingNodeId追踪

```javascript
const editingNodeId = ref(null)
const editingTitle = ref('')

const startEditTitle = (data) => {
  editingNodeId.value = data.id
  editingTitle.value = data.title
}

const confirmEditTitle = (originalTitle) => {
  // 更新数据
  emit('update', newOutline)
  editingNodeId.value = null
}
```

### 3. API响应处理模式
**问题**: axios响应拦截器统一处理
**解决**: 拦截器返回res，调用方直接用res.data

```javascript
// api/index.js
api.interceptors.response.use((response) => {
  const res = response.data
  if (res.code !== 200) {
    ElMessage.error(res.message)
    return Promise.reject(new Error(res.message))
  }
  return res  // 直接返回res
})

// 调用方
const res = await getBidDetail(id)
bidTitle.value = res.data?.title || ''  // 直接使用res.data
```

## 后端Java模式

### 1. Controller返回格式
**问题**: create接口需要返回新创建对象的ID
**解决**: 返回完整对象

```java
@PostMapping
public Map<String, Object> create(@RequestBody Map<String, Object> data) {
    data.put("id", System.currentTimeMillis());
    data.put("status", "draft");
    data.put("createdAt", new Date().toString());
    bidStore.add(data);
    return Map.of(
        "code", 200,
        "data", data  // 返回完整对象
    );
}
```

### 2. Gateway路由配置
**问题**: StripPrefix与Controller路径不匹配
**解决**: 根据实际情况配置

```yaml
# AI服务 - 不需要StripPrefix
- id: ai-service
  uri: http://localhost:8087
  predicates:
    - Path=/api/ai/**
  # 无filters配置

# Java服务 - 需要StripPrefix去掉/api前缀
- id: user-service
  uri: http://localhost:8081
  predicates:
    - Path=/api/user/**
  filters:
    - StripPrefix=1
```

## Python AI服务模式

### 1. 清理AI思考内容
**问题**: AI返回内容包含<think>标签
**解决**: 正则清理

```python
import re
content = await llm_wrapper.chat(messages)
# 清理<think>...内容
content = re.sub(r'<think>[\s\S]*?', '', content).strip()
```

### 2. API Key检查模式
**问题**: API Key未配置时返回空
**解决**: 检查并提供fallback

```python
if not llm_wrapper.gateway.api_key:
    return {
        "code": 200,
        "data": {
            "content": "# 模拟内容\n\n请配置MINIMAX_API_KEY后重试。",
            "images": [],
            "tables": []
        }
    }
```

## 工作流模式

### 1. 工作流创建后获取ID
**问题**: 创建接口返回格式不确定
**解决**: 从list中查找

```javascript
const res = await createWorkflow(createForm.value)
const newWorkflow = res.data?.list?.find(
  w => w.name === createForm.value.name
)
if (newWorkflow?.id) {
  currentWorkflowId.value = newWorkflow.id
}
```

## 常见错误处理

### 1. 500错误 - 检查@PathVariable名称
```java
// 错误
@GetMapping("/{id}")
public Map get(@PathVariable Long id) {}  // 参数名丢失

// 正确
@GetMapping("/{id:[0-9]+}")
public Map get(@PathVariable("id") Long id) {}  // 显式指定
```

### 2. CORS错误 - 添加@CrossOrigin或配置
```java
@CrossOrigin(origins = "*")
@RestController
public class XxxController {}
```

### 3. 内存存储重启丢失 - 后续需接入数据库
当前bidStore是List<Map>，重启后数据丢失。