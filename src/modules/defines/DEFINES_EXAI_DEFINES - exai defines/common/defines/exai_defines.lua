---1.关于训练部署类的
NDefines.NAI.DEPLOY_MIN_TRAINING_SURRENDER_FACTOR = 1 -- 当投降进度高于0时，AI在战时部署部队所需的训练百分比（1.0 = 100%）。
NDefines.NAI.DEPLOY_MIN_EQUIPMENT_SURRENDER_FACTOR = 1 -- 当投降进度高于0时，AI在战时部署部队所需的装备百分比（1.0 = 100%）。
NDefines.NAI.DEPLOY_MIN_TRAINING_PEACE_FACTOR = 1 -- AI在和平时期部署部队所需的训练百分比（1.0 = 100%）。
NDefines.NAI.DEPLOY_MIN_EQUIPMENT_PEACE_FACTOR = 1 -- AI在和平时期部署部队所需的装备百分比（1.0 = 100%）。
NDefines.NAI.DEPLOY_MIN_TRAINING_WAR_FACTOR = 1 -- AI在战时部署部队所需的训练百分比（1.0 = 100%）。
NDefines.NAI.DEPLOY_MIN_EQUIPMENT_WAR_FACTOR = 1 -- AI战时部署部队所需的装备百分比（1.0 = 100%）。
NDefines.NAI.DEPLOY_MIN_EQUIPMENT_CAP_DEPLOY_FACTOR = 1 -- 装备不足训练被卡住，但是我们的装备量高于这个85%数值，则无论如何都要部署部队

-- NDefines.NAI.AI_CHAIN_CALLS_ALLIES = true      ---------这条代码意思是AI会在战争中自动呼叫其它AI加入战争 -- PIHC 外交机制特殊
---以下是将领中执行计划低风险，中风险，激进计划（划线平推）的时候的一些修正
NDefines.NAI.PLAN_ATTACK_MIN_ORG_FACTOR_LOW = 0.9		-- 当你要执行低风险计划的时候，那么在你划线平推的时候系统会选什么部队执行计划呢？对了是组织度至少是85%的部队
NDefines.NAI.PLAN_ATTACK_MIN_STRENGTH_FACTOR_LOW = 0.9	-- 当你要执行低风险计划的时候，那么会选什么部队执行计划呢？对了是黄条至少是60%的部队
NDefines.NAI.PLAN_ATTACK_MIN_ORG_FACTOR_MED = 0.85		-- 中风险计划
NDefines.NAI.PLAN_ATTACK_MIN_STRENGTH_FACTOR_MED = 0.85  ----中
NDefines.NAI.PLAN_ATTACK_MIN_ORG_FACTOR_HIGH = 0.8    ----高
NDefines.NAI.PLAN_ATTACK_MIN_STRENGTH_FACTOR_HIGH = 0.8    ----高




----ai指派单位情况（有些还看不太懂
NDefines.NAI.ASSIGN_TANKS_TO_MOUNTAINS = 0            ---派坦克到山地的系数
NDefines.NAI.ASSIGN_TANKS_TO_JUNGLE = 0          ------派坦克到丛林的系数
NDefines.NAI.ASSIGN_TANKS_TO_WAR_FRONT = 100                          -- 坦克分配到交战战线的系数  建议改成9999999
NDefines.NAI.ASSIGN_TANKS_TO_NON_WAR_FRONT = -10                    -- 坦克分配到非交战区的系数 建议改成-999
NDefines.NAI.REASSIGN_TO_ANOTHER_FRONT_FACTOR = 1                   -- 重新分配单位到前线的系数，0-1表示不愿意 大于1表示愿意
NDefines.NAI.REASSIGN_TO_ANOTHER_FRONT_IF_IN_COMBAT_FACTOR = 2      -- 重新分配到交战前线的系数，跟上面那条一样的 建议改成9999
NDefines.NAI.MANPOWER_RATIO_CAREFULNESS_THRESHOLD = 0.025         -----如果人力池/已经用人力 低于0.05那么AI会极其谨慎进攻


