#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试执行脚本，运行所有测试并将结果保存到文件
"""

import os
import sys
import subprocess
import datetime

def run_tests():
    """执行测试并将结果保存到文件"""
    # 创建结果目录
    result_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "result")
    os.makedirs(result_dir, exist_ok=True)
    
    # 生成带时间戳的文件名
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    result_file = os.path.join(result_dir, f"test{timestamp}.txt")
    
    print(f"正在运行测试，结果将保存到: {result_file}")
    
    # 构建测试命令
    test_dir = os.path.dirname(os.path.abspath(__file__))
    cmd = [
        "pytest", 
        test_dir,
        "-v",
        "--cov=app",
        "--cov-report=term-missing"
    ]
    
    # 运行测试并捕获输出
    try:
        with open(result_file, "w", encoding="utf-8") as f:
            # 写入头部信息
            f.write("=================================== 测试报告 ===================================\n")
            f.write(f"运行时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"平台: {sys.platform}\n\n")
            
            # 运行测试并实时捕获输出
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            # 读取输出并写入文件
            for line in process.stdout:
                sys.stdout.write(line)  # 在控制台显示
                f.write(line)           # 写入文件
            
            # 等待进程完成
            return_code = process.wait()
            
            # 写入结束信息
            f.write("\n=================================== 测试结束 ===================================\n")
            f.write(f"测试完成，退出代码: {return_code}\n")
            
            return return_code
            
    except Exception as e:
        print(f"测试执行过程中发生错误: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests()) 