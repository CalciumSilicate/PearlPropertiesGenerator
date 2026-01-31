from typing import List, Optional, TYPE_CHECKING

from mcdreforged.api.all import *

if TYPE_CHECKING:
    from .config import Config
    from .generator import SettingResult, TracePoint

PREFIX = "!!ppg"


class RTextUI:
    TITLE_COLOR = RColor.gold
    KEY_COLOR = RColor.aqua
    VALUE_COLOR = RColor.green
    BUTTON_COLOR = RColor.yellow
    DISABLED_COLOR = RColor.gray
    ERROR_COLOR = RColor.red
    HEADER_COLOR = RColor.light_purple

    @staticmethod
    def header(text: str) -> RTextBase:
        return RTextList(
            RText("═" * 10 + " ", color=RColor.dark_gray),
            RText(text, color=RTextUI.TITLE_COLOR, styles=RStyle.bold),
            RText(" " + "═" * 10, color=RColor.dark_gray),
        )

    @staticmethod
    def divider() -> RTextBase:
        return RText("─" * 40, color=RColor.dark_gray)

    @staticmethod
    def button(
        text: str,
        command: str,
        hover: str,
        color: RColor = None,
        bracket: bool = True,
    ) -> RTextBase:
        if color is None:
            color = RTextUI.BUTTON_COLOR
        btn = RText(text, color=color)
        btn.h(hover)
        btn.c(RAction.run_command, command)
        if bracket:
            return RTextList(
                RText("[", color=RColor.gray),
                btn,
                RText("]", color=RColor.gray),
            )
        return btn

    @staticmethod
    def suggest_button(
        text: str,
        command: str,
        hover: str,
        color: RColor = None,
        bracket: bool = True,
    ) -> RTextBase:
        if color is None:
            color = RTextUI.BUTTON_COLOR
        btn = RText(text, color=color)
        btn.h(hover)
        btn.c(RAction.suggest_command, command)
        if bracket:
            return RTextList(
                RText("[", color=RColor.gray),
                btn,
                RText("]", color=RColor.gray),
            )
        return btn

    @staticmethod
    def copy_button(text: str, copy_text: str, hover: str) -> RTextBase:
        btn = RText(text, color=RColor.green)
        btn.h(hover + f"\n§7{copy_text}")
        btn.c(RAction.copy_to_clipboard, copy_text)
        return RTextList(
            RText("[", color=RColor.gray),
            btn,
            RText("]", color=RColor.gray),
        )

    @staticmethod
    def key_value(key: str, value, editable_key: str = None) -> RTextBase:
        parts = [
            RText(f"  {key}: ", color=RTextUI.KEY_COLOR),
            RText(str(value), color=RTextUI.VALUE_COLOR),
        ]
        if editable_key:
            parts.append(RText(" "))
            parts.append(
                RTextUI.suggest_button(
                    "✎",
                    f"{PREFIX} set {editable_key} ",
                    f"点击修改 {key}",
                    color=RColor.gray,
                    bracket=False,
                )
            )
        return RTextList(*parts)


