---
name: dz-blender-python
description: 让 Blender 在后台执行脚本，完成新建场景、导入模型、导出文件或渲染，适合重复使用的三维制作任务。
---

# Blender Python 执行

用 `scripts/run_blender.py --blender <executable> --script <scene.py>` 运行脚本。需要已有工程时添加 `--blend <scene.blend>`；工具不会自动保存或覆盖工程，输出行为由场景脚本明确决定。

已有交互场景需要继续编辑时，使用用户已连接的 Blender MCP 或保存副本再处理。独立后台任务适合新建工程、批处理、导入导出和渲染，不要冒充正在控制用户打开的窗口。

重要修改后检查实际输出。视觉任务查看预览图；结构任务核对网格、相机和包围盒。错误日志用于定位，不能在失败后把旧输出当成这次成功结果。
