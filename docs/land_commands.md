# 领土获取与快速吞并（1.3.2）

普通命令在开启 `-debug_mode` 后的控制台逐条输入。`pdx` 代码放入 `inspect_country TUN` → Script Runner → Effect，不加 `effect` 前缀。

## 快速吞并整个国家

```text
tag TUN
annex FRA
```

这会把法国当前拥有的土地吞并给迦太基。`annex` 后只写目标代码；不是 `annex FRA TUN`。换成 `annex SPA`、`annex POR`、`annex TUR` 可分别吞并西班牙、葡萄牙、奥斯曼。目标必须在当前存档中存在。

一次吞并多个国家，整段放 Script Runner：

```pdx
c:TUN = {
    if = { limit = { exists = c:FRA } annex = c:FRA }
    if = { limit = { exists = c:SPA } annex = c:SPA }
    if = { limit = { exists = c:POR } annex = c:POR }
    if = { limit = { exists = c:TUR } annex = c:TUR }
    if = { limit = { exists = c:EGY } annex = c:EGY }
    if = { limit = { exists = c:MOR } annex = c:MOR }
    if = { limit = { exists = c:ALD } annex = c:ALD }
    if = { limit = { exists = c:TRI } annex = c:TRI }
    if = { limit = { exists = c:SIC } annex = c:SIC }
    if = { limit = { exists = c:SAR } annex = c:SAR }
    if = { limit = { exists = c:PAP } annex = c:PAP }
    if = { limit = { exists = c:AUS } annex = c:AUS }
    if = { limit = { exists = c:PRU } annex = c:PRU }
    if = { limit = { exists = c:BEL } annex = c:BEL }
    if = { limit = { exists = c:NET } annex = c:NET }
    if = { limit = { exists = c:SWI } annex = c:SWI }
}
```

也可使用 `c:TUN = { annex_with_incorporation = c:FRA }` 保留目标州原有的整合状态。吞并不会自动完成主线阶段、建好港口或跳过和平与冷却要求。用 `own` 测单个地区更方便保留其他国家作对照。

## 全部土地一览与整段获取

下方列出全部 25 个可成立辖区；合并主线额外目标后共 152 个不同地区。

[控制台纯命令](testing/own_all_mod_lands.txt)：逐行执行。

[整段获取全部土地](testing/own_all_mod_lands.pdx)：将文件全文粘贴到 Script Runner 的 Effect，一次执行。两者均将范围内整个地区（含分割州）交给 TUN；在未建立属地的测试存档使用，避免收回已经分配的土地。

## 的黎波里 — TRP

```text
own STATE_TRIPOLI TUN
own STATE_LIBYA TUN
own STATE_LIBYAN_DESERT TUN
```

## 努米底亚 — NUM

```text
own STATE_ALGIERS TUN
own STATE_CONSTANTINE TUN
own STATE_ORAN TUN
```

## 伊比利亚 — IBT

```text
own STATE_MURCIA TUN
own STATE_VALENCIA TUN
own STATE_CATALONIA TUN
own STATE_ARAGON TUN
own STATE_LOWER_ANDALUSIA TUN
own STATE_UPPER_ANDALUSIA TUN
own STATE_NEW_CASTILE TUN
own STATE_OLD_CASTILE TUN
own STATE_LEON TUN
own STATE_EXTREMADURA TUN
own STATE_GALICIA TUN
own STATE_ASTURIAS TUN
own STATE_BASQUE_COUNTRY TUN
```

## 纳尔波高卢 — GLT

```text
own STATE_PROVENCE TUN
own STATE_LANGUEDOC TUN
own STATE_RHONE TUN
own STATE_POITOU TUN
own STATE_GUYENNE TUN
own STATE_AUVERGNE_LIMOUSIN TUN
own STATE_BURGUNDY TUN
own STATE_AQUITAINE TUN
```

## 阿尔卑斯／雪山 — SNT

```text
own STATE_WEST_SWITZERLAND TUN
own STATE_EAST_SWITZERLAND TUN
own STATE_SAVOY TUN
own STATE_PIEDMONT TUN
own STATE_LOMBARDY TUN
own STATE_VENETIA TUN
```

## 意大利／罗马 — IOP, RPR

```text
own STATE_LAZIO TUN
own STATE_ABRUZZO TUN
own STATE_CAMPANIA TUN
own STATE_APULIA TUN
own STATE_CALABRIA TUN
```

## 毛里塔尼亚 — CPM

```text
own STATE_FEZ TUN
own STATE_MARRAKECH TUN
own STATE_AL_RIF TUN
own STATE_INNER_MOROCCO TUN
```

## 埃及 — CPE

```text
own STATE_UPPER_EGYPT TUN
own STATE_MIDDLE_EGYPT TUN
own STATE_EGYPTIAN_DESERT TUN
own STATE_MATRUH TUN
own STATE_SINAI TUN
```

