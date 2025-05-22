"""
文件功能描述：

该Python脚本演示了如何使用 `subprocess` 模块与子进程进行高效交互，涵盖了多种典型使用场景，
包括但不限于命令执行、进程管理、管道通信、超时处理以及多进程并行操作。

主要功能模块：
- 使用 `subprocess.run` 封装执行简单命令并捕获输出（如 echo 和 sleep）。
- 使用 `subprocess.Popen` 启动并管理长期运行的子进程。
- 实现跨平台兼容的命令抽象调度机制（支持 Windows 和 Linux）。
- 演示如何通过管道与子进程通信（如数据加密和哈希链式处理）。
- 展示子进程并行执行与状态轮询。
- 提供对子进程执行超时的异常处理。
- 通过装饰器封装统一的错误日志记录机制。

依赖说明：
- 系统中需安装 OpenSSL 并配置到环境变量 PATH 中，用于加密和哈希相关示例。

命令行参数支持：
- 可通过 `--example` 参数指定运行特定示例，例如：
    --example simple      # 运行简单命令示例
    --example poll        # 运行轮询子进程状态示例
    --example parallel    # 运行并行进程示例
    --example pipe        # 运行管道数据传输示例
    --example chain       # 运行子进程链示例
    --example timeout     # 运行超时处理示例
    --example all         # 运行所有示例（默认）

日志输出：
- 输出信息级别为 INFO，包含每个示例的执行过程和结果，便于调试和学习。
"""

import argparse
import logging
import os
import platform
import shutil
import subprocess
import time
from contextlib import contextmanager
from typing import Tuple, List, Optional, IO, AnyStr, Callable
from enum import Enum

# ====================
# 配置日志
# ====================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ====================
# 工具函数
# ====================

# 定义命令类型枚举类
class CommandType(Enum):
    SLEEP = "sleep"
    ECHO = "echo"

# 定义平台类型枚举类
class Platform(Enum):
    WINDOWS = "Windows"
    LINUX = "Linux"

# 根据不同的命令类型和平台类型，定义对应的命令执行函数
PLATFORM_COMMANDS = {
    # Windows平台下的SLEEP命令执行函数
    (CommandType.SLEEP.value, Platform.WINDOWS.value): lambda *args: (["timeout", "/T", args[0] if args else "1", "/NOBREAK"], False),
    # Linux平台下的SLEEP命令执行函数
    (CommandType.SLEEP.value, Platform.LINUX.value): lambda *args: (["sleep", args[0] if args else "1"], False),
    # Windows平台下的ECHO命令执行函数
    (CommandType.ECHO.value, Platform.WINDOWS.value): lambda *args: (["cmd", "/c", "echo", " ".join(args)], False),
    # Linux平台下的ECHO命令执行函数
    (CommandType.ECHO.value, Platform.LINUX.value): lambda *args: (["echo", " ".join(args)], False),
}


def get_platform_command(command_name: str, *args: str) -> Tuple[List[str], bool]:
    """
    根据操作系统和命令类型，返回相应的命令列表和是否需要shell执行。

    参数:
    command_name: str - 命令名称，用于确定命令类型。
    *args: str - 可变参数，根据命令类型决定如何使用。

    返回:
    Tuple[List[str], bool] - 一个元组，包含命令列表和一个布尔值，指示是否需要shell执行。

    抛出:
    ValueError - 当传入的命令类型或平台不受支持时抛出。
    """
    cmd_type = CommandType(command_name)
    plat = Platform(platform.system())
    key = (cmd_type.value, plat.value)

    if key in PLATFORM_COMMANDS:
        return PLATFORM_COMMANDS[key](*args)
    else:
        raise ValueError(f"Unsupported command type or platform: {cmd_type}, {plat}")

def run_command(command: List[str], *, shell: bool = False, **kwargs) -> Optional[str]:
    """
    封装 subprocess.run 调用，以简化外部命令的执行并统一错误处理

    参数:
    - command: List[str] - 要执行的命令及其参数，以字符串列表形式提供
    - shell: bool - 是否通过shell环境执行命令，默认为False
    - **kwargs - 任意额外的关键字参数，将传递给subprocess.run

    返回:
    - Optional[str] - 命令的输出结果（去除首尾空白），如果命令执行失败则返回None
    """
    try:
        # 执行命令并捕获输出，设置编码为utf-8，确保兼容性
        result = subprocess.run(
            command,
            capture_output=True,
            shell=shell,
            encoding="utf-8",
            check=True,
            **kwargs
        )
        # 返回命令执行结果的stdout部分，去除首尾空白字符
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        # 当命令执行失败时，记录错误信息
        logger.error("Command failed: %s", e.stderr or e)
        # 返回None表示命令执行失败
        return None



