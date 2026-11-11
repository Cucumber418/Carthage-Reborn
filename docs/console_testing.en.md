# Console and Language Checks — 1.3.0

These scenarios are prepared from the scripts. They have not been run in a Victoria 3 process.

## Preparation

Enable `-debug_mode` in the game's launch options, set the game language to **English**, and fully restart. Begin a non-Ironman Carthaginian game and keep a clean test save.

Use the console for `text` blocks, one command at a time. Use the country inspector's **Script Runner → Effect** for `pdx` blocks.

```text
tag TUN
money 10000000
```

The country should appear as **Punic State**, with Carthage as its capital, Punic culture, the Cult of Tanit, and Dual Suffetes. Check Interventionism, Migration Controls, three frigates, and one naval base level.

## Territorial Government

From a peaceful starting save:

```text
own STATE_CONSTANTINE TUN
```

Allow the relevant checks to run. **Carthage's Territories** should offer **Organize Numidia**. Choose a trading post, a province, or continued direct rule. Only eligible land actually owned by Carthage is transferred.

Each row below is a separate test. Load a clean save to compare mutually exclusive forms.

| Region | Console command |
| --- | --- |
| Tripoli | `own STATE_TRIPOLI TUN` |
| Numidia | `own STATE_CONSTANTINE TUN` |
| Iberia | `own STATE_MURCIA TUN` |
| Gaul | `own STATE_PROVENCE TUN` |
| The Alps | `own STATE_PIEDMONT TUN` |
| Southern Italy | `own STATE_APULIA TUN` |
| Mauretania | `own STATE_FEZ TUN` |
| Egypt | `own STATE_MIDDLE_EGYPT TUN` |
| Phoenicia | `own STATE_LEBANON TUN` |
| Syria | `own STATE_ALEPPO TUN` |
| Mesopotamia | `own STATE_BAGHDAD TUN` |
| Arabia | `own STATE_YEMEN TUN` |

Foundations share a three-month handover. Canceling a foundation should leave other buttons usable. After a successful foundation, their buttons remain visible but unavailable until the handover ends.

To speed up later tests, open the country inspector with `inspect_country TUN` and run:

```pdx
c:TUN = { remove_modifier = crb_territory_disposition_cooldown }
```

This shortcut does not verify natural expiry.

After establishing the Numidian Trading Post, check **Provincialize Numidia**. It should require peace and an expired handover, add 15 Infamy, switch payments from 30% to 50%, remove commercial privileges, and retain the existing country's assets and current Liberty Desire.

The conversion button should disappear, replaced by **Expand the Numidian Province**. Acquiring Oran with `own STATE_ORAN TUN` should let that expansion button transfer only the relevant land.

For the 1.2.9 colonization exclusion, test both subject forms and the bulk expansion Decision with an actual ongoing colony in the relevant region. With only land being colonized, expansion should be unavailable. With another eligible non-capital state, transfer only that eligible state and preserve the colony's ownership and progress. Once colonization ends, the excluded state should become eligible if the other requirements are met. Foreign land, capitals, and other subjects' regions remain protected. Changing ownership with `own` alone is not a substitute for testing a real colonization process; the UI and colony continuity still need in-game validation.

For the Roman case, establish the Ionian Trading Post and use **Provincialize Rome**. The same country should become the Roman Province (RPR). A separately existing RPR must block conversion without being overwritten or charging Infamy.

## English Text and Icons

- Check the country panel, subject list, relationship tooltip, and concept tooltip. The names must read **Trading Post** and **Province**, with their English descriptions.
- The country relationship retains its graphical icon. Names and territorial buttons must not insert a second text icon.
- Check Governor, Governorship, the Carthaginian Trading House name, modifiers, and event options.
- No `crb_…`, `je_crb_…`, or `concept_crb_…` keys should appear as labels.
- Check that dynamic names and values render correctly rather than appearing as raw `$…$` or `[…]` expressions.
- Check restored map names and Hanno's live target names before and after acquisition, including Mauretania, Cerne, Chretes, and Chariot of the Gods after the mod's renaming.
- Check that Punic War titles use English ordinals such as **Fourth Punic War**.
- Inspect long event bodies and territorial buttons for clipping.
- Foundation tooltips should highlight the future country and overlord, link the Trading Post or Province concept, and emphasize 30% or 50% payments and the three-month handover. Check both the original regions and the six hidden regions.

Restart in Simplified Chinese and check the same screens, then repeat with an existing save. Both languages should show the same mechanics and numbers, while names and prose follow the selected language.

## Events and Routes

Large event text and quotations should tell the story. Check the Hannibal introduction and the four revenge-route events: their bodies must not state Infamy costs, while the relevant option effects retain the original 10/10/15/20/25 Infamy and claims. Historical dates and elapsed time within the story are legitimate narrative details.

