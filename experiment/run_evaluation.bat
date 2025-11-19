@echo off
setlocal

REM 设置环境变量
set PYTHONPATH=%PYTHONPATH%;D:\大论文资料\benchmark\elereasoning

REM 运行评测
python main.py ^
    --dataset "D:\大论文资料\benchmark\datasets\test.csv" ^
    --config "config\openai.json" ^
    --output "results" ^
    --strategy "cot" ^
    --language "zh" ^
    --llm_extract

echo 评测完成！
pause