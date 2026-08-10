NDefines.NFrontend.CAMERA_MIN_HEIGHT = 40.0;						-- Minimum camera height
NDefines.NFrontend.CAMERA_MAX_HEIGHT = 4000.0;						-- Maximum camera height
NDefines.NGraphics.CAMERA_ZOOM_SPEED = 35;
NDefines.NGraphics.DRAW_MAP_OBJECTS_CUTOFF = 1200.0;				-- Remove map objects at this distance

NDefines.NMapIcons.STRATEGIC_AIR_PRIORITY_AIR_MISSION = 290;

NDefines.NMapMode.CONSTRUCTION_MAP_MODE_BUILDING_DEFAULT_COLOR = { 0.43, 0.22, 0.22, 0.25 }; 			-- Color of states/provinces that can't be built on
NDefines.NMapMode.CONSTRUCTION_MAP_MODE_BUILDING_MAX_LEVEL_COLOR = { 0.05, 0.1, 0.7, 0.4 }; 			-- Color of states/provinces where current building level is maxed out (max is current max level, not final max level) of a building type
NDefines.NMapMode.CONSTRUCTION_MAP_MODE_BUILDING_LEVEL_LOW_COLOR = { 0.05, 0.22, 0.0, 0.4 };
NDefines.NMapMode.CONSTRUCTION_MAP_MODE_BUILDING_LEVEL_HI_COLOR = { 0.4, 0.9, 0.0, 0.5 };

NDefines.NGraphics.BORDER_COLOR_SELECTION_STATE_R = 0.35;
NDefines.NGraphics.BORDER_COLOR_SELECTION_STATE_G = 0.75;
NDefines.NGraphics.BORDER_COLOR_SELECTION_STATE_B = 0.75;
NDefines.NGraphics.BORDER_COLOR_SELECTION_PROVINCE_R = 0.15;
NDefines.NGraphics.BORDER_COLOR_SELECTION_PROVINCE_G = 0.9;
NDefines.NGraphics.BORDER_COLOR_SELECTION_PROVINCE_B = 0.9;
NDefines.NGraphics.COUNTRY_FLAG_TEX_MAX_SIZE = 2048; -- Tweak dependly on amount of countries. Must be power of 2. No more then 2048.
NDefines.NGraphics.COUNTRY_FLAG_STRIPE_TEX_MAX_WIDTH = 10;
NDefines.NGraphics.COUNTRY_FLAG_STRIPE_TEX_MAX_HEIGHT = 8196;
NDefines.NGraphics.COUNTRY_FLAG_LARGE_STRIPE_MAX_WIDTH = 42;
NDefines.NGraphics.COUNTRY_FLAG_LARGE_STRIPE_MAX_HEIGHT = 24000; --this
NDefines.NGraphics.VICTORY_POINT_MAP_ICON_AFTER = {0, 10, 20}; -- After this amount of VP the map icon becomes bigger dot.
NDefines.NGraphics.VICTORY_POINT_MAP_ICON_CAPITAL_CUTOFF_MAX = 1500.0;	--Capitals are special snowflakes, they need their own number
NDefines.NGraphics.VICTORY_POINT_MAP_ICON_TEXT_CUTOFF = {300, 500, 1500}; -- At what camera distance the VP name text disappears, was 150, 250, 500
NDefines.NGraphics.VICTORY_POINT_MAP_ICON_TEXT_CUTOFF_MIN = 100.0; -- Min range for victory point text
NDefines.NGraphics.VICTORY_POINT_MAP_ICON_TEXT_CUTOFF_MAX = 1600.0; -- Max range for victory point text, was 800
NDefines.NGraphics.TRADE_ROUTE_RESOURCE_EXPORT_COLOR = { 0.5, 0.5, 1.0, 0.75 };
NDefines.NGraphics.TRADE_ROUTE_RESOURCE_IMPORT_COLOR = { 0.5, 0.5, 1.0, 0.75 };
NDefines.NGraphics.SUPPLY_UNIT_COUNTER_SHOW_THRESHOLD = 0.75;  -- At what supply threshold will the normal crate be shown on unit counters
NDefines.NGraphics.SUPPLY_UNIT_COUNTER_LOW_THRESHOLD = 0.50;  -- At what supply threshold will the orange crate be shown on unit counters
NDefines.NGraphics.SUPPLY_UNIT_COUNTER_VERY_LOW_THRESHOLD = 0.25;  -- At what supply threshold will the red crate with ! will be shown on unit counters