The Cothon planning event should describe the engineers' plans; the construction unlock is explained by the confirmation option's tooltip. Territorial event bodies should retain their local setting, with non-capital-state restrictions shown in the foundation tooltips instead.

To inspect the opening event's English:

```text
event crb_carthage.1 TUN
```

The first conquest should also open the factional struggle. Full Barcid victory and the Barcid advantage at the three-year deadline now settle victory directly, before confirmation of the victory notice. A stalemate choice for the Barcids must also open **Hannibal Returns**. Reconfirming the notice must not repeat settlement or refresh its modifier. If journal registration is deferred, the pending request must survive for the next monthly retry. Later adoption of a colonial law must not repeat the introduction.

For an existing save where a normal Barcid victory never produced either the opening or the journal, fully restart after updating and allow the monthly recovery check. If an unfinished request was previously marked as shown, this manual Effect Script Runner command retries it:

```pdx
c:TUN = { crb_repair_hannibal_start_effect = yes }
```

It requires an eligible Barcid route, no active Hannibal journal, and no opening reward, objective progress, conclusion, or final modifier. It clears only startup markers before retrying. It cannot reset routes with rewards or progress. Directly forcing the Barcid victory event is a real settlement, not a cosmetic preview, and does not replace testing natural journal outcomes.

To arrange the initial French border:

```text
own STATE_ALGIERS FRA
own STATE_CONSTANTINE TUN
```

Allow the border or monthly check to run. **Gauls?** should offer the payments and truce, confrontation, and non-intervention options. All three have five-year policy terms; payments enter both budgets weekly, while relations change once when chosen. A European border alone must not start the event.

For text inspection only:

```text
event crb_flavor.17 TUN
```

Manual event calls do not validate the normal scheduling or border trigger. Hover over all three choices: the agreement shows only its actual weekly payment for five years, +20 relations and a five-year truce; confrontation shows only -50 relations and +10% Kill Rate for five years; non-intervention shows reconsideration in five years. Use the vanilla automatic effect list, country and value formatting, modifier breakdowns, and hover details. No hand-written paragraph should replace those effects; no other policy removals or GDP formulas should appear. The payer and France must have opposite budget entries of exactly the same whole-unit weekly amount for 60 months, without an immediate Treasury transfer. The rate is 0.12% of the payer's GDP, rounded when chosen: 800–900K GDP gives 960–1,080 per week, fixed for the term. France leaving North Africa must clear both payment modifiers on the monthly check while preserving the existing truce. Old saves with the former one-time agreement start payments only on their next choice. Event monetary previews retain vanilla K/M abbreviations; check the small and large values and confirm income/expense colors and durations.

The Cothon's completion event must wait until at least one building level is complete. A level-zero construction site is insufficient.

## Additional European Territories

Use separate pre-foundation saves for each region. Own one non-capital state at peace, then check its foundation button in Carthage's Territories.

| Region | Console command | Subject tag |
| --- | --- | --- |
| Lusitania | `own STATE_ESTREMADURA TUN` | `XLU` |
| Etruria | `own STATE_TUSCANY TUN` | `XET` |
| Illyria | `own STATE_DALMATIA TUN` | `XIL` |
| Achaea | `own STATE_ATTICA TUN` | `XAC` |
| Macedonia | `own STATE_MACEDONIA TUN` | `XMA` |
| Thrace | `own STATE_EASTERN_THRACE TUN` | `XTH` |
| Moesia | `own STATE_BULGARIA TUN` | `XMO` |
| Dacia | `own STATE_WALLACHIA TUN` | `XDA` |
| Pannonia | `own STATE_CENTRAL_HUNGARY TUN` | `XPA` |
| Noricum | `own STATE_AUSTRIA TUN` | `XNO` |
| Belgica | `own STATE_FLANDERS TUN` | `XBE` |
| Germania | `own STATE_RHINELAND TUN` | `XGE` |

For all twelve regions, test all three choices, creation-time primary cultures and laws, both names and flags, conversion in place, and individual/bulk expansion. Provinces and conversions cost 15 Infamy; Trading Posts have no foundation Infamy. New foundations and conversions share the three-month handover. Capitals, foreign holdings, and ongoing colonies remain protected from expansion. War, cooldown, loss of land before confirmation, or an existing foreign tag must prevent creation and Infamy charges. Test one non-capital holding away from the nominal capital as well. Luxembourg is covered through Wallonia. Existing-subject saves with no new direct land must still recover the journal on the monthly check.

## New Subject Cultures and Laws

Found both subject forms under each current Carthaginian colonial policy: No Colonial Affairs, Internal Colonization, Frontier Colonization, Colonial Resettlement, and Colonial Exploitation. Each new country must keep its original primary cultures and add Punic, adopt Subjecthood, and retain its Governorship. The latter four founder policies must give the new subject Frontier Colonization; No Colonial Affairs must not enable it. Carthage's own cultures and laws must remain unchanged. Later founder law changes must not rewrite existing subjects. Check Tripolitanian and Numidian subjects in particular: adding Punic must not activate Carthage's factional journal for them. These settings initialize new countries; they do not migrate existing subjects or rerun on provincialization.

