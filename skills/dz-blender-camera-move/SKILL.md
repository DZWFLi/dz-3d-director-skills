---
name: dz-blender-camera-move
description: 导入自己的三维模型，生成镜头靠近、稍微绕行或轻微晃动的产品展示画面，输出可修改工程、预览图和可选视频。
---

# Blender 相机预演

运行 `scripts/generate_camera_move.py --asset <file> --out <directory> --blender <executable>`。输入位置、输出位置和 Blender 路径由用户环境决定。脚本在独立后台进程中创建新场景。

默认是 30mm、120 帧、24fps 的推进与轻环绕。用 `--lens`、`--frames`、`--width`、`--height` 调整。需要视频时添加 `--render-video`，并确保运行 Python 安装了 imageio-ffmpeg。

先检查 `.blend` 中主体的世界包围盒和相机视野，再查看首帧与中帧；不要只凭“进程成功”判断主体可见。FBX 层级或单位异常时可以选择同资产的 OBJ，但不要替换成不属于用户的其他模型。

归一化会改变导入副本的尺寸与位置；这个流程用于镜头预演，不是保持毫米精度的工程资产转换。原文件保持不变。

输出包含 `scene.blend`、`scene.glb` 和两张预览图；请求视频后还包含 PNG 序列与 MP4。当前脚本没有浏览器编辑器、碰撞模拟或视频生成模型调用。
