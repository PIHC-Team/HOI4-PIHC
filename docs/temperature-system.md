# Temperature system

The temperature system is evaluated once per calendar month. The generic HoI4 monthly hook runs for multiple countries; a global year/month guard must prevent each callback from recalculating the world. Native testing reproduced 302 unintended world updates over roughly five calendar months before this guard was added. Outdoor temperature is a random seasonal baseline plus a random terrain correction and the controller’s outdoor-temperature influence, minus global disharmony (world tension × 60) and the controller’s tension contribution × 0.3. The result is clamped to −50…50 °C. C15, C17 and C27 retain their original −8 °C first-month cold snap.

Indoor temperature starts from outdoor temperature. Each local generator-complex level adds 15 °C; each neighboring state with a generator adds 5 °C regardless of its level. Cold technology adds 3 °C per level. Heating policy adds `(5 + technology level) × policy level`, coal subsidy adds 10 °C and wood subsidy adds 5 °C. The burn policy overrides the result to 20 °C. Indoor temperature is also clamped to −50…50 °C.

Indoor temperature determines the seven comfort classes and state modifiers. Comfort scores are 1 below −40; 3 from −40; 7 from −20; 8 from −10; 10 from 0; 9 from 30 through 40; and 1 above 40 °C. National effects use a population-weighted mean of these scores, retaining the existing 2.5/4/6/7.5 thresholds. Zero-population countries receive neutral/warm comfort 10 without division.

## Monthly execution

1. Resolve the seasonal random bounds once and cache each country’s policy, technology, resource costs and outdoor influence.
2. Clear neighbor heat, then visit neighbors only from states containing a generator.
3. In one controlled-state pass per country, calculate outdoor and indoor temperatures once, derive comfort/modifiers once, and collect subsidy costs and weighted population totals.
4. Finalize national effects, then copy national tooltip values and population shares to controlled states in one final pass. Refresh the country’s dynamic modifiers once.
5. Increment one global GUI revision. There is no weekly temperature callback.

The previous code evaluated indoor temperature and all-state adjacency twice and comfort three times per monthly update. Repeated policy/technology/subsidy scans have been removed. Population is converted from thousands to millions before multiplication, avoiding unsafe large intermediate weighted sums; precision is to approximately 1,000 inhabitants. The old 14,760 × 410 mercury strip is removed from the runtime package.

Startup is guarded by `PIHC_temperature_initialized`. The seasonal month is derived from the engine’s `global.num_days` on its 365-day calendar, so stale or previously drifted counters self-correct. Subsequent reloads do not reroll weather. A unique year/month key guards both simultaneous and staggered callbacks. Changes to towers, controller, policy and technology are reflected on the next monthly update, matching the existing monthly cadence.

The self-heating policy no longer charges all three government heating costs. Only the selected policy’s resource/factory cost is charged. A wood shortage can fall back to subsidies even if coal is still available.

## Mercury display

The existing single `mercury.dds` is drawn inside a clipped container at y=40 with height 438. The mercury sprite's y coordinate is `129 − 4 × clamp(outdoor temperature, −39, 42)`. Its visible top is therefore `40 + 39 + y = 208 − 4T` in artwork coordinates. Sprite positions inherit the parent 1.28 scale; applying that scale again caused r5's −1 °C sample to appear near −13 °C. Only the clipping height requires compensation: 342 × 1.28, rounded up to 438. The panel restores its legacy lower-right attachment at y=−362. The indoor pointer retains its seven meaningful class frames. One global revision replaces the former five conflicting `dirty` entries.

Existing saves retain their cached mercury coordinate until the next monthly temperature update. New games initialize the corrected coordinate immediately.

The implementation follows the installed HoI4 `common/scripted_guis/_documentation.md` property and dirty-variable contract. Tests execute the authored arithmetic rather than a separately maintained formula; native engine tests are still required for scope, scheduling and UI behavior.

## Validation

Targeted arithmetic tests cover all class boundaries, heating and the burn override, display clamps and fractional positions, two simulated years, generator removal, empty countries, and a 1.5-billion-population country. Native HoI4 1.19.2 completed 120 consecutive world updates in a disposable C08 campaign: revision advanced from 1 to 121 and the month returned to December. No temperature-related engine errors were recorded. These checks do not establish that every unrelated campaign branch is crash-free.

Final native verification: December 1002 → March 22, 1003 produced exactly three scheduled updates (revision 1 → 4), with the season correctly at month 3. The final calculation completed another 120 forced updates (revision 4 → 124), self-heating logged zero coal/wood/factory costs, and every state had an initialized outdoor temperature. No temperature-specific errors were recorded. The guarded test exited normally through the game menu; an earlier pre-guard test stalled after a direct quit/hot-reload session and required force quit.

The r5 endpoint-only visual check missed an intermediate-position error. The r6 clean launch checked −30, −10, +10 and +30 °C against labeled ticks and +42 °C against the top of the tube. The user's exact case logged outdoor −1, indoor 4 and mercury_y 133; the central indoor dial obscures the mercury tip near zero, as in the existing artwork. The legacy attachment was restored; the small native test window clips the bottom of both the state view and attached panel, so it does not establish full visibility at every resolution. Thirty-eight targeted temperature tests pass, including ten outdoor samples with an independent indoor value, clamps and a fractional position. The generated build has zero diagnostics. Only the scripted-effect and interface-GUI game files differ from r5; monthly calculations and localization bytes are unchanged.
