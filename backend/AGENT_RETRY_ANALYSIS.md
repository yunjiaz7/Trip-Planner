# Agent过多重试问题分析

## 🐛 问题1: 过多的LLM调用

### 现象
从测试输出看，Hotel Agent调用了**很多次**`amap_maps_text_search`工具：
- 每次调用都返回相同的结果（香港的酒店，不是北京的）
- Agent看到结果不对，就继续重试
- 最终因为"Agent stopped due to max iterations"而停止

### 原因分析

#### 1. 没有设置max_iterations限制
- 用户移除了`max_iterations=5`和`max_execution_time=60`的限制
- AgentExecutor默认没有迭代次数限制（或限制很大）
- Agent会一直重试直到达到默认限制

#### 2. Agent看到错误结果继续重试
- MCP工具返回的结果不正确（返回香港的酒店而不是北京的）
- Agent认为工具调用失败，继续尝试
- 但每次调用都返回相同错误的结果，形成死循环

#### 3. 工具返回格式问题
- 工具返回的是JSON格式的原始数据
- Agent可能无法正确理解结果
- 需要更好的结果格式化

### 解决方案

#### 方案1: 设置合理的迭代限制（推荐）
```python
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=3,  # 限制最多3次迭代
    max_execution_time=30  # 限制最多30秒
)
```

#### 方案2: 改进工具返回格式
- 让工具返回更友好的文本格式
- 而不是原始JSON数据
- 这样Agent更容易理解结果

#### 方案3: 改进提示词
- 在提示词中明确告诉Agent：如果工具返回的结果不符合要求，应该停止重试
- 或者接受当前结果并继续

---

## 🐛 问题2: HelloAgents依赖检查失败

### 现象
测试显示：
```
⚠️  代码中仍包含HelloAgents引用:
   - SimpleAgent (行 71)
   - SimpleAgent (行 114)
```

### 原因分析
- 代码注释中提到了`SimpleAgent`
- 测试脚本检查代码源文件，发现了这些字符串
- 虽然只是注释，但测试认为这是依赖

### 解决方案
- 清理注释中的HelloAgents引用
- 或者更新测试脚本，忽略注释中的引用
