from typing import TYPE_CHECKING

from maa.context import Context
from action.fight import fightUtils
from action.fight.fightUtils import timing_decorator

if TYPE_CHECKING:
    from action.fight.mars101 import Mars101


class MarsHPManager:
    """马尔斯101血量管理器：负责血量检查、治疗、安全压血等逻辑"""

    def __init__(self, mars: "Mars101") -> None:
        self.mars: "Mars101" = mars

    def Check_DefaultStatus(self, context: Context):
        """检查冈布奥状态，保持80%以上HP"""
        tempNum = self.mars.layers % 10
        if (
            (11 <= self.mars.layers <= 79) and (tempNum == 1 or tempNum == 5 or tempNum == 9)
        ) or self.mars.layers >= 80:
            if self.mars.layers <= 60 and self.mars.useEarthGate > 0:
                return True
            cast_time = 0
            StatusDetail = fightUtils.checkGumballsStatusV2(context)
            CurrentHP = float(StatusDetail["当前生命值"])
            MaxHp = float(StatusDetail["最大生命值"])
            HPStatus = CurrentHP / MaxHp

            if HPStatus < 0.8:
                if self.mars.layers <= 60:
                    fightUtils.cast_magic_special("生命颂歌", context)
                if self.mars.layers >= 110:
                    fightUtils.cast_magic("气", "静电场", context)
                cast_state = {"痊愈术": True, "神恩术": True, "治疗术": True}
                while HPStatus < 0.8:
                    cast_time += 1
                    if cast_time > 5:
                        break
                    if cast_state["痊愈术"]:
                        if not fightUtils.cast_magic("水", "痊愈术", context):
                            cast_state["痊愈术"] = False
                    elif cast_state["神恩术"]:
                        if not fightUtils.cast_magic("光", "神恩术", context):
                            cast_state["神恩术"] = False
                    elif not fightUtils.cast_magic("水", "治疗术", context):
                        break
                    context.run_task("Fight_ReturnMainWindow")
                    StatusDetail = fightUtils.checkGumballsStatusV2(context)
                    AfterHP = float(StatusDetail["当前生命值"])
                    MaxHp = float(StatusDetail["最大生命值"])
                    HPStatus = AfterHP / MaxHp
            if self.mars.layers >= 51 and not fightUtils.checkBuffStatus("神圣重生", context):
                fightUtils.cast_magic("光", "神圣重生", context)
        return True

    def Get_CurrentHPStatus(self, context: Context):
        """获取当前HP百分比"""
        StatusDetail = fightUtils.checkGumballsStatusV2(context)
        CurrentHP = float(StatusDetail["当前生命值"])
        MaxHp = float(StatusDetail["最大生命值"])
        return CurrentHP / MaxHp

    @timing_decorator
    def Control_TenpecentHP(self, context: Context):
        """安全压血主逻辑，尽可能压低目标血量同时确保目标不会死亡"""
        SAFETY_MARGIN = 0.08
        MAX_ATTEMPTS = 20
        TEST_ROUNDS = 3
        MIN_CHANGE_THRESHOLD = 0.01
        CONSECUTIVE_STALL_LIMIT = 3
        BLESSING_DAMAGE_MULTIPLIER = 9
        DAMAGE_HISTORY_SIZE = 3

        current_hp = self.Get_CurrentHPStatus(context)

        _, max_stoneskin_damage = self.Test_Stoneskin_Damage(context, TEST_ROUNDS)
        if max_stoneskin_damage is None:
            return 10000000

        blessing_damage = max_stoneskin_damage * BLESSING_DAMAGE_MULTIPLIER
        current_hp = self.Get_CurrentHPStatus(context)
        stoneskin_damage_history = []
        blessing_damage_history = []
        attempts = 0
        consecutive_no_change = 0

        while attempts < MAX_ATTEMPTS:
            safe_hp_to_reduce = current_hp - SAFETY_MARGIN

            if blessing_damage <= safe_hp_to_reduce and current_hp > 0.1:
                prev_hp = current_hp
                fightUtils.cast_magic("光", "祝福术", context)
                context.run_task("Fight_ReturnMainWindow")
                current_hp = self.Get_CurrentHPStatus(context)

                actual_damage = prev_hp - current_hp
                if actual_damage > 0:
                    blessing_damage_history.append(actual_damage)
                    if len(blessing_damage_history) > DAMAGE_HISTORY_SIZE:
                        blessing_damage_history.pop(0)
                    new_max_blessing = max(blessing_damage_history)
                    if new_max_blessing > blessing_damage:
                        blessing_damage = new_max_blessing
                    elif new_max_blessing < blessing_damage * 0.8:
                        blessing_damage = new_max_blessing

            elif max_stoneskin_damage <= safe_hp_to_reduce and current_hp > 0.1:
                prev_hp = current_hp
                fightUtils.cast_magic("土", "石肤术", context)
                context.run_task("Fight_ReturnMainWindow")
                current_hp = self.Get_CurrentHPStatus(context)

                if current_hp <= 0:
                    return -1

                actual_damage = prev_hp - current_hp
                if actual_damage > 0:
                    stoneskin_damage_history.append(actual_damage)
                    if len(stoneskin_damage_history) > DAMAGE_HISTORY_SIZE:
                        stoneskin_damage_history.pop(0)
                    new_max_stoneskin = max(stoneskin_damage_history)
                    if new_max_stoneskin > max_stoneskin_damage:
                        max_stoneskin_damage = new_max_stoneskin
            else:
                return current_hp

            hp_change = prev_hp - current_hp
            attempts += 1

            if hp_change > 0:
                consecutive_no_change = 0
            else:
                consecutive_no_change += 1
                if consecutive_no_change >= CONSECUTIVE_STALL_LIMIT:
                    return current_hp

        return current_hp

    def Test_Stoneskin_Damage(self, context: Context, test_rounds: int):
        """测试石肤术伤害"""
        effective_casts = 0
        damage_values = []

        for _ in range(test_rounds):
            prev_hp = self.Get_CurrentHPStatus(context)
            fightUtils.cast_magic("土", "石肤术", context)
            context.run_task("Fight_ReturnMainWindow")
            current_hp = self.Get_CurrentHPStatus(context)

            if current_hp <= 0:
                return None, None

            if prev_hp > current_hp:
                damage_values.append(prev_hp - current_hp)
                effective_casts += 1

        if effective_casts == 0:
            return None, None

        avg_damage = sum(damage_values) / effective_casts
        max_damage = max(damage_values)

        return avg_damage, max_damage
