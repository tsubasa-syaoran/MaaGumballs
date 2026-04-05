# Mars101 重构记录

## 概述

将约 1700 行的 `Mars101` 单一巨型类拆分为 7 个内聚的独立模块，主类只保留流程编排和状态聚合。

## 最终文件结构

```
agent/action/mars/
├── mars_hp.py           (~180行) MarsHPManager — 血量检查、治疗、安全压血
├── mars_boss.py          (~130行) MarsBossHandler — Boss层战斗逻辑
├── mars_title.py         (~90行)  MarsTitleManager — 按层数自动学习称号
├── mars_special_layer.py (~100行) MarsSpecialLayerManager — 进入/离开休息室
├── mars_earth_gate.py    (~35行)  MarsEarthGateManager — 大地之门施放与等待
├── mars_events.py        (~220行) MarsEventDispatcher — 6个Mars事件分发
├── mars_settlement.py    (~190行) MarsSettlementManager — 出图前结算流程
└── REFACTORING.md        本文档
```

## 设计原则

- 每个 Manager 持有 `Mars101` 引用（`self.mars`）访问状态
- `mars101.py` 中原方法保留，改为委托给对应 Manager
- 所有 `timing_decorator` 装饰器保留，统计时间不变
- 逐步拆分，每步验证后进行下一步

---

## Step 1: mars_hp.py 提取完成 ✅

**日期**: 2026-04-05

**提取内容**: `Check_DefaultStatus`, `Get_CurrentHPStatus`, `Control_TenpecentHP`, `Test_Stoneskin_Damage`

**新增文件**: `agent/action/mars/mars_hp.py`

**修改文件**: `agent/action/fight/mars101.py`

**改动说明**:
- 新增 `MarsHPManager` 类，持有 Mars101 引用（`self.mars`）访问状态
- `mars101.py` 中原方法保留，改为委托给 `MarsHPManager`
- 业务逻辑完全不变，行为一致

**验证通过**:
- 所有 `self.layers` 引用在 `mars_hp.py` 中正确映射到 `self.mars.layers`
- `Get_CurrentHPStatus` 内部调用链: MarsHPManager → `self.mars.Get_CurrentHPStatus` → MarsHPManager（委托链正确）
- `Control_TenpecentHP` 内部调用 `Test_Stoneskin_Damage` 同类方法，链不变
- `timing_decorator` 装饰器保留，统计时间不变

---

## Step 2: mars_boss.py 提取完成 ✅

**日期**: 2026-04-05

**提取内容**: `handle_boss_event`

**新增文件**: `agent/action/mars/mars_boss.py`

**修改文件**: `agent/action/fight/mars101.py`

**改动说明**:
- 新增 `MarsBossHandler` 类，持有 Mars101 引用访问状态
- Boss坐标常量（`boss_x/y`, `boss_slave_1_x/y`, `boss_slave_2_x/y`）移入 `mars_boss.py`
- `mars101.py` 中原方法保留，改为委托给 `MarsBossHandler`
- `timing_decorator` 装饰器保留
- 业务逻辑完全不变，行为一致

**验证通过**:
- 所有 `self.layers` 和 `self.target_magicgumball_para` 引用在 `mars_boss.py` 中正确映射到 `self.mars.*`
- `handle_clearCurLayer_event` 调用 `self.handle_boss_event()` 不变，委托链正确
- boss 坐标常量已从 `mars101.py` 中移除

---

## Step 3: mars_title.py 提取完成 ✅

**日期**: 2026-04-05

**提取内容**: `Check_DefaultTitle`

**新增文件**: `agent/action/mars/mars_title.py`

**修改文件**: `agent/action/fight/mars101.py`

**改动说明**:
- 新增 `MarsTitleManager` 类，称号状态标志（`isTitle_L1/L10/L61/L86`, `isGetDragonTitle`）移入此类
- `__init__` 中移除已迁移的称号状态标志
- `mars101.py` 中原方法保留，改为委托给 `MarsTitleManager`
- `timing_decorator` 装饰器保留，统计名称不变
- 业务逻辑完全不变，行为一致

**验证通过**:
- 所有 `self.layers`, `self.astrological_title_para`, `self.is_demontitle_enable` 正确映射到 `self.mars.*`
- `isGetDragonTitle` 已从 `Mars101.__init__` 移除，实际值由 `MarsTitleManager` 管理
- 调用点 `handle_postLayers_event` 中 `self.Check_DefaultTitle(context)` 不变，委托链正确

