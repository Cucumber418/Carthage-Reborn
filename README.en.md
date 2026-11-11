# Carthage Reborn

[简体中文](README.md) | **English**

A Victoria 3 alternate-history mod. In 1836, Tunisia is replaced by a newly restored Punic state. Conservative senators govern an unrecognized republic, but the army and the Popular Assembly have ambitions of their own. Choose between the Hannonids and the Barcids, revive Punic culture, and follow the routes of Hanno or Hannibal.

- Version: **1.2.6**
- Victoria 3: **1.15.\***
- Languages: **English and Simplified Chinese**, included in the same mod and selected by the game's language setting.
- Content: 7 Journal Entries, 2 Decisions, 74 event definitions, 1 company, 13 possible subject countries across 12 regions, and an original Carthaginian music track.
- Workshop descriptions: [English](docs/workshop_description_english.txt) / [Chinese](docs/workshop_description.txt).

## Language

Set the game language to **English**, fully exit the game, and restart. The same mod and gameplay scripts serve both languages; a separate English Workshop subscription is unnecessary. Existing saves can be used.

English covers all **1,098 localization keys**: country and character names, cultures and religions, laws and governments, events, journals, decisions, territorial buttons, subject concepts, companies, modifiers, and historical place names. English files mirror the Chinese directory, including the `replace` overrides. No additional language button is required inside the mod. Interest Group variants display their current name alone, without an appended generic type in parentheses.

## The Punic Republic

The starting country uses Tunisia's `TUN` tag. It begins as the independent, unrecognized **Punic State**, taking the name **Carthage** after recognition.

Its primary culture is Punic, its religion the Cult of Tanit, and its capital Carthage. The government begins under **Dual Suffetes**, with Oligarchy, Hereditary Bureaucrats, Interventionism, Migration Controls, Mercantilism, and State Religion. The Landholders and Votaries govern, while the Shipowners and Armed Forces remain outside government.

The starting navy is adjusted to three frigates, with one naval base level. New-game history changes do not replace the laws or military of an existing save.

## Journals and Events

- **The Hannonids and the Barcids** opens after Carthage or its actual subjects acquire land in Constantine or Tripoli. The Hannonids favor the Senate, African estates, and commerce. The Barcids favor the Popular Assembly and overseas expansion. The contest lasts up to three years, with concessions and political events influencing its outcome.
- **Carthaginian Cultural Revival** restores plantations, reclaims the salted land over ten years, spreads the worship of Tanit, and rebuilds the **Cothon**. Its completion event requires a completed building level, rather than a newly placed construction site.
- **Hannibal Returns** is the Barcid route to the pre-Punic-War dominions: Tripoli, Numidia, Sicily, the Mediterranean islands, Iberia, and Tyre. Its land objectives count Carthage's holdings and those of its actual subjects. The opening has a single guarded country-level entry point. Existing saves with an active journal, prior opening, progress, or completion are marked as already started; enacting colonial laws cannot replay the opening or charge its Infamy again.
- **Punic War** journals accompany conflict with the rulers of Sicily. Their titles begin with the Fourth Punic War and advance with subsequent wars.
- **Two Thousand Years of Vengeance** follows Hannibal from Iberia through Gaul and over the Alps toward Rome.
- **The Voyage of Hanno** opens through the Hannonid route or colonial laws. Follow the Atlantic coast to Lixus, Cerne, the Chretes, and the Chariot of the Gods, and maintain ten consecutive years of peace. Target titles and conditions use live map names: current foreign names before acquisition, then the actual renamed names afterward. Split states prefer directly held land, then a Carthaginian subject, and otherwise the largest current state in the region.
- **Carthage's Territories** manages the creation, individual expansion, and provincialization of overseas possessions independently of the main political routes.

Sixteen additional flavor events draw upon Carthaginian history, agriculture, religion, trade, literature, and privateering.

Event bodies and flavor text describe the setting and its people. Mechanical costs, unlock notices, and territorial restrictions are explained by option effects and tooltips. Foundation tooltips highlight country names and key values, link to the subject-type concepts, and retain each region's narrative description.

**Gauls?** first becomes eligible when Carthage shares a land border with French territory in North Africa. Thereafter, choose a policy every five years while France retains North African land:

1. Pay France 0.12% of Carthage's annual GDP each week for five years, rounded when chosen; improve relations by 20 and sign a mutual five-year truce.
2. Reduce relations by 50 and gain 10% Kill Rate for five years.
3. Let events take their course and reconsider after five years.

The payment agreement cannot be selected while France is an enemy in a war or Diplomatic Play. The cycle ends when France leaves North Africa; an existing truce keeps its original term. Each choice shows only its own effects; cleanup of other policies stays hidden. Event effects use the vanilla automatic tooltips, including modifier breakdowns, hover details, colored values, and durations, without money formulas. At a starting GDP of 800–900K, the agreement costs 960–1,080 per week. Both countries receive equal five-year budget modifiers, fixed for the term and removed together if France leaves North Africa. Existing saves already using the former one-time agreement incur no retroactive payments; the next choice uses the new scheme. Weekly payments and income rewards are rounded to whole units, while large amounts retain vanilla K/M abbreviations.

