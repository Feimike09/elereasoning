@echo off
setlocal

REM 设置环境变量
set PYTHONPATH=%PYTHONPATH%;D:\大论文资料\benchmark\elereasoning

REM 运行分析
python analyze_results.py --results_dir "results" --output "analysis"

echo 分析完成！
pause