NDefines.NInterface.DRAG_AND_DROP_SCROLLING_SENSITIVITY = 30;	-- Speed multiplier for components scrolling while drag'n dropping elements
NDefines.NInterface.SLOW_INTERFACE_THRESHOLD = 50000; -- Show warning "SLOW INTERFACE" in debug when interface refresh takes more that this (in microseconds)

NDefines.NGraphics.RESISTANCE_COLOR_NONE = {0.4, 0.4, 0.6, 0.5}; --rgba
NDefines.NGraphics.RESISTANCE_COLOR_GOOD = {0.0, 0.65, 0, 1}; --rgba
NDefines.NGraphics.RESISTANCE_COLOR_AVERAGE = {0.65, 0.65, 0, 1};
NDefines.NGraphics.RESISTANCE_COLOR_BAD = {0.65, 0, 0, 1};
NDefines.NGraphics.CONSTRUCTION_CONVERSION_COLOR = { 0.9, 0.9, 0.3, 0.1};
NDefines.NGraphics.CONSTRUCTION_CONVERSION_IN_PROGRESS_COLOR = { 0.3, 0.3, 0.9, 0.1};
NDefines.NGraphics.VIRTUAL_BATTLEPLANS_COLOR = { 0.2, 1.0, 0.2, 1 };
NDefines.NGraphics.ALLIED_BATTLEPLANS_COLOR = { 0.3, 0.4, 1.0, 1 };
NDefines.NGraphics.OFFENSIVE_PING_CIRCLE_COLOR = { 0.64, 0.48, 0.35 };
NDefines.NGraphics.DEFENSIVE_PING_CIRCLE_COLOR = { 0.4, 0.55, 0.66 };
NDefines.NGraphics.GMT_OFFSET = 2793; --X position on map, of Greenwitch GMT+0 (see also in shader daynight.fxh)
NDefines.NGraphics.DAY_NIGHT_FEATHER = 0.024; --Feather value between complete darkness and the day (see also in shader daynight.fxh)
NDefines.NGraphics.SOUTH_POLE_OFFSET = 0.17; --Our map is missing big parts of globe on north and south (see also in shader daynight.fxh)
NDefines.NGraphics.NORTH_POLE_OFFSET = 0.93;
NDefines.NGraphics.COUNTRY_FLAG_TEX_WIDTH = 82; --Expected texture size
NDefines.NGraphics.COUNTRY_FLAG_TEX_HEIGHT = 52;
NDefines.NGraphics.COUNTRY_FLAG_TEX_MAX_SIZE = 2048; --Tweak dependly on amount of countries. Must be power of 2. No more then 2048.
NDefines.NGraphics.COUNTRY_FLAG_MEDIUM_TEX_WIDTH = 41;
NDefines.NGraphics.COUNTRY_FLAG_MEDIUM_TEX_HEIGHT = 26;
NDefines.NGraphics.COUNTRY_FLAG_MEDIUM_TEX_MAX_SIZE = 1024; --Tweak dependly on amount of countries. Must be power of 2. No more then 2048.
NDefines.NGraphics.COUNTRY_FLAG_SMALL_TEX_WIDTH = 10;
NDefines.NGraphics.COUNTRY_FLAG_SMALL_TEX_HEIGHT = 7;
NDefines.NGraphics.COUNTRY_FLAG_SMALL_TEX_MAX_SIZE = 256; --Tweak dependly on amount of countries. Must be power of 2. No more then 2048.
NDefines.NGraphics.COUNTRY_FLAG_STRIPE_TEX_MAX_WIDTH = 10;
NDefines.NGraphics.COUNTRY_FLAG_STRIPE_TEX_MAX_HEIGHT = 8196;
NDefines.NGraphics.COUNTRY_FLAG_LARGE_STRIPE_MAX_WIDTH = 42;
NDefines.NGraphics.COUNTRY_FLAG_LARGE_STRIPE_MAX_HEIGHT = 24000; --this was changed to 16384 in vanilla
NDefines.NGraphics.VICTORY_POINT_LEVELS = 3;
NDefines.NGraphics.VICTORY_POINT_MAP_ICON_AFTER = {0, 10, 20}; --After this amount of VP the map icon becomes bigger dot.
NDefines.NGraphics.VICTORY_POINT_MAP_ICON_CAPITAL_CUTOFF_MAX = 1500.0;	--Capitals are special snowflakes, they need their own number
NDefines.NGraphics.VICTORY_POINT_MAP_ICON_TEXT_CUTOFF = {1000, 1000, 1000};  -- At what camera distance the VP name text disappears, was 150, 250, 500
NDefines.NGraphics.VICTORY_POINT_MAP_ICON_TEXT_CUTOFF_MIN = 100.0; --Min range for victory point text
NDefines.NGraphics.VICTORY_POINT_MAP_ICON_TEXT_CUTOFF_MAX = 1000.0; --Max range for victory point text, was 800
NDefines.NGraphics.VICTORY_POINT_MAP_ICON_DOT_CUTOFF_MIN = 100.0; --Min range for victory point dot
NDefines.NGraphics.VICTORY_POINT_MAP_ICON_DOT_CUTOFF_MAX = 1000.0; --Max range for victory point text
NDefines.NGraphics.VICTORY_POINT_MAP_ICON_MAX_VICTORY_POINTS_FOR_PERCENT = 22; --Default max value for point on the above range. It doesn't matter much if the VP value exceeds this, it'll be treated as max.
NDefines.NGraphics.AIRBASE_ICON_DISTANCE_CUTOFF = 900; --At what distance air bases are hidden
NDefines.NGraphics.NAVALBASE_ICON_DISTANCE_CUTOFF = 900; --1300; --At what distance naval bases are hidden
NDefines.NGraphics.RADAR_ICON_DISTANCE_CUTOFF = 900; --At what distance the radars are hidden
NDefines.NGraphics.RESOURCE_MAP_ICON_TEXT_CUTOFF = 800;  -- At what camera distance the resource name/amount text disappears.
NDefines.NGraphics.RESISTANCE_MAP_ICON_MODIFIERS_DISTANCE_CUTOFF = 500;  -- At what camera distance the resistance/compliance map icon modifiers are hidden
NDefines.NGraphics.RESISTANCE_MAP_ICON_DISTANCE_CUTOFF = 1200;  -- At what camera distance the resistance/compliance map icons are hidden
NDefines.NGraphics.PROVINCE_ANIM_TEXT_DISTANCE_CUTOFF = 500;
NDefines.NGraphics.CAPITAL_ICON_CUTOFF = 1500;	-- At what camera distance capital icons disappears
NDefines.NGraphics.UNITS_DISTANCE_CUTOFF = 120;
NDefines.NGraphics.SHIPS_DISTANCE_CUTOFF = 240;
NDefines.NGraphics.UNIT_ARROW_DISTANCE_CUTOFF = 875;
NDefines.NGraphics.UNITS_ICONS_DISTANCE_CUTOFF = 900;
NDefines.NGraphics.NAVAL_COMBAT_DISTANCE_CUTOFF = 1500;
NDefines.NGraphics.FACILITY_DISTANCE_CUTOFF = 900;
NDefines.NGraphics.ADJACENCY_RULE_DISTANCE_CUTOFF = 1700;
NDefines.NGraphics.LAND_COMBAT_DISTANCE_CUTOFF = 1500;
NDefines.NGraphics.PROV_CONSTRUCTION_ICON_DISTANCE_CUTOFF = 400;
NDefines.NGraphics.STATE_CONSTRUCTION_ICON_DISTANCE_CUTOFF = 800;
NDefines.NGraphics.DECISION_MAP_ICON_DISTANCE_CUTOFF = 1000;
NDefines.NGraphics.DECISION_MAP_ICON_DEPTH_PRIORITY = 50;
NDefines.NGraphics.NAVAL_MISSION_TASK_FORCES_GROUP_BY_ALLEGIANCE_CUTOFF = 500;
NDefines.NGraphics.NAVAL_MISSION_ICONS_DISTANCE_CUTOFF = 900; --1300;
NDefines.NGraphics.NAVAL_MINES_DISTANCE_CUTOFF = 800;
NDefines.NGraphics.CRYPTOLOGY_MAP_ICON_DISTANCE_CUTOFF = 1000;
NDefines.NGraphics.PEACE_CONFERENCE_MAP_ICON_DISTANCE_CUTOFF = 500;
NDefines.NGraphics.NAVAL_MINES_CLUMPING = 58; --The higher value, the more likely the 3d naval mines will clamp together
NDefines.NGraphics.NAVAL_MINES_CLUMP_NEAR_TERRITORY = 25; --Higher chance to spawn 3d naval mine near our territory
NDefines.NGraphics.NAVAL_MINES_COUNT_TO_VISUAL_ASPECT = 0.1; --How many in-game-naval-mines is one visual 3d naval mine?
NDefines.NGraphics.MAP_ICONS_GROUP_CAM_DISTANCE = 100.0; --camera distance at which the icons begin to group up
NDefines.NGraphics.MAP_ICONS_STATE_GROUP_CAM_DISTANCE = 325.0; --Camera distance at which the icons begin to group up on state level
NDefines.NGraphics.MAP_ICONS_STRATEGIC_GROUP_CAM_DISTANCE = 400; --second camera distance at which the icons begin to group up
NDefines.NGraphics.MAP_ICONS_STRATEGIC_AREA_HUGE = 220;
NDefines.NGraphics.MAP_ICONS_STATE_HUGE = 100;
NDefines.NGraphics.MAPICON_GROUP_PASSES = 20; --how many mapicons get processed per frame for grouping. more = quicker response, fewer = better performance
NDefines.NGraphics.MAP_ICONS_GROUP_SPLIT_SELECTED_LIMIT = 10;   -- Maximum number of units selected that will cause icon stacks to split
NDefines.NGraphics.MAP_ICONS_COARSE_COUNTRY_GROUPING_DISTANCE = 200; --Distance at which icon grouping becomes very coarse and merges different types of units
NDefines.NGraphics.MAP_ICONS_COARSE_COUNTRY_GROUPING_DISTANCE_STRATEGIC = 0; --Distance at which icon grouping becomes very coarse and merges different types of units for strategic mapmodes
NDefines.NGraphics.RIVER_FADE_FROM = 20.0; --the last river endings got faded out, X distance from the ending...
NDefines.NGraphics.RIVER_FADE_TO = 3.0;
NDefines.NGraphics.TOOLTIP_DELAYED_DELAY = 1; 						--How long before showing delayed tooltip.
NDefines.NGraphics.TOOLTIP_SHOW_DELAY = 0.05; 						--How long before showing delayed tooltip.
NDefines.NGraphics.TOOLTIP_HIDE_DELAY = 0.05; 						--How long before showing delayed tooltip.
NDefines.NGraphics.INTEL_LEDGER_CIVILIAN_ICON_STATE_CUTOFF = 250.0;
NDefines.NGraphics.INTEL_LEDGER_CIVILIAN_ICON_REGION_CUTOFF = 700.0;
NDefines.NGraphics.RAILWAY_CAMERA_CUTOFF = 200.0; --railways are cut off above this camera height
NDefines.NGraphics.RAILWAY_CAMERA_CUTOFF_SPEED = 3.0; --railways fade in/out speed
NDefines.NGraphics.DIVISION_NAMES_GROUP_MAX_TOOLTIP_ENTRIES = 15;	-- Max entries to display the names in the tooltip, when mouse over the division-names-group in the division template designer.
NDefines.NGraphics.NAMES_GROUP_MAX_NAME_LIST_ENTRIES = 25;	-- Max example name entries in ship and railway gun name list in production menu
NDefines.NGraphics.POSTEFFECT_PER_PROVINCE_MIN_SNOW = 0.1;
NDefines.NGraphics.POSTEFFECT_PER_PROVINCE_MAX_SNOW = 0.2;
NDefines.NGraphics.POSTEFFECT_TOTAL_MIN_SNOW = 0.0;
NDefines.NGraphics.POSTEFFECT_TOTAL_MAX_SNOW = 0.05;
NDefines.NGraphics.POSTEFFECT_FEATHER_MIN_DISTANCE = 300.0;
NDefines.NGraphics.POSTEFFECT_FEATHER_MAX_DISTANCE = 1200.0;
NDefines.NGraphics.POSTEFFECT_FEATHER_AT_MIN = 0.03;
NDefines.NGraphics.POSTEFFECT_FEATHER_AT_MAX = 0.80;
NDefines.NGraphics.LAND_COMBAT_BALANCED_COLOR = { 1.0, 1.0, 0.0, 1.0 };
NDefines.NGraphics.LAND_COMBAT_LOSING_COLOR = { 1.0, 0.0, 0.0, 1.0 };
NDefines.NGraphics.LAND_COMBAT_WINNING_COLOR = { 0.0, 1.0, 0.0, 1.0 };