## Subject State Transfers

Test **Take State** and **Grant State** on both a Trading Post and a Province with several states, satisfying the normal conditions shown by the vanilla UI. Taking an eligible non-capital state should work; capital and other eligibility restrictions should remain. When granting a state, check eligible land owned directly by Carthage and land held by another Trading Post or Province. Another country's subjects must not supply land. Compare costs and Liberty Desire changes against an ordinary vanilla subject. These interactions should use the vanilla state-selection and execution flow. Restart with the updated mod and include an existing save in the in-game checks.

Version 1.2.8 loading regression: hover over a disabled **Take State** button. A Trading Post or Province should no longer fail the Colony/Puppet/Vassal type requirement. Other vanilla conditions remain, including Liberty Desire below 50, no committed Diplomatic Play participation or revolution, and a selectable non-capital state that is not being colonized. Existing custom subjects need not be founded again for this check. Both actions now use the mandatory `REPLACE:` database mode; the automated check validates that mode as well as the action bodies. Actual button behavior still requires in-game validation.

## Companies and Music

```text
research corporate_charters
```

The mod adds only the Carthaginian Trading House. Own an incorporated Tunisia with at least three levels of Trade Centers or Ports, then establish the company through the normal interface. Check its custom emblem, vanilla harbor/shipbuilding background, English name, and prosperity bonuses (+10% Trade Advantage and +5% Trade Capacity). Default industries remain Trade Centers and Ports; an additional-industry charter offers Arts Academies. The other three custom companies, their two Prestige Goods, and the specialized Lebanese dye plantation have been removed.

For a quick company preview in Script Runner:

```pdx
c:TUN = { add_company = company_type:company_crb_carthaginian_trade_house }
```

For the additional-industry check, research Romanticism or run this in a test save:

```text
research romanticism
```

Open **Carthaginian Trading House → Company Charters → Industry Rights → Select Additional Industry**. Arts Academies should be offered and added to the company's industries after granting the charter, while Trade Centers and Ports remain its defaults. Version 1.2.7 uses the current vanilla ID, `building_art_academy`; the old `building_arts_academy` name was replaced in 1.12. The separate vanilla Trade Rights charter still refers to Trade Centers.

Fully exit the game, update the mod copy actually loaded, and check the existing save first. If another industry charter is already active, revoke it when allowed before applying again. Use a separate new test save for comparison if needed, preserving the original. These UI and save-loading steps still require in-game validation.

For music, enable **Carthage**, select **Weighted** mode, and run:

```text
Music.ListTracks
```

Find `crb_carthage_theme`. Its Carthaginian weight is 100000 in January 1836 and 500 afterward; an ordinary other country has weight 1. Startup music requests require a new game and remain subject to the music player's normal restrictions.

## Automated Checks

```sh
python -m unittest discover -s tests -v
```

The bilingual checks require matching keys and language files, valid UTF-8 BOM encoding, complete UI references, intact substitutions and formatting, equal visible numbers, and English values without untranslated Chinese.

## Interest Group Names

Check Interest Group panels, event bodies, journal entries, and effect tooltips. Landholders, Shipowners, Votaries, and Scribes should show their current name without a generic type in parentheses. The same shared format applies to variants in other countries and in Chinese.

## Hannibal Opening Must Not Replay After Colonial Laws

Test a new campaign and a pre-update save. After a Barcid victory, accept the single opening and record the 10 Infamy and claims. Enact Colonial Exploitation: the Voyage of Hanno may activate, while the existing Hannibal journal must continue without another opening or Infamy charge. Repeat law changes and monthly checks. Old active journals and old progress must count as already started, even without the new markers; completed routes must stay closed.

Repeated `crb_try_start_hannibal_route_effect = yes` calls in the Effect Script Runner are useful for inspecting the guard, but forcing event IDs does not replace the natural law-change test.

## Live Voyage Target Names

Check all four objective titles and conditions against the current map. Before acquisition they should use the existing names; after the mod renames the held states they should show Mauretania, Cerne, Chretes, and Chariot of the Gods. Disabling dynamic names or manually renaming a state must keep the journal consistent with the actual map.

For split states, directly held land takes priority over a Carthaginian subject's land and then the largest current state in the region. Test subject transfers and loss of control. Existing saves refresh on the monthly check; `crb_refresh_hanno_target_names_effect = yes` in the Effect Script Runner refreshes the references immediately. Check both languages for raw keys, invalid State references, and clipping.

The automated scenarios do not run Victoria 3's event or GUI engine.