## 腓尼基 — CPF

```text
own STATE_LEBANON TUN
```

## 叙利亚 — CPS

```text
own STATE_SYRIA TUN
own STATE_ALEPPO TUN
own STATE_DEIR_EZ_ZOR TUN
own STATE_PALESTINE TUN
own STATE_TRANSJORDAN TUN
```

## 美索不达米亚 — CPB

```text
own STATE_MOSUL TUN
own STATE_BAGHDAD TUN
own STATE_BASRA TUN
```

## 阿拉伯 — CPA

```text
own STATE_HAIL TUN
own STATE_HEDJAZ TUN
own STATE_YEMEN TUN
own STATE_OMAN TUN
own STATE_ABU_DHABI TUN
```

## 卢西塔尼亚 — XLU

```text
own STATE_ENTRE_DOURO_E_MINHO TUN
own STATE_BEIRA TUN
own STATE_ESTREMADURA TUN
own STATE_ALENTEJO TUN
```

## 伊特鲁里亚 — XET

```text
own STATE_TUSCANY TUN
own STATE_UMBRIA TUN
own STATE_EMILIA TUN
own STATE_ROMAGNA TUN
```

## 伊利里亚 — XIL

```text
own STATE_ISTRIA TUN
own STATE_DALMATIA TUN
own STATE_CROATIA TUN
own STATE_SLAVONIA TUN
own STATE_SLOVENIA TUN
own STATE_BOSNIA TUN
own STATE_MONTENEGRO TUN
own STATE_ALBANIA TUN
```

## 阿该亚 — XAC

```text
own STATE_ATTICA TUN
own STATE_PELOPONNESE TUN
own STATE_THESSALIA TUN
```

## 马其顿 — XMA

```text
own STATE_MACEDONIA TUN
own STATE_SKOPIA TUN
own STATE_KOSOVO TUN
```

## 色雷斯 — XTH

```text
own STATE_EASTERN_THRACE TUN
own STATE_WESTERN_THRACE TUN
```

## 默西亚 — XMO

```text
own STATE_WESTERN_SERBIA TUN
own STATE_EASTERN_SERBIA TUN
own STATE_BULGARIA TUN
own STATE_NORTHERN_THRACE TUN
own STATE_DOBRUDJA TUN
```

## 达契亚 — XDA

```text
own STATE_WALLACHIA TUN
own STATE_MOLDAVIA TUN
own STATE_NORTHERN_TRANSYLVANIA TUN
own STATE_SOUTHERN_TRANSYLVANIA TUN
own STATE_BUKOVINA TUN
```

## 潘诺尼亚 — XPA

```text
own STATE_CENTRAL_HUNGARY TUN
own STATE_BEKES TUN
own STATE_TRANSDANUBIA TUN
own STATE_DELVIDEK TUN
own STATE_BANAT TUN
own STATE_SLOVAKIA TUN
own STATE_RUTHENIA TUN
```

## 诺里库姆 — XNO

```text
own STATE_AUSTRIA TUN
own STATE_STYRIA TUN
own STATE_TYROL TUN
own STATE_SOUTH_TYROL TUN
```

## 贝尔吉卡 — XBE

```text
own STATE_FLANDERS TUN
own STATE_WALLONIA TUN
own STATE_HOLLAND TUN
own STATE_FRIESLAND TUN
own STATE_GELRE TUN
```

## 日耳曼尼亚 — XGE

```text
own STATE_POMERANIA TUN
own STATE_ELBE TUN
own STATE_WESTPHALIA TUN
own STATE_ANHALT TUN
own STATE_RHINELAND TUN
own STATE_NORTH_RHINE TUN
own STATE_BRANDENBURG TUN
own STATE_SCHLESWIG_HOLSTEIN TUN
own STATE_WURTTEMBERG TUN
own STATE_BADEN TUN
own STATE_HANNOVER TUN
own STATE_BRUNSWICK TUN
own STATE_BAVARIA TUN
own STATE_FRANCONIA TUN
own STATE_SAXONY TUN
own STATE_HESSE TUN
own STATE_MECKLENBURG TUN
own STATE_RUHR TUN
own STATE_LOWER_SILESIA TUN
own STATE_UPPER_SILESIA TUN
own STATE_WEST_PRUSSIA TUN
own STATE_EAST_PRUSSIA TUN
```

## 卢格敦高卢 — XLG

```text
own STATE_ILE_DE_FRANCE TUN
own STATE_NORMANDY TUN
own STATE_PICARDY TUN
own STATE_ALSACE_LORRAINE TUN
own STATE_BRITTANY TUN
own STATE_CHAMPAGNE TUN
own STATE_FRANCHE_COMTE TUN
own STATE_LORRAINE TUN
own STATE_ORLEANS TUN
own STATE_MAINE_ANJOU TUN
own STATE_FRENCH_LOW_COUNTRIES TUN
```