---

## Step 4: mars_special_layer.py 提取完成 ✅

**日期**: 2026-04-05

**提取内容**: `gotoSpecialLayer`, `leaveSpecialLayer`, `handle_SpecialLayer_event`

**新增文件**: `agent/action/mars/mars_special_layer.py`

**修改文件**: `agent/action/fight/mars101.py`

**改动说明**:
- 新增 `MarsSpecialLayerManager` 类
- 特殊层怪物坐标（`special_layer_monster_1_x/y`, `special_layer_monster_2_x/y`）移入 `mars_special_layer.py`
- `mars101.py` 中原方法保留，改为委托给 `MarsSpecialLayerManager`
- `timing_decorator` 装饰器保留
- 业务逻辑完全不变，行为一致

**验证通过**:
- `special_layer_monster` 坐标已无引用，已从 `mars101.py` 中移除
- 所有调用点（`handle_before_leave_maze_event`, `handle_SpecialLayer_event` 内部）通过 `self.*` 调用不变，委托链正确

---

## Step 5: mars_earth_gate.py 提取完成 ✅

**日期**: 2026-04-05

**提取内容**: `handle_EarthGate_event`

**新增文件**: `agent/action/mars/mars_earth_gate.py`

**修改文件**: `agent/action/fight/mars101.py`

**改动说明**:
- 新增 `MarsEarthGateManager` 类
- `mars101.py` 中原方法保留，改为委托给 `MarsEarthGateManager`
- 业务逻辑完全不变，行为一致

**验证通过**:
- `self.layers`, `self.useEarthGate`, `self.target_earthgate_para`, `self.isUseMagicAssist` 正确映射到 `self.mars.*`
- `self.mars.Check_CurrentLayers(context)` 调用链正确
- 调用点 `handle_postLayers_event` 中 `self.handle_EarthGate_event(context)` 不变

---

## Step 6: mars_events.py 提取完成 ✅

**日期**: 2026-04-05

**提取内容**: `handle_MarsReward_event`, `handle_MarsBody_event`, `handle_MarsRuinsShop_event`, `handle_MarsStatue_event`, `handle_MarsExchangeShop_event`, `handle_MarsStele_event`

**新增文件**: `agent/action/mars/mars_events.py`

**修改文件**: `agent/action/fight/mars101.py`

**改动说明**:
- 新增 `MarsEventDispatcher` 类，统一管理6个Mars事件
- `mars101.py` 中原6个方法全部改为委托给 `MarsEventDispatcher`
- `timing_decorator` 装饰器保留
- `handle_MarsReward_event` 内部调用 `self.mars.handle_MarsStele_event` 和 `self.mars.Check_GridAndMonster`，委托链正确
- 业务逻辑完全不变，行为一致

**验证通过**:
- 所有 `self.layers`, `self.isGetTitanFoot`, `self.isGetMagicAssist` 等引用正确映射到 `self.mars.*`
- 调用点 `handle_postLayers_event` 中各事件处理方法调用链不变

---

## Step 7: mars_settlement.py 提取完成 ✅

**日期**: 2026-04-05

**提取内容**: `handle_before_leave_maze_event`

**新增文件**: `agent/action/mars/mars_settlement.py`

**修改文件**: `agent/action/fight/mars101.py`

**改动说明**:
- 新增 `MarsSettlementManager` 类
- `mars101.py` 中原方法改为委托给 `MarsSettlementManager`
- 所有内联注释代码（压血相关）一并移入，逻辑不变
- 业务逻辑完全不变，行为一致

**验证通过**:
- 所有 `self.layers`, `self.useEarthGate`, `self.isUseMagicAssist`, `self.director_para`, `self.manual_leave_para`, `self.isLeaveMaze` 正确映射到 `self.mars.*`
- `gotoSpecialLayer`/`leaveSpecialLayer` 通过 `self.mars.gotoSpecialLayer`/`leaveSpecialLayer` 调用，委托链正确
- 调用点 `handle_postLayers_event` 中 `self.handle_before_leave_maze_event(context)` 不变

---

## 遗留事项

- `mars101.py` 仍有部分方法待最终精简（`Check_CurrentLayers`, `Check_GridAndMonster`, `Check_DefaultEquipment`, `handle_preLayers_event`, `handle_postLayers_event` 等流程编排方法）
- `Mars_Fight_ClearCurrentLayer` 类仍保留在 `mars101.py` 底部（可独立为一个文件）