## Trading Posts and Provinces

Acquire any directly owned non-capital state in an eligible region while at peace to open **Carthage's Territories**. You do not need to conquer the entire region. Constantine alone can support a Numidian subject; a holding in Provence can support a Gallic subject.

Both subject forms use a non-hereditary **Governorship**, a special form of monarchy.

| Form | Payments | Administration |
| --- | --- | --- |
| Trading Post | 30% of income | Free Trade and Laissez-Faire; export and import advantages, plus Trade Center and Port throughput privileges. No foundation Infamy. |
| Province | 50% of income | Oligarchy, Appointed Bureaucrats, Secret Police, Mercantilism, and State Religion. Foundation costs 10 or 15 Infamy. |

Each relationship costs the overlord 10 Influence. Newly established subjects receive Carthage's Protection. Its small weekly Liberty Desire modifiers follow the scale of vanilla subject interactions.

| Region | Trading Post / Province | Province Infamy |
| --- | --- | --- |
| Tripoli | Tripolitanian Trading Post / Tripolitanian Province | 10 |
| Numidia | Numidian Trading Post / Numidian Province | 15 |
| Iberia | Iberian Trading Post / Iberian Province | 15 |
| Gaul | Gallic Trading Post / Gallic Province | 15 |
| The Alps | Snow Mountain Trading Post / Alpine Province | 15 |
| Southern Italy | Ionian Trading Post / Roman Province | 15 |
| Mauretania | Mauretanian Trading Post / Mauretanian Province | 10 |
| Egypt | Egyptian Trading Post / Egyptian Province | 15 |
| Phoenicia | Phoenician Trading Post / Phoenician Province | 10 |
| Syria | Syrian Trading Post / Syrian Province | 15 |
| Mesopotamia | Mesopotamian Trading Post / Mesopotamian Province | 15 |
| Arabia | Arabian Trading Post / Arabian Province | 15 |

The final six regions remain hidden until eligible land is acquired. Subjects receive only the relevant non-capital land Carthage actually owns; foreign holdings, the homeland, Sicily, and the current capital are protected.

Founding a subject or converting a trading post into a province starts a **shared three-month handover** across all regions. Canceling a foundation and expanding an existing subject do not start this cooldown.

Each trading post has a **Provincialize** button in the territorial journal. Conversion uses the existing country, retaining its assets and current Liberty Desire. It charges the same Infamy as directly founding the province, replaces the commercial privileges with provincial arrangements, and switches to the province's expansion button. The Ionian Trading Post becomes the Roman Province, provided a separate Roman Province does not already exist.

Existing subjects each have their own expansion button. The **Expand the Trading Posts** Decision can still transfer eligible new territory to all actual subjects at once. The **Convert to Islam** Decision provides another course for the country's religion.

## Carthaginian Trading House, Art, and Music

The mod adds one company: the **Carthaginian Trading House**, engaged in trade and shipping through Carthage. It requires Corporate Charters and at least three levels of Trade Centers or Ports in incorporated Tunisia. Its industries are Trade Centers and Ports, with Arts Academies as an extension. Prosperity grants +10% Trade Advantage and +5% Trade Capacity.

The company retains its custom emblem and vanilla harbor/shipbuilding background. Subject relationships and the Cothon retain their dedicated artwork; original art containing the retained Trading House remains archived in [docs/art](docs/art).

The supplied track **Carthage** is integrated with Victoria 3's 1.15 music system. In **Weighted** mode it is heavily favored for Carthage, particularly at the start of 1836. A new Carthaginian game has an 85% chance to request it at startup; disabled tracks, cooldowns, and non-interruptible music can prevent immediate playback. Random and Least Played modes do not reproduce the intended weighting.

## Installation and Testing

Enable this mod in the Victoria 3 launcher. It replaces Tunisia and conflicts with other mods that replace the same country. Use the same Workshop item for both supported languages.

For a local checkout, place the mod in the Victoria 3 mod directory and add it to a launcher playset. Pull updates from `main`, fully restart the game, and select the desired game language. Version 1.2.5 removes custom company, Prestige Good, and specialized building definitions; loading saves containing those objects has not been tested in the game.

[English console and language checks](docs/console_testing.en.md) cover the main test points. The [Chinese test guide](docs/console_testing.md) contains the longer scenario reference.

Run the automated checks from the repository root:

```sh
python -m unittest discover -s tests -v
```

The 113 checks cover territorial safeguards, provincialization, recurring events, governance, route separation, building completion, localization references, complete language coverage, and preservation of dynamic expressions and numbers. These are static and simulated-script checks, not an in-game test.

Known limitation: the automatic Hannonid result at the three-year deadline still lacks part of its victory effects. Reaching the Hannonid end of the progress bar, or choosing the Hannonids in the stalemate event, uses the complete victory path. This update does not change that deadline behavior.