## 主线目标

汉尼拔与复仇目标可计入实际属地控制；汉诺航海记的目标要求迦太基直辖，西撒哈拉还需建成至少一级港口。复仇之路应逐阶段取得土地，罗马终局还要求和平。新迦太基列出的三州是满足三州门槛的示例。

### hannibal / 的黎波里

```text
own STATE_TRIPOLI TUN
own STATE_LIBYA TUN
```

### hannibal / 努米底亚

```text
own STATE_ALGIERS TUN
own STATE_CONSTANTINE TUN
own STATE_ORAN TUN
```

### hannibal / 叙拉古

```text
own STATE_SICILY TUN
```

### hannibal / 地中海诸岛

```text
own STATE_BALEARIC_ISLANDS TUN
own STATE_MALTA TUN
own STATE_CRETE TUN
own STATE_CYPRUS TUN
```

### hannibal / 伊比利亚入口

```text
own STATE_LOWER_ANDALUSIA TUN
```

### hannibal / 新迦太基

```text
own STATE_MURCIA TUN
own STATE_VALENCIA TUN
own STATE_CATALONIA TUN
```

### hannibal / 推罗

```text
own STATE_LEBANON TUN
```

### revenge / 翻过比利牛斯后

```text
own STATE_CATALONIA TUN
own STATE_VALENCIA TUN
own STATE_MURCIA TUN
own STATE_UPPER_ANDALUSIA TUN
own STATE_LOWER_ANDALUSIA TUN
```

### revenge / 越过高卢后

```text
own STATE_LANGUEDOC TUN
own STATE_PROVENCE TUN
own STATE_RHONE TUN
```

### revenge / 翻过阿尔卑斯后

```text
own STATE_WEST_SWITZERLAND TUN
own STATE_EAST_SWITZERLAND TUN
own STATE_SAVOY TUN
own STATE_PIEDMONT TUN
own STATE_LOMBARDY TUN
own STATE_VENETIA TUN
```

### revenge / 复仇开始后

```text
own STATE_LAZIO TUN
```

### hanno / 利克苏斯

```text
own STATE_FEZ TUN
```

### hanno / 刻尔涅商站

```text
own STATE_WEST_SAHARA TUN
```

### hanno / 克雷特斯之河

```text
own STATE_SENEGAL TUN
```

### hanno / 诸神之车

```text
own STATE_SOUTH_CAMEROON TUN
```

## 收回自建属地

先执行 `tag TUN`，然后按需输入：目标必须已经存在。

| 属地 | 吞并指令 |
| --- | --- |
| 的黎波里 | `annex TRP` |
| 努米底亚 | `annex NUM` |
| 伊比利亚 | `annex IBT` |
| 纳尔波高卢 | `annex GLT` |
| 阿尔卑斯／雪山 | `annex SNT` |
| 意大利／罗马 | `annex IOP`, `annex RPR` |
| 毛里塔尼亚 | `annex CPM` |
| 埃及 | `annex CPE` |
| 腓尼基 | `annex CPF` |
| 叙利亚 | `annex CPS` |
| 美索不达米亚 | `annex CPB` |
| 阿拉伯 | `annex CPA` |
| 卢西塔尼亚 | `annex XLU` |
| 伊特鲁里亚 | `annex XET` |
| 伊利里亚 | `annex XIL` |
| 阿该亚 | `annex XAC` |
| 马其顿 | `annex XMA` |
| 色雷斯 | `annex XTH` |
| 默西亚 | `annex XMO` |
| 达契亚 | `annex XDA` |
| 潘诺尼亚 | `annex XPA` |
| 诺里库姆 | `annex XNO` |
| 贝尔吉卡 | `annex XBE` |
| 日耳曼尼亚 | `annex XGE` |
| 卢格敦高卢 | `annex XLG` |

原版常见代码：法兰西 FRA、西班牙 SPA、葡萄牙 POR、奥斯曼 TUR、埃及 EGY、摩洛哥 MOR、阿尔及尔 ALD、的黎波里 TRI、两西西里 SIC、撒丁—皮埃蒙特 SAR、教宗国 PAP、奥地利 AUS、普鲁士 PRU、比利时 BEL、荷兰 NET、瑞士 SWI、英国 GBR、俄国 RUS、美国 USA。原版 TRI 与模组 TRP 是不同国家。

## 依据

[1.15 effects](https://github.com/Victoria-3-Modding-Co-op/Modding-Digests/blob/b4e1e105a8003e4b9c11488b938931d6e89d4985/1.15.0/docs/effects.log) · [Console syntax](https://vic3.paradoxwikis.com/Console_commands)
