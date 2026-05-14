import docker
import asyncio
import time
import tempfile
import os
from typing import Dict, Optional, Callable
from app.core.config import settings


# Language configurations with Docker images
LANGUAGE_CONFIGS = {
    "python": {
        "image": "python:3.11-slim",
        "command": "python /app/code.py",
        "file_extension": ".py"
    },
    "javascript": {
        "image": "node:18-slim",
        "command": "node /app/code.js",
        "file_extension": ".js"
    },
    "java": {
        "image": "openjdk:17-slim",
        "command": "cd /app && javac code.java && java Main",
        "file_extension": ".java"
    },
    "cpp": {
        "image": "gcc:12-slim",
        "command": "cd /app && g++ -o code code.cpp && ./code",
        "file_extension": ".cpp"
    },
    "c": {
        "image": "gcc:12-slim",
        "command": "cd /app && gcc -o code code.c && ./code",
        "file_extension": ".c"
    }
}


class CodeExecutor:
    def __init__(self):
        self.client = None
        try:
            self.client = docker.from_env()
        except Exception as e:
            print(f"Docker not available: {e}")
    
    async def execute_code(
        self, 
        language: str, 
        code: str, 
        input_data: str = "",
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        Execute code in a sandboxed Docker container
        Returns: {output, error, status, execution_time}
        """
        if language not in LANGUAGE_CONFIGS:
            return {
                "output": "",
                "error": f"Unsupported language: {language}",
                "status": "error",
                "execution_time": 0
            }
        
        if not self.client:
            # Fallback for development without Docker
            return await self._execute_local(language, code, input_data)
        
        config = LANGUAGE_CONFIGS[language]
        start_time = time.time()
        
        try:
            # Create temporary directory with code
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = os.path.join(temp_dir, f"code{config['file_extension']}")
                with open(file_path, 'w') as f:
                    f.write(code)
                
                # For Java, we need to name the file Main.java if class is Main
                if language == "java":
                    java_file = os.path.join(temp_dir, "Main.java")
                    with open(java_file, 'w') as f:
                        f.write(code)
                
                # Run Docker container
                container = self.client.containers.run(
                    config["image"],
                    command=config["command"],
                    volumes={temp_dir: {"bind": "/app", "mode": "ro"}},
                    working_dir="/app",
                    stdin=True,
                    tty=False,
                    mem_limit=settings.MAX_MEMORY,
                    network_disabled=True,  # Security: disable network
                    remove=True,
                    detach=True
                )
                
                try:
                    # Wait for container with timeout
                    result = container.wait(timeout=settings.EXECUTION_TIMEOUT)
                    exit_code = result.get("StatusCode", 0)
                    
                    # Get output
                    output = container.logs(stdout=True, stderr=False).decode('utf-8', errors='ignore')
                    error = container.logs(stdout=False, stderr=True).decode('utf-8', errors='ignore')
                    
                    execution_time = int((time.time() - start_time) * 1000)
                    
                    if progress_callback:
                        await progress_callback({"type": "complete", "output": output, "error": error})
                    
                    return {
                        "output": output,
                        "error": error if exit_code != 0 else "",
                        "status": "success" if exit_code == 0 else "error",
                        "execution_time": execution_time
                    }
                    
                except docker.errors.APIError as e:
                    return {
                        "output": "",
                        "error": f"Container error: {str(e)}",
                        "status": "error",
                        "execution_time": int((time.time() - start_time) * 1000)
                    }
                finally:
                    try:
                        container.stop(timeout=1)
                    except:
                        pass
        
        except asyncio.TimeoutError:
            return {
                "output": "",
                "error": f"Execution timeout after {settings.EXECUTION_TIMEOUT} seconds",
                "status": "timeout",
                "execution_time": settings.EXECUTION_TIMEOUT * 1000
            }
        except Exception as e:
            return {
                "output": "",
                "error": f"Execution error: {str(e)}",
                "status": "error",
                "execution_time": int((time.time() - start_time) * 1000)
            }
    
    async def _execute_local(self, language: str, code: str, input_data: str = "") -> Dict:
        """
        Fallback local execution (for development only - NOT secure for production)
        """
        import subprocess
        
        start_time = time.time()
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                if language == "python":
                    file_path = os.path.join(temp_dir, "code.py")
                    with open(file_path, 'w') as f:
                        f.write(code)
                    
                    process = await asyncio.create_subprocess_exec(
                        "python", file_path,
                        stdin=asyncio.subprocess.PIPE,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=temp_dir
                    )
                    
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(input=input_data.encode()),
                        timeout=settings.EXECUTION_TIMEOUT
                    )
                    
                    execution_time = int((time.time() - start_time) * 1000)
                    
                    return {
                        "output": stdout.decode('utf-8', errors='ignore'),
                        "error": stderr.decode('utf-8', errors='ignore'),
                        "status": "success" if process.returncode == 0 else "error",
                        "execution_time": execution_time
                    }
                else:
                    return {
                        "output": "",
                        "error": f"Language {language} requires Docker for execution",
                        "status": "error",
                        "execution_time": 0
                    }
                    
        except asyncio.TimeoutError:
            return {
                "output": "",
                "error": f"Execution timeout after {settings.EXECUTION_TIMEOUT} seconds",
                "status": "timeout",
                "execution_time": settings.EXECUTION_TIMEOUT * 1000
            }
        except Exception as e:
            return {
                "output": "",
                "error": f"Execution error: {str(e)}",
                "status": "error",
                "execution_time": int((time.time() - start_time) * 1000)
            }
    
    async def stream_execution(
        self, 
        language: str, 
        code: str, 
        input_data: str = "",
        websocket=None
    ):
        """
        Stream execution output in real-time via WebSocket
        """
        if websocket:
            await websocket.send_json({"type": "status", "message": "Starting execution..."})
        
        async def progress_callback(data):
            if websocket:
                await websocket.send_json(data)
        
        result = await self.execute_code(
            language=language,
            code=code,
            input_data=input_data,
            progress_callback=progress_callback
        )
        
        if websocket:
            await websocket.send_json({
                "type": "result",
                **result
            })
        
        return result


executor = CodeExecutor()