def spawn_process(command: List[str], *, shell: bool = False, **kwargs) -> Optional[subprocess.Popen]:
    """
    封装 subprocess.Popen 调用，用于启动一个新的进程执行给定的命令

    此函数简化了 subprocess.Popen 的使用，通过提供一个清晰的接口来启动进程
    它处理了异常情况，并返回进程对象，以便调用者可以进一步管理该进程

    参数:
    - command: List[str] - 要执行的命令，作为字符串列表提供
    - shell: bool = False - 是否通过 shell 执行命令，默认不使用 shell
    - **kwargs - 任意额外的关键字参数，将传递给 subprocess.Popen

    返回:
    - Optional[subprocess.Popen] - 成功时返回 subprocess.Popen 对象，失败时返回 None
    """
    try:
        # 尝试创建并启动新的进程
        return subprocess.Popen(
            command,
            shell=shell,
            **kwargs
        )
    except Exception as e:
        # 如果启动进程时发生异常，记录错误信息并返回 None
        logger.error("Failed to start subprocess: %s", e)
        return None



def ensure_openssl():
    """
    检查 OpenSSL 是否存在

    通过 shutil.which() 函数在系统 PATH 中查找 'openssl' 命令
    如果找不到 'openssl'，则抛出 EnvironmentError 异常，表明系统中未找到 OpenSSL
    """
    if not shutil.which("openssl"):
        raise EnvironmentError("OpenSSL not found in system PATH.")



@contextmanager
def safe_pipe(pipe: Optional[IO[AnyStr]]):
    """
    安全地管理管道资源

    该函数是一个上下文管理器，用于安全地处理管道（pipe）资源的使用。
    它的主要作用是确保在使用完管道后能够正确地关闭它，以避免资源泄露。

    参数:
    - pipe: Optional[IO[AnyStr]] -- 可能为None的管道对象，如果存在，则需要被管理。

    该上下文管理器不返回任何值。
    """
    try:
        yield pipe
    finally:
        if pipe:
            pipe.close()



