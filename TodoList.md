# 耗时统计

各阶段平均耗时（从运行到现在）
阶段 单次耗时范围 平均耗时
preLayers_总耗时 437~514ms ~1000ms 趋于稳定
clearLayer_总耗时 8634~24087ms ~15秒
interrupt_总耗时 254~826ms ~530ms
postLayers_总耗时 10秒~69秒 ~27秒
postLayers 内部分解
步骤 单次范围 平均 说明
WaitStable 183~1083ms ~380ms 稳定
dragon_event 24~113ms ~67ms 很快
MarsReward 0~8849ms ~2800ms 波动大
MarsBody 965~6743ms ~3500ms 波动大
MarsRuinsShop 186~7263ms ~1300ms 波动大
MarsStatue 0~767ms ~200ms 很快
MarsExchangeShop 0~36168ms ~2600ms 偶尔爆高
Check_DefaultTitle 0~46591ms ~5000ms 多次爆高到35-46秒！
最大问题：Check_DefaultTitle 有时跑 35-46 秒
看这些行：

第13行：Check_DefaultTitle cost 35724ms（单次）
第139行：Check_DefaultTitle cost 46591ms（单次）
第208行：MarsExchangeShop cost 36168ms（单次）
这些都是极低概率触发的步骤，但一旦触发就会卡很久。可能是在等动画、网络卡、或者 UI 识别在空转。

结论
主要耗时在 clearLayer：稳定 15 秒/层，这个是战斗本身无法优化
postLayers 波动大：主要是事件触发（Reward/Body/Shop/Title）导致的等待
Check_DefaultTitle 偶尔爆高：需要查这个函数内部在等什么
