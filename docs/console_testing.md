# 关键节点控制台测试（main，1.1.4）

按当前脚本整理，尚未在游戏进程中逐条执行。普通命令逐行输入控制台；标为 `pdx` 的代码放到 Script Runner 的 Effect 页执行。正式版不需要 `crb_debug` 测试事件。

## 准备

Steam 启动选项加入 `-debug_mode`，新开 1836 年迦太基的非铁人游戏，按 `~` 打开控制台。切到英文输入法。先留一份暂停的测试存档，各个互斥分支分别读档测试。

```text
tag TUN
money 10000000
```

`TUN` 仍是迦太基的国家代码。`own` 会改变整个指定地区的归属，也可能移走分裂地区里其他国家的部分；它适合快速布置测试场景。下文“一块地”用一个地区演示，成立按钮实际也接受本国持有的分裂州部分。每组命令执行后解除暂停，让游戏经过一次相关结算；大部分主线检查在月度结算进行。

新开局还应直接在海军、建筑与政治界面确认 **3 艘护卫舰、1 级海军部门、经济干预、移民控制**。这些历史设置不回写旧存档。

## 一块地成立商站、行省

从和平的新开局执行：

```text
own STATE_CONSTANTINE TUN
```

预期：出现“迦太基的领土”日志，里面有“处置努米底亚”。选择商站或行省后，只转交本国在对应地区持有的非首都土地。选择行省会增加恶名；可在点击前后比较。初始派系日志也可以正常启动，提前释放努米底亚不应阻断它。

再从新开局单独测试高卢：

```text
own STATE_PROVENCE TUN
```

预期：即使没有推进“汉尼拔再临”“复仇之路”，仍能在领土日志中“处置高卢”。其他主线日志中不再有成立商站、行省按钮。

下表每行都是独立场景，可从干净存档任选一条输入；按钮都属于“迦太基的领土”。

| 地区 | 控制台命令 | 成立后的代码 |
| --- | --- | --- |
| 的黎波里 | `own STATE_TRIPOLI TUN` | `TRP` |
| 努米底亚 | `own STATE_CONSTANTINE TUN` | `NUM` |
| 伊比利亚 | `own STATE_MURCIA TUN` | `IBT` |
| 高卢 | `own STATE_PROVENCE TUN` | `GLT` |
| 阿尔卑斯／雪山 | `own STATE_PIEDMONT TUN` | `SNT` |
| 意大利／罗马 | `own STATE_APULIA TUN` | `IOP` 或 `RPR`，两者互斥 |
| 隐藏：毛里塔尼亚 | `own STATE_FEZ TUN` | `CPM` |
| 隐藏：埃及 | `own STATE_MIDDLE_EGYPT TUN` | `CPE` |
| 隐藏：腓尼基 | `own STATE_LEBANON TUN` | `CPF` |
| 隐藏：叙利亚 | `own STATE_ALEPPO TUN` | `CPS` |
| 隐藏：美索不达米亚 | `own STATE_BAGHDAD TUN` | `CPB` |
| 隐藏：阿拉伯 | `own STATE_YEMEN TUN` | `CPA` |

六个隐藏地区均提供商站与行省选项，选择后用对应国家的附庸关系、名称和旗帜核对：商站免成立恶名，行省按原费用增加恶名；同一地区不能再成立另一种形式。未取得相关土地时不显示对应按钮；取得一个地区的土地不应使其他隐藏地区一起出现。

补充检查：成立 `NUM` 后执行 `own STATE_ORAN TUN`，在“迦太基的领土”中点击对应的“扩张努米底亚商站／行省”。预期：奥兰只交给 `NUM`，其他附庸区域不受影响，首都保留。另取得 `own STATE_MARRAKECH TUN` 并成立毛里塔尼亚附庸时，应看到它自己的扩张按钮，而非与努米底亚合并。原有一键扩张决议也保留。

