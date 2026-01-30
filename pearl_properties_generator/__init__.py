from typing import Dict, List, Optional

from mcdreforged.api.all import *

from .config import Config
from .generator import PearlPropertiesGenerator, SettingResult, SortBy, TraceSimulator
from .ui import (
    PREFIX,
    ResultsUI,
    SettingsUI,
    TraceUI,
    show_error,
    show_help,
    show_success,
)


config: Optional[Config] = None
cached_results: Dict[str, List[SettingResult]] = {}
cached_dest: Dict[str, tuple] = {}


def get_cache_key(source: CommandSource) -> str:
    if isinstance(source, PlayerCommandSource):
        return source.player
    return "__console__"


def on_load(server: PluginServerInterface, old):
    global config
    config = Config(server)

    server.register_help_message(PREFIX, "Pearl Properties Generator - 珍珠炮配置生成器")

    server.register_command(
        Literal(PREFIX)
        .runs(lambda src: show_help(src))
        .then(
            Literal("set")
            .runs(cmd_show_settings)
            .then(
                Text("key")
                .then(
                    GreedyText("value")
                    .runs(lambda src, ctx: cmd_set_config(src, ctx["key"], ctx["value"]))
                )
            )
        )
        .then(
            Literal("reset")
            .runs(cmd_reset_config)
        )
        .then(
            Literal("gen")
            .then(
                Float("dest_x")
                .then(
                    Float("dest_z")
                    .runs(lambda src, ctx: cmd_generate(src, ctx["dest_x"], ctx["dest_z"]))
                )
            )
        )
        .then(
            Literal("page")
            .then(
                Integer("page_num")
                .runs(lambda src, ctx: cmd_show_page(src, ctx["page_num"], "distance"))
                .then(
                    Text("sort_by")
                    .runs(lambda src, ctx: cmd_show_page(src, ctx["page_num"], ctx["sort_by"]))
                )
            )
        )
        .then(
            Literal("trace")
            .then(
                Text("bits")
                .runs(lambda src, ctx: cmd_trace(src, ctx["bits"], 1))
                .then(
                    Integer("page_num")
                    .runs(lambda src, ctx: cmd_trace(src, ctx["bits"], ctx["page_num"]))
                )
            )
        )
    )


def on_unload(server: PluginServerInterface):
    pass


def cmd_show_settings(source: CommandSource):
    ui = SettingsUI(config)
    source.reply(ui.build())


def cmd_set_config(source: CommandSource, key: str, value: str):
    real_key = Config.resolve_key(key)
    if real_key is None:
        show_error(source, f"未知的配置项: {key}")
        show_error(source, f"可用配置项: {', '.join(Config.CONFIG_KEYS)}")
        return

    if config.set(key, value):
        show_success(source, f"已设置 {real_key} = {config.get(real_key)}")
        cmd_show_settings(source)
    else:
        show_error(source, f"设置失败: 值 '{value}' 无效")


def cmd_reset_config(source: CommandSource):
    config.reset()
    show_success(source, "已重置所有配置为默认值")
    cmd_show_settings(source)


def cmd_generate(source: CommandSource, dest_x: float, dest_z: float):
    source.reply(RText("[PPG] 正在生成配置，请稍候...", color=RColor.yellow))

    generator = PearlPropertiesGenerator(
        pearl_x=config.get("pearl_x"),
        pearl_z=config.get("pearl_z"),
        player_y=config.get("player_y"),
        rotation=config.get("rotation"),
        max_tnt=config.get("max_tnt"),
        ground_y=config.get("ground_y"),
        max_tick=config.get("max_tick"),
        dest_x=dest_x,
        dest_z=dest_z,
        max_results=config.get("max_results"),
    )

    results = generator.generate(sort_by=SortBy.DISTANCE)

    cache_key = get_cache_key(source)
    cached_results[cache_key] = results
    cached_dest[cache_key] = (dest_x, dest_z)

    if not results:
        show_error(source, "未找到任何有效配置")
        return

    show_success(source, f"找到 {len(results)} 个配置")
    ui = ResultsUI(results, dest_x, dest_z, page=1, sort_by="distance")
    source.reply(ui.build())


def cmd_show_page(source: CommandSource, page_num: int, sort_by: str):
    cache_key = get_cache_key(source)

    if cache_key not in cached_results or not cached_results[cache_key]:
        show_error(source, "没有缓存的结果，请先使用 !!ppg gen <x> <z> 生成")
        return

    results = cached_results[cache_key]
    dest_x, dest_z = cached_dest.get(cache_key, (0, 0))

    sort_map = {
        "distance": SortBy.DISTANCE,
        "tick": SortBy.TICK,
        "total_tnt": SortBy.TOTAL_TNT,
        "light_gray": SortBy.LIGHT_GRAY,
        "dark_gray": SortBy.DARK_GRAY,
    }

    sort_enum = sort_map.get(sort_by, SortBy.DISTANCE)

    if sort_enum == SortBy.DISTANCE:
        results.sort(key=lambda x: x.distance)
    elif sort_enum == SortBy.TICK:
        results.sort(key=lambda x: x.tick)
    elif sort_enum == SortBy.TOTAL_TNT:
        results.sort(key=lambda x: x.total_tnt)
    elif sort_enum == SortBy.LIGHT_GRAY:
        results.sort(key=lambda x: x.light_gray)
    elif sort_enum == SortBy.DARK_GRAY:
        results.sort(key=lambda x: x.dark_gray)

    total_pages = max(1, (len(results) + 9) // 10)
    page_num = max(1, min(page_num, total_pages))

    ui = ResultsUI(results, dest_x, dest_z, page=page_num, sort_by=sort_by)
    source.reply(ui.build())


def cmd_trace(source: CommandSource, bits: str, page_num: int):
    bits_clean = ''.join(c for c in bits if c in '01')
    if len(bits_clean) != 27:
        show_error(source, f"无效的比特序列: 需要27位，得到{len(bits_clean)}位")
        return

    simulator = TraceSimulator(
        pearl_x=config.get("pearl_x"),
        pearl_z=config.get("pearl_z"),
        player_y=config.get("player_y"),
        rotation=config.get("rotation"),
        ground_y=config.get("ground_y"),
        max_tick=config.get("max_tick"),
    )

    traces = simulator.simulate(bits_clean)

    if not traces:
        show_error(source, "无法生成轨迹，请检查比特序列")
        return

    total_pages = max(1, (len(traces) + 9) // 10)
    page_num = max(1, min(page_num, total_pages))

    ui = TraceUI(traces, bits_clean, page=page_num)
    source.reply(ui.build())