class SettingsUI:
    def __init__(self, config: "Config"):
        self.config = config

    def build(self) -> RTextBase:
        lines = [
            RTextUI.header("Pearl Properties Generator 配置"),
            RText(""),
        ]

        lines.append(RText("§e【珍珠炮参数】", color=RColor.yellow))
        lines.append(
            RTextUI.key_value("Pearl X (px)", f"{self.config.get('pearl_x'):.4f}", "px")
        )
        lines.append(
            RTextUI.key_value("Pearl Z (pz)", f"{self.config.get('pearl_z'):.4f}", "pz")
        )
        lines.append(
            RTextUI.key_value("Player Y (py)", f"{self.config.get('player_y'):.1f}", "py")
        )

        rotation_val = self.config.get("rotation")
        rotation_text = RTextList(
            RText(f"  Rotation: ", color=RTextUI.KEY_COLOR),
            RText(f"{self.config.get_rotation_name()} ({rotation_val})", color=RTextUI.VALUE_COLOR),
            RText(" "),
        )
        for i, name in enumerate(self.config.ROTATION_NAMES):
            if i == rotation_val:
                rotation_text.append(RText(f"[{name}]", color=RColor.green))
            else:
                rotation_text.append(
                    RTextUI.button(name, f"{PREFIX} set rotation {i}", f"设置为 {name}")
                )
            rotation_text.append(RText(" "))
        lines.append(rotation_text)

        lines.append(RText(""))
        lines.append(RText("§e【搜索限制】", color=RColor.yellow))
        lines.append(
            RTextUI.key_value("Max TNT", self.config.get("max_tnt"), "max_tnt")
        )
        lines.append(
            RTextUI.key_value("Ground Y (gy)", f"{self.config.get('ground_y'):.1f}", "gy")
        )
        lines.append(
            RTextUI.key_value("Max Tick", self.config.get("max_tick"), "max_tick")
        )
        lines.append(
            RTextUI.key_value("Max Results", self.config.get("max_results"), "max_results")
        )

        lines.append(RText(""))
        lines.append(RTextUI.divider())

        action_line = RTextList(
            RTextUI.button("重置默认", f"{PREFIX} reset", "重置所有配置为默认值", color=RColor.red),
            RText("  "),
            RTextUI.suggest_button("生成配置", f"{PREFIX} gen ", "输入目标坐标生成配置", color=RColor.green),
        )
        lines.append(action_line)

        return RTextList(*[RTextList(line, "\n") for line in lines])