确认弹窗的再次校验可这样测：先取得君士坦丁并点开“处置努米底亚”，暂停时执行 `own STATE_CONSTANTINE FRA`，再返回弹窗。预期：不能在失去土地后继续成立，也不应被扣行省恶名。战争中、目标国家已存在时，同样应阻止重复成立。

## 共享冷却与治理说明

从和平的新存档逐条输入：

```text
own STATE_CONSTANTINE TUN
own STATE_PROVENCE TUN
own STATE_LEBANON TUN
```

先点“处置努米底亚”并选择保留直辖，再立即查看其他地区：应仍可处置。然后实际成立努米底亚商站或行省：高卢、腓尼基的按钮应保留显示，但因三个月交接期而不能点击；日志状态应提示正在交接。让游戏时间正常经过三个月，冷却消失后应可再次成立另一处。

若测试时已经预先打开多个处置弹窗，先成功成立其中一个，再回到其他弹窗：成立选项应受冷却限制，不能建第二个国家或扣行省恶名。

悬停商站、行省选项，检查区域会变成怎样的商埠或总督辖区，应看到形象化的地方描述，不能再看到逐条“启用某法律”。日志介绍与外交关系说明应能查看商站、行省的通用介绍和 30%／50% 缴款差别。

连续测试其他功能时，可以在 `inspect_country TUN` 打开的 Script Runner → Effect 中手动解除冷却：

```pdx
c:TUN = { remove_modifier = crb_territory_disposition_cooldown }
```

这只是测试捷径，不能用它证明自然到期计时正确。

## “高卢人？”接壤事件

另开一份尚未触发该事件的存档，执行：

```text
own STATE_ALGIERS FRA
own STATE_CONSTANTINE TUN
```

预期：迦太基与法兰西在北非实际陆地接壤后，自动出现“高卢人？”；不需要战争或参加战斗。让月度检查运行后观察。

反向测试用另一份新存档，只执行 `own STATE_PROVENCE TUN`：即使与欧洲的法兰西土地接壤，也不应因此触发。第一轮开启后会每 60 个月重选；后续不再要求接壤，只要法国仍在北非持地即可。三项分别测试：赠款应从迦太基扣除选择时年 GDP 的 1%，并给法国等额入账、关系 +20、双向停战 60 个月；强硬为关系 -50、击杀率 +10% 持续 60 个月；顺其自然无额外收益，五年后再议。与法国交战或在外交博弈中敌对时，赠款选项仍显示，但不能选择。

仅检查这个事件的中文弹窗可输入 `event crb_flavor.17 TUN`。手动点事件会绕过正常调度，不能用来证明接壤条件正确。

只快速验证“到期重选”，可在 `inspect_country TUN` 的 Script Runner → Effect 运行：

```pdx
c:TUN = {
    remove_modifier = crb_gallic_appeasement
    remove_modifier = crb_flavor_gallic_legacy
    remove_modifier = crb_gallic_nonintervention
    crb_check_french_border_effect = yes
}
```

这是模拟路线到期，不替代实际经过五年的计时测试。再次选择时不能叠加重复路线。清除法国全部北非直辖土地可测试终止：

```pdx
c:FRA = {
    every_scope_state = {
        limit = { crb_is_north_african_state_trigger = yes }
        set_state_owner = c:TUN
    }
}
c:TUN = { crb_check_french_border_effect = yes }
```

预期：不再发出新一轮弹窗，清理路线标记与专属修正；已签的停战协议保留原期限。

## 汉诺派、巴卡派与三年结局

先用君士坦丁命令让“汉诺派与巴卡派”日志自然激活，处理开场弹窗。然后在控制台输入：

```text
inspect_country TUN
```

在打开的国家检查器进入 **Script Runner → Effect**。如果界面没有这个入口，可用控制台 `explorer`，Provider 选择 Countries，选中 `TUN` 后打开 Script Runner。下列 `pdx` 代码粘在这里，不加 `effect` 命令前缀。