NDefines.NAI.ARMY_LEADER_ASSIGN_KEEP_CURRENT_LEADER_FACTOR = 10000                    -- AI保持这个将领的修正分数，改成99999那么AI不会轻易换将领，因为AI换将的修正因子真的太多了不如直接9999999防止换将，然后给AI上一个将领受伤-99999患病-999999
NDefines.NAI.ARMY_LEADER_ASSIGN_DONT_STEAL_OTHER_FACTOR = 0.1
NDefines.NMilitary.UNIT_LEADER_MODIFIER_COOLDOWN_ON_GROUP_CHANGE = 0


NDefines.NAI.AREA_DEFENSE_SETTING_VP = false       ------ai是否默认（是默认情况）防守胜利点
NDefines.NAI.AREA_DEFENSE_SETTING_PORTS = true          -------港口
NDefines.NAI.AREA_DEFENSE_SETTING_AIRBASES = false      ----------空军基地
NDefines.NAI.AREA_DEFENSE_SETTING_FORTS = true         ----要塞
NDefines.NAI.AREA_DEFENSE_SETTING_COASTLINES = true	 --------海岸线
NDefines.NAI.AREA_DEFENSE_SETTING_RAILWAYS = false         -------铁路

NDefines.NAI.DIVISION_SUPPLY_RATIO_TO_MOTORIZE = 0.80       ------如果补给转化比例低于这个数，那么AI会把临近的补给中心摩托化

NDefines.NAI.ATTACK_HEAVILY_DEFENDED_LIMIT = 0.7				--------AI进攻高防御地方的修正限制，这个0.5意思是ai至少有50%优势才会去创防线
NDefines.NAI.HOUR_BAD_COMBAT_REEVALUATE = 48        -----------如果ai在一场战斗中持续了48小时，那么AI会尝试跳过这场战斗（可能会站着不动

--海军AI修正
NDefines.NAI.ENEMY_NAVY_STRENGTH_DONT_BOTHER = 10  --敌方海军能力强于我方1.5倍则禁止登陆 5
NDefines.NAI.SHIPS_PRODUCTION_BASE_COST = 20000  --AI标准化海军造价，原1万，此值防止AI抽风捏低造价垃圾船
NDefines.NAI.NAVY_PREFERED_MAX_SIZE = 108  --AI尝试将舰队规模合并到这个规模，原25，但此值是一个软指标，AI可能不会强制执行
NDefines.NAI.DOCKYARDS_PER_NAVAL_DESIRE_EFFECT = 10  --AI对舰船的关注程度，原-10
NDefines.NAI.PRODUCTION_MAX_PROGRESS_TO_SWITCH_NAVAL = 0.1   --如果进度高于此数值，AI不会删除产线已经在建造的船 原0.1
NDefines.NAI.PRODUCTION_WAIT_TO_FINISH_IF_EXPENSIVE = 0.1 --如果生产的船造价较高，AI不会删除此进度的船

NDefines.NAI.CARRIER_TASKFORCE_MAX_CARRIER_COUNT = 4 --AI舰队设定的最佳航母数量
NDefines.NAI.CAPITAL_TASKFORCE_MAX_CAPITAL_COUNT = 12  --AI舰队设定的最佳主力舰数量 原12
NDefines.NAI.SCREEN_TASKFORCE_MAX_SHIP_COUNT = 120 --AI舰队设定的最佳屏位舰数量 原12
NDefines.NAI.SUB_TASKFORCE_MAX_SHIP_COUNT = 50  --AI舰队设定的最佳潜艇数量 原16
NDefines.NAI.SCREENS_TO_CAPITAL_RATIO = 10 --AI舰队屏位舰比上主力舰的比例原4

NDefines.NAI.REPAIR_TASKFORCE_SIZE = 50  --AI修船最大船坞数量  原4 （TM的怪不得AI分配修船数量那么少，老是修不起船）






