# Pearl Properties Generator

一个用于 [MCDReforged](https://github.com/Fallen-Breath/MCDReforged) 的珍珠炮配置生成器插件。

基于 [PearlCannonHelper](https://github.com/Fallen-Breath/PearlCannonHelper) 的算法，为 [360FTL Heavy](https://www.bilibili.com/video/BV1NC4y1x7WW) 重型矢量珍珠炮生成最优配置。

## 功能

- 🎯 **配置生成**: 输入目标坐标，自动搜索最优 TNT 配置
- 📊 **结果排序**: 支持按距离、Tick、TNT 数量等排序
- 🔄 **轨迹模拟**: 模拟珍珠飞行轨迹，显示每 tick 的位置和动量
- 💾 **配置持久化**: 自动保存配置到 JSON 文件
- 🖱️ **交互式界面**: 使用 RText 实现点击操作

## 安装

将 `pearl_properties_generator.pyz` 放入 MCDR 的 `plugins/` 目录。

## 命令

| 命令 | 说明 |
|------|------|
| `!!ppg` | 显示帮助 |
| `!!ppg set` | 打开配置界面 |
| `!!ppg set <key> <value>` | 设置配置项 |
| `!!ppg gen <x> <z>` | 生成珍珠炮配置 |
| `!!ppg trace <bits>` | 模拟珍珠轨迹 |
| `!!ppg reset` | 重置为默认配置 |

### 配置项

| 键 | 别名 | 默认值 | 说明 |
|----|------|--------|------|
| `pearl_x` | `px` | -99.0625 | 珍珠 X 坐标 |
| `pearl_z` | `pz` | 0.0625 | 珍珠 Z 坐标 |
| `player_y` | `py` | 139 | 玩家 Y 坐标 |
| `rotation` | - | 0 | 旋转方向 (0=None, 1=CW_90, 2=CW_180, 3=CCW_90) |
| `max_tnt` | - | 1820 | 最大 TNT 数量 |
| `ground_y` | `gy` | 0 | 地面 Y 坐标 |
| `max_tick` | - | 1000 | 最大模拟 tick |
| `max_results` | - | 100 | 最大结果数量 |

## 使用示例

1. 设置珍珠炮参数:
   ```
   !!ppg set px -99.0625
   !!ppg set pz 0.0625
   !!ppg set py 139
   ```

2. 生成配置:
   ```
   !!ppg gen -1649 0
   ```

3. 查看轨迹:
   ```
   !!ppg trace 100001110000110101000110001
   ```

## 构建

```bash
cd pearl_properties_generator
zip -r ../pearl_properties_generator.pyz mcdreforged.plugin.json pearl_properties_generator/
```

## 致谢

- [Fallen_Breath](https://github.com/Fallen-Breath) - 原始 PearlCannonHelper 项目
- [360FTL Heavy](https://www.bilibili.com/video/BV1NC4y1x7WW) - 重型矢量珍珠炮设计

## 许可证

MIT License