巴卡派胜利：

```pdx
c:TUN = {
    je:je_crb_hanno_barca = {
        set_bar_progress = { name = crb_hanno_barca_progress_bar value = 100 }
    }
}
```

预期：日志按胜利结果结算；接受巴卡胜利弹窗后立即加入“汉尼拔再临”，不需要再改殖民法律。之后开启殖民剥削应能解锁“汉诺航海记”，不会重复开启汉尼拔开场或重复发放宣称。汉诺派胜利请读取派系尚未结束的存档，把上述 `value = 100` 改成 `value = 0`；应进入汉诺路线，可以开启“汉诺航海记”。

测试三年僵局，在另一份派系仍激活的存档运行：

```pdx
c:TUN = {
    je:je_crb_hanno_barca = {
        set_bar_progress = { name = crb_hanno_barca_progress_bar value = 50 }
    }
    set_variable = { name = crb_hb_elapsed_months value = 35 }
}
```

预期：下一次月度结算进入三年最终抉择。单独 `event crb_hanno_barca.2 TUN` 只适合预览弹窗，不能替代派系日志结算。

## 汉尼拔再临与复仇之路

进入巴卡路线后，可按需取得下列土地，让主线自行记录进度：

| 节点 | 逐条执行 `own 地区代码 TUN` 的地区代码 |
| --- | --- |
| 的黎波里 | `STATE_TRIPOLI`、`STATE_LIBYA` |
| 努米底亚 | `STATE_ALGIERS`、`STATE_CONSTANTINE`、`STATE_ORAN` |
| 叙拉古 | `STATE_SICILY` |
| 地中海诸岛 | `STATE_BALEARIC_ISLANDS`、`STATE_MALTA`、`STATE_CRETE`、`STATE_CYPRUS` |
| 伊比利亚入口 | `STATE_LOWER_ANDALUSIA` |
| 新迦太基／复仇日志入口 | 本土伊比利亚累计至少三个地区，如 `STATE_MURCIA`、`STATE_VALENCIA`、`STATE_CATALONIA` |
| 推罗 | `STATE_LEBANON` |

例如新迦太基节点：

```text
own STATE_MURCIA TUN
own STATE_VALENCIA TUN
own STATE_CATALONIA TUN
```

预期：月度结算后出现对应事件，并可开启“复仇之路”。完成一部分占领后先成立商站、行省，再继续推进，也应计入实际附庸持有的地区；这是检查本次附庸兼容的方式。

在“复仇之路”中依次点击阶段按钮，然后取得对应土地解锁下一阶段：

| 已点击的阶段 | 下阶段要求的地区 |
| --- | --- |
| 第一阶段 | `STATE_CATALONIA`、`STATE_VALENCIA`、`STATE_MURCIA`、`STATE_UPPER_ANDALUSIA`、`STATE_LOWER_ANDALUSIA` |
| 第二阶段 | `STATE_LANGUEDOC`、`STATE_PROVENCE`、`STATE_RHONE` |
| 第三阶段 | `STATE_WEST_SWITZERLAND`、`STATE_EAST_SWITZERLAND`、`STATE_SAVOY`、`STATE_PIEDMONT`、`STATE_LOMBARDY`、`STATE_VENETIA` |
| 第四阶段 | `STATE_LAZIO`；取得后等月度结算，检查罗马终局 |

仍使用 `own 地区代码 TUN`。直接调用终局事件只能预览文本，不能验证这些土地要求。

## 文化复兴与 U 型港

先在控制台解锁两个需要的科技：

```text
research intensive_agriculture
research reinforced_concrete
```

在“迦太基文化复兴”日志点击治理盐碱地；下一次月度结算检查 U 型港解锁事件。开始建造 `building_crb_cothon` 但等级仍为 0 时，经过月度结算不能弹出港口完成事件；建筑至少建成一级后，下一次月度结算才记录目标并触发完成事件。建筑界面应显示新的 U 型港图片。种植园目标需要累计 20 级脚本计入的种植园，例如葡萄种植园。