--其余杂项
NDefines.NAI.NAVAL_DOCKYARDS_SHIP_FACTOR = 5	   -- 逼着AI造船  原1.5
NDefines.NAI.START_TRAINING_EQUIPMENT_LEVEL = 0.6               --凑齐60%装备开始训练 原0.4
NDefines.NAI.PRODUCTION_EQUIPMENT_SURPLUS_FACTOR = 0.5    -- 装备基础溢出比例，多了删产线原0.8
NDefines.NMilitary.PLAN_MIN_AUTOMATED_EMPTY_POCKET_SIZE = 4       -- 四个格子开始做饺子 原2
NDefines.NMilitary.PLAN_SPREAD_ATTACK_WEIGHT = 5	      -- 集中突击  原12 数值越高就不越不会多次强袭
NDefines.NMilitary.PLAN_PROVINCE_LOW_VP_IMPORTANCE_FRONT = 1    -- 低胜利点重要性 原2
NDefines.NMilitary.PLAN_PROVINCE_MEDIUM_VP_IMPORTANCE_FRONT = 2  --中胜利点重要性 原2.25
NDefines.NMilitary.PLAN_PROVINCE_HIGH_VP_IMPORTANCE_FRONT = 3    -- 高胜利点重要性 原2.75
NDefines.NAI.FAILED_INVASION_AVOID_DURATION = 1               -- 如果同一块地入侵失败那么AI会等60天后再入侵这块地 原60
NDefines.NAI.CANCEL_COMBAT_DISADVANTAGE_RATIO = 1.3            -- 如果敌方在（正常）战斗中对我方的优势比大于 <值>，则允许取消攻击 原1.5
NDefines.NAI.CANCEL_COMBAT_MIN_DURATION_HOURS = 24            -- 只有在至少 <value> 小时后才允许取消（正常）战斗 原48
NDefines.NAI.CANCEL_INVASION_COMBAT_DISADVANTAGE_RATIO = 2.5    -- 如果入侵战斗中敌方对我方的优势比大于 <value>，则允许取消攻击 原3.5
NDefines.NSupply.AI_THEATRE_SUPPLY_CRISIS_LIMIT = 0.5  --如果AI在一个地区补给数值低于0.5会试图逃跑
NDefines.NAI.REFIT_SHIP_PERCENTAGE_OF_FORCES = 0 -- AI改装船的百分比，原0.1

--AI部署师修正
NDefines.NAI.WANTED_UNITS_INDUSTRY_FACTOR = 10                       -- ai想部署多少兵取决于ai有多少工厂原1.6
-- NDefines.NAI.WANTED_UNITS_THREAT_BASE = 1                             -- 根据世界紧张度的动态修正原0.7 -- PIHC 紧张度机制特殊
-- NDefines.NAI.WANTED_UNITS_THREAT_MAX = 10                             -- 根据世界紧张度的动态修正（1~10）原6.0 -- PIHC 紧张度机制特殊
NDefines.NAI.WANTED_UNITS_WAR_THREAT_FACTOR = 1.5                     -- 如果我们的头上有红色的东西（造宣战）原1.15
NDefines.NAI.WANTED_UNITS_DANGEROUS_NEIGHBOR_FACTOR = 2               -- 如果我们有个危险的邻居（造成紧张度高的国家）原1.15
-- NDefines.NAI.WANTED_UNITS_MANPOWER_DIVISOR = 10000                    -- 如果我们有多少人力我们需要一个师
NDefines.NAI.WANTED_UNITS_MANPOWER_DIVISOR = 1000                    -- 如果我们有多少人力我们需要一个师 -- PIHC 人力（马力）机制特殊
NDefines.NAI.WANTED_UNITS_MAX_WANTED_CAP = 2000                     --最大能部署多少部队  原500
NDefines.NMilitary.DEPLOY_TRAINING_MAX_LEVEL = 2                     --银牌训练部署 原1
NDefines.NProduction.MIN_FIELD_TO_TRAINING_MANPOWER_RATIO = 2      ----------可以训练部队占总部队的人数  原0.75

-- NDefines.NMilitary.COMBAT_MINIMUM_TIME = 6  ----最低交战时间 --从4 延长到6小时 -- PIHC: ???