def run_encrypt(data: bytes) -> subprocess.Popen:
    """
    使用openssl工具对数据进行加密处理。

    该函数通过调用openssl的enc命令，使用3DES加密算法和PBKDF2密钥派生方法对输入的数据进行加密。
    加密使用的密码通过环境变量传递，以避免直接在命令行中暴露。

    参数:
    - data: 需要加密的数据，以字节流的形式传入。

    返回:
    - subprocess.Popen: 返回一个加密进程对象，可以通过该对象与加密进程进行交互。
    """
    # 创建一个环境变量副本，并添加加密使用的密码，避免直接在命令行参数中暴露密码
    env = dict(os.environ, password="secure")

    # 调用openssl的enc命令，使用3DES加密算法和PBKDF2密钥派生方法对数据进行加密
    # 加密密码通过环境变量传递
    return spawn_process(
        ["openssl", "enc", "-des3", "-pbkdf2", "-pass", "env:password"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )



# ====================
# 示例函数抽象封装
# ====================

def handle_example_errors(func: Callable):
    """
    一个装饰器，用于处理示例中的错误。

    如果装饰的函数在执行过程中抛出异常，此装饰器会捕获异常并使用对象的logger记录错误详情。

    参数:
    - func: Callable 被装饰的函数，通常是一个可能会抛出异常的方法。

    返回:
    - wrapper: Callable 包装了错误处理逻辑的函数。
    """
    def wrapper(self, *args, **kwargs):
        """
        实际的错误处理逻辑。

        参数:
        - self: 被装饰方法所属的实例对象。
        - *args: 位置参数，传递给被装饰方法。
        - **kwargs: 关键字参数，传递给被装饰方法。

        返回:
        - 被装饰方法的返回值，如果执行成功。
        - None: 如果执行失败并记录了错误。

        此函数尝试执行被装饰的函数，如果执行过程中出现异常，则使用对象的logger记录异常信息。
        """
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            self.logger.exception("%s failed: %s", func.__name__, e)
    return wrapper



class SubprocessExampleRunner:
    def __init__(self):
        """
        初始化日志记录器和检查OpenSSL配置。

        在类的构造函数中，首先创建一个日志记录器，用于记录类级别的日志。
        然后调用ensure_openssl函数，确保OpenSSL库被正确配置并可用。
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        ensure_openssl()  # 提前检查一次即可

    @handle_example_errors
    def run_simple_command(self):
        """
        运行 echo 命令，捕获输出
        该方法主要用于演示如何执行一个简单的系统命令，并记录其输出
        """
        # 获取适用于当前操作系统的命令和参数
        cmd, shell = get_platform_command("echo", "Hello from the child!")

        # 执行命令并获取输出
        output = run_command(cmd, shell=shell)

        # 如果有输出，记录到日志
        if output:
            self.logger.info("Simple command output: %s (Command: %s)", output, ' '.join(cmd))

    @handle_example_errors
    def poll_child_process(self):
        """
        轮询子进程状态。

        此方法用于启动一个子进程并轮询其状态，直到子进程结束。
        它会记录子进程的退出状态码，标准输出和错误输出。
        """
        # 获取适用于当前平台的命令和是否使用shell
        cmd, shell = get_platform_command("sleep", "2")

        # 启动一个新的进程
        proc = spawn_process(cmd, shell=shell)

        # 如果进程启动失败，则直接返回
        if not proc:
            return

        # 当进程仍然运行时，持续轮询
        while proc.poll() is None:
            # 记录调试信息表示进程正在运行
            self.logger.debug("Working...")
            # 短暂暂停，减少CPU占用
            time.sleep(0.5)

        # 记录进程的退出状态码
        self.logger.info("Exit status: %d", proc.returncode)

        # 获取进程的标准输出和错误输出
        stdout, stderr = proc.communicate()

        # 如果有标准输出，记录标准输出信息
        if stdout:
            self.logger.debug("Standard output: %s", stdout)

        # 如果有错误输出，记录错误输出信息
        if stderr:
            self.logger.debug("Error output: %s", stderr)

    @handle_example_errors
    def run_parallel_processes(self):
        """
        并行运行多个子进程

        此函数演示如何同时启动多个进程，并等待它们全部完成
        它使用了time模块来计时这些进程运行的总时间，并记录下来
        """
        # 获取当前平台下的sleep命令及是否需要shell执行
        cmd, shell = get_platform_command("sleep", "2")
        # 记录开始时间
        start = time.perf_counter()
        # 创建并启动5个进程
        procs = [spawn_process(cmd, shell=shell) for _ in range(5)]
        # 遍历所有进程，如果进程存在则等待其完成
        for proc in procs:
            if proc:
                proc.communicate()
        # 计算并记录所有进程完成的总时间
        elapsed = time.perf_counter() - start
        self.logger.info("Finished in %.2f seconds", elapsed)

    @handle_example_errors
    def pipe_data_to_subprocess(self):
        """向 subprocess 写入数据并读取输出

        本函数通过创建一个子进程，向其写入随机生成的数据，并读取处理后的输出。
        主要用于演示如何与子进程进行通信及错误处理。
        """
        # 重复执行以下步骤3次，每次生成不同的数据并处理
        for _ in range(3):
            # 生成16字节的随机数据
            data = os.urandom(16)
            # 启动一个加密进程，并传入随机生成的数据
            proc = run_encrypt(data)
            # 安全地获取进程的输入管道
            with safe_pipe(proc.stdin) as stdin_pipe:
                # 向进程写入数据并获取处理后的输出和错误信息
                out, err = proc.communicate(data)

            # 根据进程的退出状态码判断加密是否成功
            if proc.returncode == 0:
                # 如果成功，记录加密后的数据的最后10个字节
                self.logger.info("Encrypted (last 10 bytes): %s", out[-10:])
            else:
                # 如果失败，记录错误信息
                self.logger.error("Encryption failed: %s", err.decode())

    @handle_example_errors
    def chain_parallel_processes(self):
        """
        创建子进程链：加密 -> 哈希
        此函数演示了如何使用子进程执行加密和哈希操作，
        并将它们链接在一起以处理数据流。
        """

        # 定义一个内部函数来执行哈希操作
        def run_hash(stdin_pipe):
            """
            使用openssl工具执行SHA-256哈希操作
            参数:
                stdin_pipe: 用于接收输入数据的管道
            返回:
                返回执行哈希操作的子进程
            """
            return spawn_process(
                ["openssl", "dgst", "-sha256", "-binary"],
                stdin=stdin_pipe,
                stdout=subprocess.PIPE
            )

        # 重复三次执行加密和哈希操作
        for _ in range(3):
            # 生成随机数据
            data = os.urandom(64)
            # 执行加密操作
            encrypt_proc = run_encrypt(data)
            if not encrypt_proc:
                continue

            # 执行哈希操作
            hash_proc = run_hash(encrypt_proc.stdout)
            if not hash_proc:
                continue

            # 将原始数据写入加密进程
            encrypt_proc.stdin.write(data)
            encrypt_proc.stdin.flush()
            encrypt_proc.stdin.close()

            # 获取哈希操作的结果
            out, _ = hash_proc.communicate()
            # 根据哈希进程的返回码记录结果或错误
            if hash_proc.returncode == 0:
                self.logger.info("Hashed (last 10 bytes): %s", out[-10:])
            else:
                self.logger.error("Hashing failed.")

    @handle_example_errors
    def handle_timeout(self):
        """
        处理子进程超时
        此函数用于演示如何处理启动子进程后该子进程超时的情况它尝试执行一个命令，
        如果该命令在指定时间内未完成，则终止子进程并记录相关日志
        """
        # 获取适合当前操作系统的睡眠命令和是否使用shell
        cmd, shell = get_platform_command("sleep", "10")

        # 启动一个新的进程来执行睡眠命令
        proc = spawn_process(cmd, shell=shell)

        # 检查进程是否成功启动
        if not proc:
            return

        try:
            # 尝试与进程通信，设置超时时间为1秒
            proc.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            # 如果发生超时，记录警告日志并终止进程
            self.logger.warning("Timeout. Terminating...")
            proc.terminate()
            proc.wait()

        # 记录进程的退出状态码
        self.logger.info("Exit status: %d", proc.returncode)

    def run_all(self):
        """
        运行所有示例

        该方法定义了一个示例列表，每个示例由其名称和对应的执行函数组成
        遍历每个示例，记录日志开始执行，并捕获可能发生的异常
        如果执行过程中发生异常，记录异常信息
        """
        # 定义示例列表，每个元素是一个元组，包含示例名称和执行函数
        examples = [
            ("Simple Command", self.run_simple_command),
            ("Polling Process", self.poll_child_process),
            ("Parallel Processes", self.run_parallel_processes),
            ("Pipe Data", self.pipe_data_to_subprocess),
            ("Chain Processes", self.chain_parallel_processes),
            ("Handle Timeout", self.handle_timeout),
        ]
        # 遍历示例列表，执行每个示例
        for name, func in examples:
            # 记录日志，开始执行示例
            self.logger.info("Running %s example", name)
            # 尝试执行示例函数
            try:
                func()
            # 捕获执行过程中发生的异常
            except Exception as e:
                # 记录异常信息
                self.logger.exception("%s failed: %s", name, e)


# ====================
# 主入口：支持 CLI 参数
# ====================

EXAMPLES = {
    # 运行所有示例
    'all': lambda r: r.run_all(),
    # 运行简单命令示例，执行 echo 命令并捕获输出
    'simple': lambda r: r.run_simple_command(),
    # 运行轮询子进程状态示例，演示如何轮询子进程直到完成
    'poll': lambda r: r.poll_child_process(),
    # 运行并行进程示例，演示如何同时运行多个子进程
    'parallel': lambda r: r.run_parallel_processes(),
    # 运行管道数据到子进程示例，演示如何向子进程写入数据并读取输出
    'pipe': lambda r: r.pipe_data_to_subprocess(),
    # 运行子进程链示例，演示加密后立即进行哈希处理
    'chain': lambda r: r.chain_parallel_processes(),
    # 运行超时处理示例，演示如何处理子进程执行超时的情况
    'timeout': lambda r: r.handle_timeout(),
}



def main():
    """
    主函数入口。
    解析命令行参数，并根据参数选择要运行的子进程示例。
    """
    # 创建命令行参数解析器，描述信息为"Run subprocess examples"
    parser = argparse.ArgumentParser(description="Run subprocess examples")

    # 添加命令行参数'--example'，指定可选值为EXAMPLES字典的键，默认值为'all'，
    # 帮助信息为"Specify which example to run"
    parser.add_argument('--example', choices=EXAMPLES.keys(), default='all',
                        help="Specify which example to run")

    # 解析命令行参数
    args = parser.parse_args()

    # 创建子进程示例运行器实例
    runner = SubprocessExampleRunner()

    # 根据解析到的命令行参数example，从EXAMPLES字典中获取对应的函数，并调用该函数，
    # 传入子进程示例运行器实例作为参数
    EXAMPLES[args.example](runner)



if __name__ == "__main__":
    main()