为了快建，可暂时在控制台输入 `fastbuild`、`fasthire`，然后在建筑界面下单；两者是开关，可能同时影响 AI，测试后各输入一次关闭。

把十年盐碱地测试缩短到下一次年度结算：先确保已经点击治理按钮，再在 Script Runner 运行：

```pdx
c:TUN = { set_variable = { name = crb_salt_years value = 9 } }
```

预期：下一次年度结算记录治理完成，而非立刻完成。只改游戏日期不能代替实际年度结算。

快速布置塔尼特信仰占比测试，在 Script Runner 运行：

```pdx
c:TUN = {
    every_scope_state = {
        convert_population = { target = rel:crb_tanit value = 1 }
    }
}
```

预期：塔尼特人口达到至少 80% 后，月度结算记录宗教目标。四项目标完成后再检查复兴终局。

## 汉诺航海记

进入汉诺路线并等航海日志激活，控制台逐条执行：

```text
own STATE_FEZ TUN
own STATE_WEST_SAHARA TUN
own STATE_SENEGAL TUN
own STATE_SOUTH_CAMEROON TUN
```

在刻尔涅（`STATE_WEST_SAHARA`）建至少一级港口。预期：下次月度结算分别记录利克苏斯、刻尔涅、克雷特斯之河、诸神之车。

保持和平，在 Script Runner 设置：

```pdx
c:TUN = { set_variable = { name = crb_hv_peace_months value = 119 } }
```

预期：下次月度结算达到 120 个月和平，并在其他目标满足时完成航海日志。另读一份存档，在战争中测试相同计数，应重置为零。

## 总督制、图标、庇护与改名

分别成立一处商站和一处行省，政治界面的治理原则应是“总督治理”，属于君主制变体；元首头衔为总督。两种附庸的成立选项、类型名称和扩张按钮，应分别显示船舶贸易、官署卷册的专属图标。各区域正文、引语和选项提示应有各自的地方描写。

打开已成立附庸的国家界面，检查与迦太基的附庸关系图标：商站应为船舶贸易图标，行省应为官署卷册图标，不能显示占位符。这一项与文字中的小图标分别检查；国家面板通过外交行动定义的 `texture` 读取图片。更新 1.1.4 后完全退出并重启游戏，再读取原存档即可检查，无需重新建立附庸。

庇护的原始修正是每周自由欲变化额外 `-0.05`、正向增长速度 `-5%`；宗主国霸权为各附庸每周额外 `-0.02`。在附庸自由欲明细里对照，不应再出现旧的每周 `-25`、`-10`；最终周变化还受原版公式影响。旧存档中的实际附庸会在月度进行一次性总督制迁移。

“汉诺航海记”四个土地提示应使用与地图相同的模组地名：毛里塔尼亚、刻尔涅、克雷特斯、诸神之车，不能仍显示原版地区名称。

## 公司、名品美术与音乐

正常成立公司：控制台执行 `research corporate_charters`。按公司说明取得对应已整合地区、至少三级相关建筑，再从公司界面成立。推罗可用 `own STATE_LEBANON TUN` 布置土地，塞浦路斯可用 `own STATE_CYPRUS TUN`。

只快速预览公司徽记时，在 Script Runner 按需任选一行运行；分别读档可以避免公司数量上限干扰：

```pdx
c:TUN = { add_company = company_type:company_crb_carthaginian_trade_house }
```

```pdx
c:TUN = { add_company = company_type:company_crb_tyrian_purple }
```

```pdx
c:TUN = { add_company = company_type:company_crb_punic_wine }
```

```pdx
c:TUN = { add_company = company_type:company_crb_cyprus_copper }
```