NDefines.NAI.LAND_DEFENSE_CIVIL_FACTORY_IMPORTANCE = 800 -- 50			-- Strategic importance of civil factories
NDefines.NAI.LAND_DEFENSE_MILITARY_FACTORY_IMPORTANCE = 880 -- 70		-- Strategic importance of military factories
NDefines.NAI.LAND_DEFENSE_NAVAL_FACTORY_IMPORTANCE = 420 -- 30			-- Strategic importance of naval factories




NDefines.NAI.NAVAL_PATROL_PLANES_PER_SHIP_RAIDING = 40 --10.0		-- Amount of naval patrol planes per ship on a convoy raid mission


NDefines.NAI.MIN_NAVAL_MISSION_PRIO_TO_ASSIGN = {  -- priorities for regions to get assigned to a mission
	0, -- HOLD (consumes fuel HOLD_MISSION_MOVEMENT_COST fuel while moving)
	200, -- PATROL
	200, -- STRIKE FORCE
	200, -- CONVOY RAIDING
	100, -- CONVOY ESCORT
	200, -- MINES PLANTING
	100, -- MINES SWEEPING
	0, -- TRAIN
	0, -- RESERVE_FLEET
	100, -- NAVAL INVASION SUPPORT
}

NDefines.NAI.HIGH_PRIO_NAVAL_MISSION_SCORES = {  -- priorities for regions to get assigned to a mission
	0, -- HOLD (consumes fuel HOLD_MISSION_MOVEMENT_COST fuel while moving)
	1000000, -- PATROL
	1000, -- STRIKE FORCE
	1500, -- CONVOY RAIDING
	1000, -- CONVOY ESCORT
	10, -- MINES PLANTING
	300, -- MINES SWEEPING
	0, -- TRAIN
	0, -- RESERVE_FLEET
	1000, -- NAVAL INVASION SUPPORT
}

NDefines.NAI.MAX_MISSION_PER_TASKFORCE = {  -- max mission region/taskforce ratio
	0, -- HOLD (consumes fuel HOLD_MISSION_MOVEMENT_COST fuel while moving)
	1.5, -- PATROL
	6, -- STRIKE FORCE
	1.5, -- CONVOY RAIDING
	4, -- CONVOY ESCORT
	2, -- MINES PLANTING
	2, -- MINES SWEEPING
	0, -- TRAIN
	0, -- RESERVE_FLEET
	10, -- NAVAL INVASION SUPPORT
}

NDefines.NAI.AREA_DEFENSE_CAPITAL_PEACE_VP_WEIGHT = { 1.0, 1.0, 1.0 }
NDefines.NAI.AREA_DEFENSE_CAPITAL_VP_WEIGHT = { 0.0, 1.0, 2.0 }
NDefines.NAI.AREA_DEFENSE_HOME_VP_WEIGHT = { 0.0, 0.5, 1.0 }
NDefines.NAI.AREA_DEFENSE_OTHER_VP_WEIGHT = { 0.0, 0.0, 1.0 }

NDefines.NAI.AREA_DEFENSE_CAPITAL_PEACE_COAST_WEIGHT = { 0.0, 0.0, 0.0 }
NDefines.NAI.AREA_DEFENSE_CAPITAL_COAST_WEIGHT = { 0.0, 0.2, 0.7 }
NDefines.NAI.AREA_DEFENSE_HOME_COAST_WEIGHT = { 0.0, 0.1, 0.5 }
NDefines.NAI.AREA_DEFENSE_OTHER_COAST_WEIGHT = { 0.0, 0.0, 0.0 }

NDefines.NAI.AREA_DEFENSE_CAPITAL_PEACE_BASE_WEIGHT = { 0.0, 0.0, 0.0 }
NDefines.NAI.AREA_DEFENSE_CAPITAL_BASE_WEIGHT = { 0.5, 1.0, 1.5 }
NDefines.NAI.AREA_DEFENSE_HOME_BASE_WEIGHT = { 0.5, 1.0, 1.0 }
NDefines.NAI.AREA_DEFENSE_OTHER_BASE_WEIGHT = { 0.5, 0.5, 1.0 }
