# DreamCatcher 测试文档

本目录包含DreamCatcher项目的测试用例。测试主要关注数据库操作和API接口，以确保核心功能正常工作。

## 测试结构

- `conftest.py`: 测试配置，设置测试环境和共用夹具
- `test_plan_service.py`: 针对计划服务层的测试
- `test_plans_api.py`: 针对计划API接口的测试
- `run_tests.py`: Python测试执行脚本，自动将结果保存到文件
- `run_and_save_tests.sh`: Shell测试执行脚本，自动将结果保存到文件
- `result/`: 目录存放测试结果报告

## 运行测试

### 安装测试依赖

确保已安装必要的测试依赖:

```bash
conda env update -f configs/environment.yml  # 先更新环境
pip install pytest pytest-cov httpx
```

### 运行所有测试

方法1：使用pytest直接运行
```bash
pytest app/test/ -v
```

方法2：使用Python脚本运行并保存结果
```bash
python app/test/run_tests.py
```

方法3：使用Shell脚本运行并保存结果
```bash
./app/test/run_and_save_tests.sh
```

### 运行特定测试文件

```bash
pytest app/test/test_plan_service.py -v  # 运行服务层测试
pytest app/test/test_plans_api.py -v     # 运行API接口测试
```

### 手动生成测试报告

如果不使用提供的脚本，也可以手动将测试结果重定向到文件：

```bash
pytest app/test/ --cov=app --cov-report=term-missing -v > app/test/result/test$(date +"%Y%m%d%H%M%S").txt
```

## 测试结果文件

测试结果会自动保存在 `app/test/result/` 目录中，文件名格式为 `test{时间戳}.txt`。
每个测试结果文件包含以下信息：
- 测试运行时间和平台信息
- 各测试用例的通过/失败状态
- 测试覆盖率报告
- 失败测试的详细信息

## 测试覆盖范围

测试覆盖以下功能:

1. **服务层功能**:
   - 创建拍摄计划
   - 获取单个拍摄计划
   - 获取不存在的拍摄计划
   - 获取用户的所有拍摄计划
   - 更新拍摄计划
   - 更新不存在的拍摄计划
   - 删除拍摄计划
   - 删除不存在的拍摄计划

2. **API接口**:
   - 创建拍摄计划API
   - 处理无效数据的创建请求
   - 获取用户拍摄计划
   - 按ID获取拍摄计划
   - 处理获取不存在的拍摄计划
   - 更新拍摄计划
   - 处理更新不存在的拍摄计划
   - 删除拍摄计划
   - 处理删除不存在的拍摄计划

## 注意事项

- 测试使用SQLite内存数据库，以保证测试速度和隔离性
- 每个测试前后会创建和删除数据库表，确保测试相互独立
- 网络渲染相关功能未包括在当前测试范围内 
- 结果文件(`test{时间戳}.txt`)会自动保存在`result`目录，方便查看和分析 