class ResultsUI:
    PAGE_SIZE = 10

    def __init__(
        self,
        results: List["SettingResult"],
        dest_x: float,
        dest_z: float,
        page: int = 1,
        sort_by: str = "distance",
    ):
        self.results = results
        self.dest_x = dest_x
        self.dest_z = dest_z
        self.page = page
        self.sort_by = sort_by
        self.total_pages = max(1, (len(results) + self.PAGE_SIZE - 1) // self.PAGE_SIZE)

    def build(self) -> RTextBase:
        lines = [
            RTextUI.header(f"生成结果 - 目标 ({self.dest_x}, {self.dest_z})"),
            RText(""),
        ]

        sort_line = RTextList(RText("排序: ", color=RColor.gray))
        sort_options = [
            ("distance", "距离"),
            ("tick", "Tick"),
            ("total_tnt", "总TNT"),
            ("light_gray", "浅灰"),
            ("dark_gray", "深灰"),
        ]
        for key, name in sort_options:
            if key == self.sort_by:
                sort_line.append(RText(f"[{name}]", color=RColor.green))
            else:
                sort_line.append(
                    RTextUI.button(
                        name,
                        f"{PREFIX} page 1 {key}",
                        f"按{name}排序",
                    )
                )
            sort_line.append(RText(" "))
        lines.append(sort_line)
        lines.append(RText(""))

        lines.append(
            RTextList(
                RText(" # ", color=RTextUI.HEADER_COLOR),
                RText("│", color=RColor.dark_gray),
                RText(" 距离    ", color=RTextUI.HEADER_COLOR),
                RText("│", color=RColor.dark_gray),
                RText(" Tick ", color=RTextUI.HEADER_COLOR),
                RText("│", color=RColor.dark_gray),
                RText(" 浅灰 ", color=RTextUI.HEADER_COLOR),
                RText("│", color=RColor.dark_gray),
                RText(" 深灰 ", color=RTextUI.HEADER_COLOR),
                RText("│", color=RColor.dark_gray),
                RText(" 总TNT ", color=RTextUI.HEADER_COLOR),
                RText("│", color=RColor.dark_gray),
                RText(" 操作", color=RTextUI.HEADER_COLOR),
            )
        )
        lines.append(RTextUI.divider())

        start_idx = (self.page - 1) * self.PAGE_SIZE
        end_idx = min(start_idx + self.PAGE_SIZE, len(self.results))

        for i in range(start_idx, end_idx):
            r = self.results[i]
            row = RTextList(
                RText(f"{i + 1:>2} ", color=RColor.white),
                RText("│", color=RColor.dark_gray),
                RText(f" {r.distance:>6.4f} ", color=RColor.aqua),
                RText("│", color=RColor.dark_gray),
                RText(f" {r.tick:>4} ", color=RColor.yellow),
                RText("│", color=RColor.dark_gray),
                RText(f" {r.light_gray:>4} ", color=RColor.white),
                RText("│", color=RColor.dark_gray),
                RText(f" {r.dark_gray:>4} ", color=RColor.gray),
                RText("│", color=RColor.dark_gray),
                RText(f" {r.total_tnt:>5} ", color=RColor.green),
                RText("│", color=RColor.dark_gray),
            )

            row.append(
                RTextUI.copy_button("复制", r.bits, "点击复制比特序列")
            )
            row.append(RText(" "))

            detail_btn = RText("[详情]", color=RColor.aqua)
            detail_btn.h(
                f"§e位置: §f{r.position}\n"
                f"§e比特序列: §f{r.bits}\n"
                f"§eDirection: §f{r.direction}\n"
                f"§ePitch: §f{r.pitch}"
            )
            row.append(detail_btn)
            row.append(RText(" "))

            bits_clean = ''.join(c for c in r.bits if c in '01')
            row.append(
                RTextUI.button("轨迹", f"{PREFIX} trace {bits_clean}", "生成珍珠轨迹", color=RColor.light_purple)
            )

            lines.append(row)

        lines.append(RText(""))
        lines.append(RTextUI.divider())

        page_line = RTextList(
            RText(f"第 {self.page}/{self.total_pages} 页  ", color=RColor.gray)
        )

        if self.page > 1:
            page_line.append(
                RTextUI.button("◀ 上一页", f"{PREFIX} page {self.page - 1} {self.sort_by}", "上一页")
            )
        else:
            page_line.append(RText("[◀ 上一页]", color=RTextUI.DISABLED_COLOR))

        page_line.append(RText("  "))

        if self.page < self.total_pages:
            page_line.append(
                RTextUI.button("下一页 ▶", f"{PREFIX} page {self.page + 1} {self.sort_by}", "下一页")
            )
        else:
            page_line.append(RText("[下一页 ▶]", color=RTextUI.DISABLED_COLOR))

        page_line.append(RText("  "))
        page_line.append(
            RTextUI.button("返回设置", f"{PREFIX} set", "返回配置界面", color=RColor.gray)
        )

        lines.append(page_line)

        return RTextList(*[RTextList(line, "\n") for line in lines])


class TraceUI:
    PAGE_SIZE = 10

    def __init__(
        self,
        traces: List["TracePoint"],
        bits: str,
        page: int = 1,
    ):
        self.traces = traces
        self.bits = bits
        self.page = page
        self.total_pages = max(1, (len(traces) + self.PAGE_SIZE - 1) // self.PAGE_SIZE)

    def build(self) -> RTextBase:
        lines = [
            RTextUI.header("珍珠轨迹模拟"),
            RText(""),
        ]

        info_line = RTextList(
            RText("比特序列: ", color=RColor.gray),
            RText(self.bits, color=RColor.aqua),
            RText(" "),
            RTextUI.copy_button("复制", self.bits, "点击复制比特序列"),
        )
        lines.append(info_line)
        lines.append(RText(""))

        lines.append(
            RTextList(
                RText(" Tick ", color=RTextUI.HEADER_COLOR),
                RText("│", color=RColor.dark_gray),
                RText(" 区块      ", color=RTextUI.HEADER_COLOR),
                RText("│", color=RColor.dark_gray),
                RText(" 位置                              ", color=RTextUI.HEADER_COLOR),
                RText("│", color=RColor.dark_gray),
                RText(" 操作", color=RTextUI.HEADER_COLOR),
            )
        )
        lines.append(RTextUI.divider())

        start_idx = (self.page - 1) * self.PAGE_SIZE
        end_idx = min(start_idx + self.PAGE_SIZE, len(self.traces))

        for i in range(start_idx, end_idx):
            t = self.traces[i]
            pos_str_raw = f"{t.position.x} {t.position.y} {t.position.z}"
            pos_str = f"({t.position.x:.4f}, {t.position.y:.4f}, {t.position.z:.4f})"
            mom_str = f"({t.momentum.x:.6f}, {t.momentum.y:.6f}, {t.momentum.z:.6f})"
            
            row = RTextList(
                RText(f" {t.tick:>4} ", color=RColor.yellow),
                RText("│", color=RColor.dark_gray),
                RText(f" {t.chunk:<9} ", color=RColor.green),
                RText("│", color=RColor.dark_gray),
                RText(f" {pos_str:<34} ", color=RColor.aqua),
                RText("│", color=RColor.dark_gray),
            )

            row.append(
                RTextUI.copy_button("位置", pos_str_raw, "点击复制位置")
            )
            row.append(RText(" "))

            detail_btn = RText("[动量]", color=RColor.light_purple)
            detail_btn.h(f"§e动量: §f{mom_str}")
            detail_btn.c(RAction.copy_to_clipboard, mom_str)
            row.append(detail_btn)

            lines.append(row)

        lines.append(RText(""))
        lines.append(RTextUI.divider())

        page_line = RTextList(
            RText(f"第 {self.page}/{self.total_pages} 页 (共 {len(self.traces)} tick)  ", color=RColor.gray)
        )

        bits_clean = ''.join(c for c in self.bits if c in '01')

        if self.page > 1:
            page_line.append(
                RTextUI.button("◀ 上一页", f"{PREFIX} trace {bits_clean} {self.page - 1}", "上一页")
            )
        else:
            page_line.append(RText("[◀ 上一页]", color=RTextUI.DISABLED_COLOR))

        page_line.append(RText("  "))

        if self.page < self.total_pages:
            page_line.append(
                RTextUI.button("下一页 ▶", f"{PREFIX} trace {bits_clean} {self.page + 1}", "下一页")
            )
        else:
            page_line.append(RText("[下一页 ▶]", color=RTextUI.DISABLED_COLOR))

        page_line.append(RText("  "))
        page_line.append(
            RTextUI.button("返回设置", f"{PREFIX} set", "返回配置界面", color=RColor.gray)
        )

        lines.append(page_line)

        return RTextList(*[RTextList(line, "\n") for line in lines])


def show_help(source: CommandSource):
    lines = [
        RTextUI.header("Pearl Properties Generator 帮助"),
        RText(""),
        RTextList(
            RText(f"  {PREFIX} ", color=RColor.gold),
            RText("- 显示此帮助", color=RColor.gray),
        ),
        RTextList(
            RText(f"  {PREFIX} set ", color=RColor.gold),
            RText("- 打开配置界面", color=RColor.gray),
        ),
        RTextList(
            RText(f"  {PREFIX} set <key> <value> ", color=RColor.gold),
            RText("- 设置配置项", color=RColor.gray),
        ),
        RTextList(
            RText(f"  {PREFIX} gen <dest_x> <dest_z> ", color=RColor.gold),
            RText("- 生成珍珠炮配置", color=RColor.gray),
        ),
        RTextList(
            RText(f"  {PREFIX} trace <bits> ", color=RColor.gold),
            RText("- 模拟珍珠轨迹", color=RColor.gray),
        ),
        RTextList(
            RText(f"  {PREFIX} reset ", color=RColor.gold),
            RText("- 重置为默认配置", color=RColor.gray),
        ),
        RText(""),
        RText("§7可用配置项: px, pz, py, rotation, max_tnt, gy, max_tick, max_results"),
    ]
    source.reply(RTextList(*[RTextList(line, "\n") for line in lines]))


def show_error(source: CommandSource, message: str):
    source.reply(
        RTextList(
            RText("[PPG] ", color=RColor.gold),
            RText(message, color=RTextUI.ERROR_COLOR),
        )
    )


def show_success(source: CommandSource, message: str):
    source.reply(
        RTextList(
            RText("[PPG] ", color=RColor.gold),
            RText(message, color=RColor.green),
        )
    )
