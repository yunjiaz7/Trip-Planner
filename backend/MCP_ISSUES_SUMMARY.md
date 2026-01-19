# MCP调用问题总结和修复

## 🐛 发现的问题

### 问题1: MCP工具调用错误 - `'dict' object has no attribute 'returncode'`

**错误信息**:
```
Error calling MCP tool: 'dict' object has no attribute 'returncode'
```

**原因**:
- `mcp_tools.py`中还在尝试访问`result.returncode`
- 但`result`现在是一个字典（来自MCP客户端的`call_tool`方法返回）
- 不是subprocess的结果对象

**位置**: `backend/app/services/mcp_tools.py` 第105-112行

**修复**:
- ✅ 已修复：移除对`result.returncode`的访问
- ✅ 直接处理字典格式的响应
- ✅ 检查`result`字典中的`content`、`text`或`error`字段

### 问题2: Planner Agent提示词问题 - 模板变量错误

**错误信息**:
```
Error: 'Input to ChatPromptTemplate is missing variables {'\n  "city"'}'
```

**原因**:
- 提示词中包含JSON示例
- LangChain将JSON中的`{`和`}`误认为是模板变量
- 例如`{"city": "City Name"}`被解析为变量`\n  "city"`

**位置**: `backend/app/agents/trip_planner_agent.py` `PLANNER_AGENT_PROMPT`

**修复**:
- ✅ 已修复：转义JSON示例中的所有`{`为`{{`
- ✅ 转义JSON示例中的所有`}`为`}}`
- ✅ 这样LangChain就不会将其误认为是模板变量

### 问题3: MCP客户端错误处理改进

**改进**:
- ✅ 改进`call_tool`方法的错误处理
- ✅ 更详细的错误信息
- ✅ 正确处理各种响应格式

## ✅ 修复详情

### 修复1: MCP工具响应处理

**修复前**:
```python
result = mcp_client.call_tool(...)
if result.returncode != 0:  # ❌ result是字典，没有returncode属性
    error_msg = result.stderr or "Unknown error"
    return json.dumps({
        "error": "MCP server call failed",
        "returncode": result.returncode,
        ...
    })
```

**修复后**:
```python
result = mcp_client.call_tool(...)
# result是字典，直接处理
if "content" in result:
    content = result["content"]
    if isinstance(content, list):
        if len(content) > 0 and isinstance(content[0], dict):
            return content[0].get("text", json.dumps(content, ensure_ascii=False))
        return json.dumps(content, ensure_ascii=False)
    elif isinstance(content, str):
        return content
    else:
        return json.dumps(content, ensure_ascii=False)
elif "text" in result:
    return result["text"]
elif "error" in result:
    # 处理错误
    ...
else:
    return json.dumps(result, ensure_ascii=False)
```

### 修复2: 提示词JSON转义

**修复前**:
```python
```json
{
  "city": "City Name",
  ...
}
```
```

**修复后**:
```python
```json
{{
  "city": "City Name",
  ...
}}
```
```

### 修复3: MCP客户端错误处理

**改进**:
```python
response = self._send_request("tools/call", params)

# 检查响应中的错误
if "error" in response:
    error_info = response["error"]
    if isinstance(error_info, dict):
        error_msg = error_info.get("message", "Unknown error")
        error_code = error_info.get("code", -1)
        raise RuntimeError(f"MCP tool call failed (code {error_code}): {error_msg}")
    else:
        raise RuntimeError(f"MCP tool call failed: {error_info}")

# 返回result字段，如果没有则返回整个response
result = response.get("result", response)
return result if result else {}
```

## 📊 预期效果

### 修复前
- ❌ MCP工具调用失败：`'dict' object has no attribute 'returncode'`
- ❌ Planner Agent失败：提示词变量错误
- ❌ 错误处理不够完善

### 修复后
- ✅ MCP工具调用成功：正确处理字典响应
- ✅ Planner Agent成功：提示词正确解析
- ✅ 更好的错误处理和错误信息

## 🎯 验证

修复后重新运行测试：
```bash
python3 test_all_agents.py
```

预期结果：
- ✅ MCP工具调用成功
- ✅ Planner Agent正常工作
- ✅ 所有测试通过

## 📝 注意事项

1. **MCP服务器初始化**: 确保MCP服务器正确初始化
2. **响应格式**: MCP协议响应格式可能因服务器而异
3. **错误处理**: 需要处理各种错误情况
4. **提示词转义**: 在LangChain提示词中使用JSON示例时，必须转义大括号
