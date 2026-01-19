"""
MCP客户端 - 实现完整的MCP协议流程

功能：
1. 管理MCP服务器连接
2. 实现完整的初始化流程
3. 提供工具调用接口
"""

import json
import subprocess
import os
import threading
import time
from typing import Dict, Any, Optional
import queue


class MCPClient:
    """
    MCP客户端 - 管理MCP服务器连接和通信
    
    实现完整的MCP协议流程：
    1. 启动MCP服务器进程
    2. 发送initialize请求
    3. 等待initialize响应
    4. 发送initialized通知
    5. 之后才能发送工具调用请求
    """
    
    def __init__(self, server_command: list, env: Optional[Dict[str, str]] = None):
        """
        初始化MCP客户端
        
        Args:
            server_command: MCP服务器启动命令，如 ["uvx", "amap-mcp-server"]
            env: 环境变量字典
        """
        self.server_command = server_command
        self.env = env or {}
        self.process: Optional[subprocess.Popen] = None
        self.initialized = False
        self.request_id = 0
        self.pending_requests: Dict[int, queue.Queue] = {}
        self.lock = threading.Lock()
        
    def _get_next_id(self) -> int:
        """获取下一个请求ID"""
        with self.lock:
            self.request_id += 1
            return self.request_id
    
    def _send_request(self, method: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        发送MCP请求并等待响应
        
        Args:
            method: MCP方法名，如 "initialize", "tools/call"
            params: 请求参数
            
        Returns:
            响应字典
        """
        if not self.process:
            raise RuntimeError("MCP server process not started")
        
        request_id = self._get_next_id()
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method
        }
        if params:
            request["params"] = params
        
        # 创建响应队列
        response_queue = queue.Queue()
        with self.lock:
            self.pending_requests[request_id] = response_queue
        
        try:
            # 发送请求（MCP协议要求每行一个JSON消息）
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            # 等待响应（最多30秒）
            try:
                response = response_queue.get(timeout=30)
                return response
            except queue.Empty:
                raise TimeoutError(f"MCP request {method} timed out")
        finally:
            with self.lock:
                self.pending_requests.pop(request_id, None)
    
    def _read_responses(self):
        """在后台线程中读取MCP服务器响应"""
        while self.process and self.process.poll() is None:
            try:
                line = self.process.stdout.readline()
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    response = json.loads(line)
                    request_id = response.get("id")
                    if request_id and request_id in self.pending_requests:
                        self.pending_requests[request_id].put(response)
                except json.JSONDecodeError:
                    # 忽略非JSON行（可能是日志）
                    continue
            except Exception as e:
                # Error reading MCP response (logged for debugging)
                pass
                break
    
    def start(self):
        """启动MCP服务器并初始化"""
        if self.process:
            return  # 已经启动
        
        # 启动MCP服务器进程
        env = os.environ.copy()
        env.update(self.env)
        
        self.process = subprocess.Popen(
            self.server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,  # 使用文本模式
            bufsize=1  # 行缓冲
        )
        
        # 启动响应读取线程
        self.response_thread = threading.Thread(target=self._read_responses, daemon=True)
        self.response_thread.start()
        
        # 等待服务器启动
        time.sleep(0.5)
        
        # 发送initialize请求
        initialize_params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "trip-planner",
                "version": "1.0.0"
            }
        }
        
        try:
            response = self._send_request("initialize", initialize_params)
            
            if "error" in response:
                raise RuntimeError(f"MCP initialize failed: {response['error']}")
            
            # 发送initialized通知
            self._send_notification("notifications/initialized", {})
            
            self.initialized = True
            return True
        except Exception as e:
            print(f"Failed to initialize MCP server: {e}")
            self.stop()
            raise
    
    def _send_notification(self, method: str, params: Optional[Dict] = None):
        """发送MCP通知（不需要响应）"""
        if not self.process:
            raise RuntimeError("MCP server process not started")
        
        notification = {
            "jsonrpc": "2.0",
            "method": method
        }
        if params:
            notification["params"] = params
        
        notification_json = json.dumps(notification) + "\n"
        self.process.stdin.write(notification_json)
        self.process.stdin.flush()
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用MCP工具
        
        Args:
            tool_name: 工具名称，如 "maps_text_search"
            arguments: 工具参数
            
        Returns:
            工具调用结果
        """
        if not self.initialized:
            raise RuntimeError("MCP client not initialized. Call start() first.")
        
        params = {
            "name": tool_name,
            "arguments": arguments
        }
        
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
    
    def stop(self):
        """停止MCP服务器"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception:
                pass
            finally:
                self.process = None
                self.initialized = False


# 全局MCP客户端实例（单例模式）
_mcp_clients: Dict[str, MCPClient] = {}


def get_mcp_client(server_command: list, env: Optional[Dict[str, str]] = None) -> MCPClient:
    """
    获取MCP客户端实例（单例模式）
    
    Args:
        server_command: MCP服务器启动命令
        env: 环境变量字典
        
    Returns:
        MCPClient实例
    """
    # 使用命令作为key
    key = " ".join(server_command)
    
    if key not in _mcp_clients:
        client = MCPClient(server_command, env)
        client.start()
        _mcp_clients[key] = client
    
    return _mcp_clients[key]