NDefines.NGraphics.MAPICON_GROUP_STRATEGIC_SIZE = 1000;
NDefines.NGraphics.COMMANDGROUP_PRESET_COLORS_HSV = {
	0.0/360.0, 1.0, 0.75,	--red
	10.0/360.0, 1.0, 0.75,	--orange
	60.0/360.0, 1.0, 0.75,	--yellow
	120.0/360.0, 0.85, 0.75,	--green
	155.0/360.0, 1.0, 0.75,	--greenish
	180.0/360.0, 1.0, 0.75,	--turq
	220.0/360.0, 1.0, 0.75,	--blue
	260.0/360.0, 1.0, 0.85,	--dark purple
	330.0/360.0, 0, 0.75		--white
};
NDefines.NGraphics.CAMERA_ZOOM_SPEED_DISTANCE_MULT = 20;
NDefines.NGraphics.STRATEGIC_AIR_COLOR_BAD = {0.65, 0, 0, 1};
NDefines.NGraphics.STRATEGIC_AIR_COLOR_GOOD = {0, 0.65, 0, 1};
NDefines.NGraphics.STRATEGIC_AIR_COLOR_AVERAGE = {0.65, 0.65, 0, 1};
NDefines.NGraphics.STRATEGIC_AIR_COLOR_NEUTRAL = {130.0/255, 130.0/255, 130.0/255, 1};
NDefines.NGraphics.GRADIENT_BORDERS_THICKNESS_STRATEGIC_REGIONS = 250.0;
NDefines.NGraphics.GRADIENT_BORDERS_THICKNESS_SUPPLY_AREA_A = 250; --250.0
NDefines.NGraphics.GRADIENT_BORDERS_THICKNESS_SUPPLY_AREA_B = 250; --250.0
NDefines.NGraphics.STRATEGIC_NAVY_COLOR_MISSION = {0.65, 0.65, 0.0, 1};
NDefines.NGraphics.STRATEGIC_NAVY_COLOR_NEUTRAL = {130.0/255, 130.0/255, 130.0/255, 1};
NDefines.NGraphics.ROOT_FRONT_OFFSET = 2;
