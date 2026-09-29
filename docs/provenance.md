# 项目与依赖

## 本仓库内容

- 镜头规划、白模预演和场景检查说明：根据作者的实际操作经验重新编写为公开工作流。
- 相机生成脚本：源自作者 2026 年 7 月的本地 Blender 运镜任务与之后整理的 `blender-camera-move` Skill；公开版将资产与输出位置参数化，移除机器路径，并添加尺寸参数和输入检查。
- Blender 执行与场景检查脚本：面向公开版编写的通用工具。
- 示例模型与预览：本仓库生成的简单几何，不使用购买资产或客户资料。

## 运行依赖

- [Blender](https://www.blender.org/)：运行时和 Python API；未随本仓库分发。
- [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg)：可选视频编码依赖；未随本仓库分发。