公司列表和详情中的公司徽记应使用定制图标；详情背景分别恢复为原版港口造船、轻工业、农业、采矿插图。这只检查公司展示，不代替正常成立条件和经济繁荣测试。“推罗紫”“布匿佳酿”图标还应在对应公司名品说明、商品详情中检查；未达到游戏的名品解锁条件时，不能据此认定繁荣机制已经通过。

音乐播放器启用《迦太基》，选择 **Weighted／加权**。控制台执行：

```text
Music.ListTracks
```

找到 `crb_carthage_theme`：迦太基在 1836 年 1 月权重为 **100000**，之后为 **500**；切换其他正常国家时为 **1**。可以输入 `tag FRA` 对照，再 `tag TUN` 切回来。

点播测试可在 Script Runner 运行：

```pdx
c:TUN = { play_music_cue = crb_carthage_theme }
```

点播仍受播放器禁用、曲目冷却和当前曲目可否中断限制。开局优先测试要新开游戏；读取存档不会重新调用开局点播。不要把随机或最少播放模式当作加权模式测试。

## GDP 比例收入奖励

在国库／预算界面记录 GDP 和额外收入，分别读档执行：

| 事件命令 | 选择 | 每周额外收入 | 持续 |
| --- | --- | --- | --- |
| `event crb_flavor.3 TUN` | 出口特许收益选项 | 选择时年 GDP × 0.015% | 60 个月 |
| `event crb_flavor.4 TUN` | 铸币收益选项 | 选择时年 GDP × 0.0075% | 36 个月 |
| `event crb_flavor.5 TUN` | 出版版税选项 | 选择时年 GDP × 0.015% | 60 个月 |
| `event crb_flavor.10 TUN` | 打捞特许收益选项 | 选择时年 GDP × 0.025% | 60 个月 |
| `event crb_flavor.16 TUN` | 私掠收益选项 | 选择时年 GDP × 0.025% | 36 个月 |

例如年 GDP 为 1,000 万，三档每周分别增加 750、1,500、2,500。收益进入每周预算，不是一笔立刻增加的国库拨款；提示应同时显示 GDP 比例和实际金额。换用 GDP 不同的存档重复测试，金额应同比变化。修正生效后的 GDP 变化不重算已确定的金额，重复选同一修正的刷新行为沿用游戏原有处理。

`money` 命令只加国库，不改变 GDP，不能用它检验比例缩放。私掠事件的一次性条件仍有效，单独从满足条件的存档测试。

## 中文显示快速检查

更新 1.1.3 后完全退出并重启游戏，选择简体中文。国家名、布匿文化、塔尼特宗教、日志名和按钮都应显示中文。事件界面可用下列命令抽查，每次单独执行、处理完再测下一项：

```text
event crb_carthage.1 TUN
event crb_flavor.1 TUN
event crb_hanno_barca_random.10 TUN
```

如果显示 `crb_…`、`je_crb_…`，表示本地化键没有加载；它和方框、问号这类字体或编码现象的排查方向不同。1.1.1 已恢复历史缺失文本，并检查 UTF-8 BOM、重复键及全部 74 个事件的文本引用。

## 依据与检查范围

地区、事件、变量、公司和日志代码来自本仓库当前 `common/` 与 `events/` 脚本。控制台基础语法可参照 [Victoria 3 Wiki](https://vic3.paradoxwikis.com/Console_commands)；国家检查器入口见 [开发日志 164](https://forum.paradoxplaza.com/forum/developer-diary/victoria-3-dev-diary-164-marvelous-modding-monday.1868975/)。Script Runner 效果对照 [1.15 导出的效果文档](https://github.com/Victoria-3-Modding-Co-op/Modding-Digests/blob/main/1.15.0/docs/effects.log)，音乐行为对照 [1.15 音乐定义](https://github.com/Victoria-3-Modding-Co-op/Modding-Digests/blob/main/1.15.0/types/music.md)。

仓库的 `python -m unittest discover -s tests -v` 检查数据和脚本条件，游戏里的实际弹窗、贴图、音频和计时仍按上述流程验收。
