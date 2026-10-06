#!/usr/bin/env python3
"""Build evidence-backed narrative design artifacts from current master data."""

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))
def write_json(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
def write_text(name, value):
    (ROOT / name).write_text(value.rstrip() + "\n", encoding="utf-8")

NPCS = read("npc_list.json")
QUEST_DIALOGS = read("dialog_quests.json")["dialogues"]
MASTER_BLOCKS = read("dialog_tree_master.json")
MASTER = [d for block in MASTER_BLOCKS for d in block.get("dialogues", [])]
QUESTS = {q["id"]: q for f in ["quest_concordium.json", "quest_arcanum.json", "quest_iron.json", "quest_meridian.json", "quest_omnicorp.json", "quest_shard.json", "quest_legion.json", "quest_neutral.json"] for q in read(f).get("quests", []) if q.get("id")}
NPC_BY_ID = {n["npc_id"]: n for n in NPCS}
MASTER_BY_ID = {d["dialog_id"]: d for d in MASTER if d.get("dialog_id")}

IDENTITIES = [
    {"canonical_id":"npc_commander_lirien_vale","canonical_name":"Commander Lirien Vale","canonical_title":"Concordium Field Commander","faction":"CONCORDIUM","role":"QUEST_GIVER","aliases":["Lirien Vale","Commander Vale"],"legacy_ids":["npc_commander_vale","npc_concordium_officer (dialogue assignment only)"],"duplicate_ids":[],"canonical_dialogue_tree":"","notes":"Created as a distinct identity. Quest fq_conc_001 explicitly self-identifies as Commander Lirien Vale; npc_concordium_officer remains Officer Valen and is not an alias."},
    {"canonical_id":"npc_arcanum_scholar","canonical_name":"Elara Voss","canonical_title":"High Seeker / Scholar Elara","faction":"THE_ARCANUM_SEEKERS","role":"QUEST_GIVER","aliases":["High Seeker Elara Voss","Scholar Elara"],"legacy_ids":["npc_high_seeker_voss"],"duplicate_ids":[],"canonical_dialogue_tree":"","notes":"Name and surname match the roster character Scholar Elara; use the roster ID as stable canonical ID."},
    {"canonical_id":"npc_warlord_harkon_steele","canonical_name":"Warlord Harkon Steele","canonical_title":"Iron Hegemony Warlord","faction":"IRON_HEGEMONY","role":"QUEST_GIVER","aliases":["Warlord Steele"],"legacy_ids":["npc_warlord_steele"],"duplicate_ids":[],"canonical_dialogue_tree":"","notes":"No matching roster identity found. Add a distinct NPC record; do not merge with the class trainer."},
    {"canonical_id":"npc_don_vercelli_mox","canonical_name":"Don Vercelli Mox","canonical_title":"Meridian Cartel Don","faction":"MERIDIAN_CARTEL","role":"QUEST_GIVER","aliases":["Don Mox"],"legacy_ids":["npc_don_mox"],"duplicate_ids":["NPC_NEXUS_QUESTGIVER_SMUGGLER"],"notes":"Roster character Revan 'Ghost' Mox has a different given name and role. Keep separate until source confirms kinship or alias."},
    {"canonical_id":"npc_omnicorp_class_trainer","canonical_name":"Director Astra Vey","canonical_title":"OmniCorp Combat Systems Instructor","faction":"OMNICORP","role":"CLASS_TRAINER","aliases":["Director Vey"],"legacy_ids":["npc_director_vey"],"duplicate_ids":[],"notes":"Exact canonical name match in the roster; preserve roster ID and migrate dialogue references through legacy_aliases."},
    {"canonical_id":"npc_elder_malakor","canonical_name":"Elder Malakor","canonical_title":"Shard Elder","faction":"CHILDREN_OF_THE_SHARD","role":"QUEST_GIVER","aliases":[],"legacy_ids":["npc_elder_malakor"],"duplicate_ids":[],"notes":"No matching roster identity found. Create a distinct NPC record; spiritual interpretation is character belief, not confirmed Aethel mechanics."},
    {"canonical_id":"npc_legion_class_trainer","canonical_name":"Centurion Valka","canonical_title":"Legion Combat Drillmaster","faction":"STARFORGED_LEGION","role":"CLASS_TRAINER","aliases":[],"legacy_ids":["npc_centurion_valka"],"duplicate_ids":[],"notes":"Exact name match in the roster; preserve stable roster ID and retain legacy ID mapping."},
]

GLOSSARY = [
    ("Aethel","energy","Energy born when fragments of the Aethel Shard resonated with Xylos's molten core.","A powerful energy associated with Xylos and its altered ecology.","The complete mechanism and any consciousness within it are not established canon.","UNKNOWN_TRUTH",1,"Keep explanations tied to observed effects."),
    ("Aethel Shard","artifact","A colossal crystalline asteroid that shattered on Xylos; its fragments remain embedded in the planet.","A source of Aethel fragments and a focus of religious and scientific claims.","Whether it has intention or a unified mind is not proven.","UNKNOWN_TRUTH",1,"Shard sentience claims remain belief or hypothesis."),
    ("Aethel Siphon","technology","Aethelgardian device that draws raw Aethel from Shard fragments; later repaired by the Concordium.","A damaged ancient system, repaired and operated by Concordium; its safety is politically contested.","The source lore says it overloaded during the Great Severance; current operation's full risk is unspecified.","FACT",2,"Do not treat every current disturbance as another overload without evidence."),
    ("Aethel Cradle","structure","A platform built around the Aethel Shard impact epicenter and housing the Siphon.","Ancient infrastructure at the heart of Nexus and planetary politics.","The full extent of lower systems remains unknown.","FACT",2,"Distinguish the ancient structure from Nexus's modern city."),
    ("Prima Materia","material","Rare substance refined from raw Aethel at the Aethel Forge.","A high-value catalyst, strategic resource, and source of faction conflict.","Its ultimate physical limits are not specified.","FACT",2,"NPCs may disagree over who should control it."),
    ("Great Severance","historical_event","Catastrophe caused when Aethelgardians pushed the Siphon beyond its limits, overloading it and shattering Shard fragments.","A civilization-ending event tied to dangerous Siphon use.","Individual mechanisms and culpability may remain disputed in-world.","FACT",1,"Separate from Great Schism."),
    ("Great Schism","political_event","Political split of the Concordium that gave rise to Arcanum Seekers, Iron Hegemony, and Meridian Cartel.","A later fracture in settler governance and faction politics.","Exact dates and individual responsibility are unspecified.","FACT",2,"Not the Great Severance."),
    ("Great Fracture","term_under_review","Used by Old Man Kael in roster dialogue; the supplied canon does not define it.","A local expression or historical claim of uncertain reference.","Whether it is a third event, nickname, or error is unresolved.","CANON_REVIEW_REQUIRED",0,"Retain as character terminology pending author decision."),
    ("Aethelgardians","people","Civilization that harnessed Aethel and built the Cradle, Siphon, Forge, and cities of Aethelgard.","An ancient civilization whose ruins and abandoned technology remain on Xylos.","Last descendants are said to live in hiding; specific identities are unknown.","FACT",2,"NPC accounts may be incomplete."),
    ("Cradle Expanse","location","Contested region around the ancient Aethel Cradle.","A hazardous frontier connected to old infrastructure and competing claims.","Detailed historical function beyond proximity to the Cradle is unclear.","FACT",3,"Use current map ID CRADLE_EXPANSE."),
    ("Nexus","settlement","Concordium capital built around the Aethel Cradle after the Siphon was repaired.","A major city and political center.","Claims of full control over the whole Cradle are contested by other factions.","FACT",1,"Do not equate Nexus with NEXUS_CORE region automatically."),
    ("Xylos","planet","A world in the Aethelgard System altered by Aethel Shard impact and later inhabited by settlers and off-world powers.","A scarred but inhabited planet rich in Aethel and ancient ruins.","The complete planetary history and Aethel's nature remain open.","FACT",1,""),
]

FACTIONS = {
"Concordium":("CONCORDIUM","Reconstruction, shared prosperity, order, public infrastructure, and regulated Aethel use.","Loss of authority, another Siphon catastrophe, and systems failing while bureaucracy stalls.","Formal institution, but civilians, scouts, officers, and administrators have different rhythms.","sector, line, protocol, restore, stabilize, record, deploy","An officer's bark as every voice; 'unity' as a cure-all."),
"Arcanum Seekers":("THE_ARCANUM_SEEKERS","Knowledge and discovery, even where caution becomes ethically costly.","Being wrong, constrained, or unable to understand Aethel.","Analytical curiosity; distinguish careful scholar, obsessive investigator, and reckless experimenter.","resonance, sample, hypothesis, evidence, pattern, observation","Mystical wizard affect; treating every experiment as justified."),
"Iron Hegemony":("IRON_HEGEMONY","Security through command, industry, discipline, and control of strategic resources.","Supply failure, fragmentation, and vulnerability caused by inflexible command.","Concrete, terse, workmanlike; workers and engineers can criticize command from inside.","forge, output, hold, pressure, armor, production","Constant shouting or reducing every problem to strength."),
"Meridian Cartel":("MERIDIAN_CARTEL","Influence through trade routes, relationships, information, and negotiated leverage.","Bad debts, broken networks, and losing control of a market they cannot command by force.","Socially observant with subtext; distinguish Don, broker, smuggler, and dock worker.","route, favor, debt, buyer, margin, leverage, insurance","Mentioning profit in every line or making all characters villains."),
"OmniCorp":("OMNICORP","Efficiency, proprietary technology, metrics, and return on investment.","Uncontrolled liability, lost assets, and the corporation abandoning people as costs.","Professional corporate language filtered through individual conviction, resentment, or fear.","asset, projection, compliance, allocation, performance, liability","Robotic delivery in every employee."),
"Children of the Shard":("CHILDREN_OF_THE_SHARD","Reverence, memory, ecology, and ending industrial harvesting.","Aethel being treated as inert property and the loss of sacred places.","Spiritual but varied: gentle, grieving, scholarly, political, or radical.","echo, memory, listen, wound, offering, return","Generic cult threats or claiming belief as objective fact."),
"Starforged Legion":("STARFORGED_LEGION","Survival, duty, lineage, disciplined defense, and earning a home.","Losing more people before they can settle, or tradition becoming a cage.","Ritual-aware, plainspoken, respectful of names and practical needs.","line, names, formation, standard, duty, endure","Repeating blood, glory, and honor as slogans."),
"Custodians":("CUSTODIANS","Prevent existential threats and protect sapient life under a mandate of galactic stability.","Neutrality becoming complicity, or intervention becoming domination.","Measured and procedural; individual Custodians may reveal moral strain.","authorization, threshold, containment, mandate, intervention","Omniscient arbiters with no personal doubt."),
"Aegis Monetary Authority":("AMA","Settlement integrity, currency stability, auditable exchange, and cross-faction trust.","Political capture, systemic contagion, and stability used to coerce.","Institutional neutral baseline with local vocabulary shaped by its host region.","ledger, reserve, settlement, liquidity, audit, rate","Behaving like a normal faction or pretending neutrality has no cost."),
"Neutral civilians":("NEUTRAL_CIVILIANS","Safety, food, family, reliable work, and access to a functioning route.","Being ignored by distant authorities or priced out of survival.","Specific local details, practical language, uneven knowledge.","shift, ration, route, shelter, price, family","Explaining faction doctrine like an official spokesperson."),
"Independent merchants":("INDEPENDENT_MERCHANTS","Keeping goods and relationships moving across unstable borders.","Confiscation, route closures, and debt to stronger powers.","Negotiating but not automatically Cartel-affiliated.","shipment, buyer, risk, credit, delay, favor","Treating all commerce as greed."),
"Scavengers":("SCAVENGERS","Survive by finding, repairing, and trading what the powerful leave behind.","Being mistaken for disposable or losing a hard-won claim.","Canny, concrete, attentive to salvage value and hazards.","usable, stripped, claim, scrap, patch, hazard","Making every scavenger a criminal."),
"Researchers":("RESEARCHERS","Understand local phenomena and prevent ignorance from driving catastrophe.","Bad data, restricted access, or consequences arriving before peer review.","Precise, curious, but marked by discipline and ethics.","reading, baseline, sample, anomaly, confidence","Universal consensus or exposition dumps."),
"Refugees":("REFUGEES","Find safety, reunite family, and regain control over ordinary choices.","Being moved, counted, or used as leverage again.","Personal and immediate, often cautious with strangers.","safe, missing, allowed, next, home","Using suffering only as atmosphere."),
"Workers":("WORKERS","Keep infrastructure and production running while protecting their crew.","Injury, unpaid risk, and leaders treating a shutdown as a statistic.","Trade knowledge and gallows humor; practical expertise.","shift, pressure, seal, jam, quota, break","Making them only background victims."),
}

def main():
    npcrefs = defaultdict(list)
    for dialog in QUEST_DIALOGS:
        npcrefs[dialog.get("npc_id")].append(dialog.get("quest_id"))
    npc_registry = []
    for npc in NPCS:
        tree = npc.get("dialogue_tree")
        npc_registry.append({**npc,
            "canonical_status": "CANONICAL" if tree in MASTER_BY_ID else "MISSING_DIALOGUE",
            "referenced_by_quests": sorted(set(npcrefs.get(npc["npc_id"], []))),
            "dialogue_exists": tree in MASTER_BY_ID,
            "identity_conflicts": [],
            "recommended_action": "Keep stable ID; add or repair its dialogue tree." if tree not in MASTER_BY_ID else "Retain identity and improve its individual voice."})
    write_json("23_updated_npc_list.json", {"source":"npc_list.json","records":npc_registry})
    write_json("02_npc_canonical_map.json", {"schema_version":1,"identities":IDENTITIES,"roster_registry":npc_registry})

    glossary=[]
    for term,kind,definition,public,unknown,status,stage,notes in GLOSSARY:
        glossary.append({"term":term,"type":kind,"canonical_definition":definition,"public_knowledge":public,"restricted_knowledge":unknown,"unknown_truth":unknown if status!="FACT" else "Further detail remains unspecified in supplied source lore.","faction_interpretations":{},"first_reveal_stage":stage,"status":status,"notes":notes})
    write_json("03_lore_glossary.json", {"canon_source":"Provided Xylos lore attachments; source details left open where unspecified.","terms":glossary})

    factions=[]
    for name,(code,worldview,fears,voice,vocab,avoid) in FACTIONS.items():
        factions.append(f"## {name}\n\n- Faction: `{code}`\n- Worldview: {worldview}\n- Fear: {fears}\n- Voice: {voice}\n- Vocabulary: {vocab}\n- Formality and rhythm: reflect role and relationship; use short directives for field roles, qualified sentences for analysts, and specific informal speech for civilians.\n- Humor: dry or situational, never a repeated faction catchphrase.\n- Threats: grounded in each speaker's authority and actual leverage.\n- Greeting / instructions: begin from current local need; give only actionable context.\n- Victory / failure: acknowledge material consequence and personal stake, not only player rank.\n- Avoid: {avoid}\n- Example: “The route is open for this shift. I still need two crews before I call it stable.”")
    write_text("04_faction_voice_bible.md", "# Faction Voice Bible\n\nFaction voice establishes a shared worldview; role, personality, and personal history shape each speaker. AMA uses an institutional baseline with local adaptation. Beliefs and rumors must not be presented as canon.\n\n"+"\n\n".join(factions))

    key_ids=["npc_concordium_officer","npc_director_hale","npc_concordium_overseer","npc_garden_scout","npc_patrol_guard","npc_veteran_explorer","npc_arcanum_scholar","npc_arcanum_archivist","npc_hegemony_commander","npc_blacksmith_ironhand","npc_cartel_boss","npc_shady_smuggler","npc_omnicorp_executive","npc_omnicorp_technician","npc_high_priest","npc_acolyte_mera","npc_legion_general","npc_drill_sergeant_korg","npc_custodian_ai","NPC_NEXUS_QUESTGIVER_ARBITER","NPC_NEXUS_BANKER_AMA7"]
    profiles=[]
    for npc_id in key_ids:
        npc=NPC_BY_ID.get(npc_id)
        if not npc: continue
        faction=npc.get("faction","NEUTRAL")
        profiles.append({"npc_id":npc_id,"name":npc.get("name"),"faction":faction,"role":npc.get("role"),"personality":npc.get("personality"),"core_motivation":f"Fulfill the duties of {npc.get('role','their role')} while protecting a personal stake in {npc.get('location','their home')}.","private_fear":"Infer only from established dialogue; otherwise leave for author review.","public_goal":npc.get("description",""),"personal_conflict":"Needs a source-backed conflict before dialogue reveals private history.","relationship_to_faction":f"Works within {faction}; individual views may diverge.","relationship_to_player_initial":"Unproven outsider; respond according to role and local risk.","speech_traits":[npc.get("personality","role-shaped voice"),npc.get("role","NPC role").lower()],"favorite_terms":[],"avoided_terms":[],"humor_style":"Set per character during authored dialogue; no default faction joke.","anger_style":"Sharper focus and less context; retain character-specific restraint.","trust_progression":["stranger","reliable contact","trusted collaborator"],"character_arc":["Initial public duty","Personal pressure revealed through actions","Changed stance after consequential player aid"]})
    write_json("05_character_voice_profiles.json", {"profiles":profiles,"coverage":"Major recurring roster NPCs; remaining roster entries are indexed in 02_npc_canonical_map.json for staged profiling."})

    write_text("06_dialogue_schema_documentation.md", "# Dialogue Schema Documentation\n\nProduction files use `dialog_quests.json` as `{ dialogues: [...] }`. Each quest dialogue contains `dialog_id`, `quest_id`, `npc_id`, `start_node`, and `nodes`. Nodes use `id`, `text`, and `options`; options use `text`, `next`, and optional `action`. NPC trees live in the segmented `dialog_tree_master.json` array. NPC records reference them through `dialogue_tree`.\n\nObserved production actions include `accept_quest` and `exit` in quest flows; master trees also use service actions such as `open_shop` and `currency_exchange`. No runtime implementation proving action idempotence or conditional state evaluation was found in this repository. Current import tooling stores node JSON without interpreting graph behavior.\n\nCompatibility rule: preserve existing IDs and service action strings. Keep state-aware conditions in a separate proposal until a runtime consumer is confirmed. An `exit` with no target node is presently ambiguous; for migrated pilot dialogues prefer an explicit terminal node and document that the app's close behavior must be confirmed.")
    proposal={"schema_version":"2-proposal","production_compatibility":"proposal only; do not import before runtime support exists","dialogues":[{"dialog_id":"","npc_id":"","quest_id":"","state":"AVAILABLE","conditions":[],"start_node":"greeting","nodes":[{"id":"greeting","speaker":"","text":"","conditions":[],"set_flags":[],"options":[{"text":"","next":"accept_confirmation","action":"","conditions":[],"set_flags":[]}]}]}],"states":["AVAILABLE","OFFERED","ACCEPTED","IN_PROGRESS","OBJECTIVE_PARTIAL","READY_TO_TURN_IN","COMPLETED","POST_COMPLETION","FAILED","OPTIONAL_REVISIT"],"condition_examples":["quest_completed:fq_conc_001","flag:FLAG_HELPED_CONCORDIUM_GARDENS","reputation:CONCORDIUM>=250"],"memory_note":"Requires runtime query for quest state, persistent player flags, and selected response flags."}
    write_json("07_dialogue_schema_v2_proposal.json",proposal)

    arc_specs={
      "concordium":("Concordium","reconstruction versus failing institutions","gardens and supply routes; civil quarter; Cradle authority; evidence of the Severance; Siphon stewardship","Keep Commander Vale's mission pressure distinct from Valen's security procedure, Hale's containment calculus, Vael's anxious logistics, Rian's observation, and the veteran's dry cost accounting."),
      "arcanum":("Arcanum Seekers","knowledge versus ethics","field anomaly; archive evidence; experimental pressure; contradictory records; cost of unrestricted access","Separate scholarly caution from obsessive leadership; discoveries remain hypotheses until corroborated."),
      "hegemony":("Iron Hegemony","survival versus authoritarian militarization","supply discipline; ravine production; salvaged machines; command dissent; strategic resource control","Give workers and engineers operational expertise and private criticism; not all Hegemony characters endorse command."),
      "meridian":("Meridian Cartel","opportunity versus exploitation","route protection; smuggler intelligence; dockside leverage; Aethel-era assets; market dependence","Show relationship management and information costs alongside trade; don't turn each exchange into a price joke."),
      "omnicorp":("OmniCorp","efficiency versus dehumanization","asset survey; extraction; grid security; reactor control; proprietary resource chain","Employees can believe in, resent, or fear the company; distinguish metrics from a human voice."),
      "children_of_shard":("Children of the Shard","spiritual truth versus fanaticism and interpretation","local ecology; wounded wetlands; fragment memory; internal disagreement; Great Purification","Keep theology as viewpoint; include grief, doubt, care, politics, and radicalism."),
      "starforged_legion":("Starforged Legion","tradition versus survival in a changing home","camp defense; scarce routes; settlement; command lineage; earned territory","Loss is personal because population is finite; honor is enacted through choices, not repeated slogans."),
      "custodians":("Custodians","neutrality versus moral responsibility","observe; assess mandate threshold; disagree about intervention; expose consequences; accept limits","Aethel activity is not automatically an existential threat; mandate and authority require evidence."),
    }
    for slug,(name,conflict,phases,voice) in arc_specs.items():
        write_text(f"faction_arc_{slug}.md",f"# {name} Narrative Arc\n\n## Central Conflict\n{conflict}.\n\n## Seven Acts\n\n1. **Introduction:** establish local need, speaker, and faction's practical presence.\n2. **Escalation:** first solution exposes a cost or fragile dependency.\n3. **Internal Contradiction:** a faction member challenges the official account.\n4. **Discovery:** present evidence with known limits; distinguish observation from interpretation.\n5. **Crisis:** a prior decision or neglected civilian consequence worsens the situation.\n6. **Faction Truth:** reveal a source-backed truth and one unresolved question.\n7. **Choice and Consequence:** show who benefits, who bears the cost, and how the character's stance changes.\n\n## Voice and Continuity\n{voice}\n\n## State Beats\nOffer dialogue states: available, accepted, in progress, ready to turn in, completed, and post-completion where runtime support exists. Record flags only in the schema proposal until the game implements them.\n\n## Quest Mapping\nUse the matching `fq_*` sequence in `dialog_quests.json`; keep current quest IDs and objectives. Author a distinct personal stake and story beat for each quest rather than recycling a faction lore paragraph.\n\n## Canon Limits\nGreat Severance is the Aethelgardian catastrophe; Great Schism is the later settler faction split. Great Fracture remains unresolved. Faction claims about Aethel intent remain belief or hypothesis.")
    write_text("faction_arc_ama.md","# Aegis Monetary Authority Narrative Layer\n\nAMA is a neutral financial institution, not a player faction. Its dialogue should retain a 70% institutional voice (settlement, audit, reserve, liquidity, rate integrity) and 30% host-region adaptation. Build conflict around neutrality under political pressure, counterfeit CRD, financial exclusion, and the possibility that stability tools can become coercive. Treat Credent as a universal currency described by supplied AMA lore; do not claim local quest hooks or policies beyond the data.")

    # Evidence-based baseline audit and migration record.
    missing_ids=Counter(d.get("npc_id") for d in QUEST_DIALOGS if d.get("npc_id") not in NPC_BY_ID)
    broken=[]; multi=0; quest_ref=Counter()
    for d in QUEST_DIALOGS:
        quest_ref[d.get("quest_id")]+=1
        ids={node.get("id") for node in d.get("nodes",[])}
        for node in d.get("nodes",[]):
            for op in node.get("options",[]):
                if op.get("next") and op["next"] not in ids and op.get("action") not in {"exit","open_shop","open_crafting","currency_exchange","open_banking","open_class_change","open_bounty","rest"}:
                    broken.append((d.get("dialog_id"),op.get("next")))
        multi+=sum(op.get("action")=="accept_quest" for node in d.get("nodes",[]) for op in node.get("options",[]))>1
    report=f"""# Dialogue Audit Report

Audit snapshot generated from current workspace files.

## Dataset

- NPC roster: {len(NPCS)} records.
- Quest dialogue: {len(QUEST_DIALOGS)} records ({sum(1 for d in QUEST_DIALOGS if d.get('quest_id','').startswith('fq_'))} faction quest and {sum(1 for d in QUEST_DIALOGS if not d.get('quest_id','').startswith('fq_'))} other quest dialogs).
- Current quest JSON records: {len(QUESTS)}.
- Master dialogue trees: {len(MASTER)} across {len(MASTER_BLOCKS)} legacy blocks; block sizes {[len(block.get('dialogues',[])) for block in MASTER_BLOCKS]}.
- Master metadata currently declares {next((b.get('meta',{}).get('quest_dialog_count') for b in MASTER_BLOCKS if b.get('meta')),None)} quest and {next((b.get('meta',{}).get('total_count') for b in MASTER_BLOCKS if b.get('meta')),None)} total trees; this is stale against source files.

## Confirmed Structural Findings

- {len(missing_ids)} quest dialogs reference missing NPC IDs across {len(missing_ids)} unique IDs: {', '.join(f'{key} ({value})' for key,value in sorted(missing_ids.items()))}.
- {sum(1 for npc in NPCS if npc.get('dialogue_tree') not in {d.get('dialog_id') for d in MASTER})} NPCs point to a tree absent from the master.
- {multi} quest dialogues contain multiple `accept_quest` actions; repository import code persists strings but does not establish idempotence.
- {len(broken)} non-terminal broken `next` references identified by direct graph inspection. The three `msq_lv*_reminder` references to `exit` have no declared terminal node.
- No duplicate quest dialog IDs, node IDs, or empty node texts were found in the current quest dialogue source.
- The master uses a legacy three-block array. Normalization must preserve all 31 existing NPC trees and compute metadata from the flattened result.

## Identity Decisions

- **Commander Lirien Vale vs Officer Valen:** keep distinct. Quest 001 contains explicit self-identification as Commander Lirien Vale, while roster defines Officer Valen. Create/retain distinct commander identity; reassign the erroneous first 20 dialogue references instead of renaming Officer Valen.
- **High Seeker Elara Voss:** map legacy `npc_high_seeker_voss` to `npc_arcanum_scholar` because the dialogue's full name matches the roster's Scholar Elara identity. Preserve the old ID as an alias.
- **Warlord Harkon Steele:** no roster match; create a separate NPC.
- **Don Vercelli Mox vs Revan “Ghost” Mox:** do not merge; distinct given names and no evidence of alias/kinship. Keep separate pending author confirmation.
- **Director Astra Vey:** map legacy `npc_director_vey` to roster `npc_omnicorp_class_trainer` based on exact full-name match; preserve legacy ID.
- **Elder Malakor:** no roster match; create a separate NPC.
- **Centurion Valka:** map legacy `npc_centurion_valka` to roster `npc_legion_class_trainer` based on exact name match; preserve legacy ID.

## Lore Classification

- Great Severance: established Aethelgardian Siphon overload catastrophe.
- Great Schism: later political split of Concordium leadership.
- Great Fracture: `CANON_REVIEW_REQUIRED`; only found as Old Man Kael wording in roster and not defined by the supplied canon.
- Meridian Cartel is the canonical faction name in faction data. “Meridian Compact” is not proven to be a historical predecessor; classify as a likely writing inconsistency and retain for author review before global replacement.
- Aethel Shard consciousness and any present-day deliberate intent are unresolved; dialogue may state them as belief or hypothesis only.

## Priorities

- **P0:** missing explicit `exit` targets in three level reminder dialogues; verify app terminal behavior before production migration.
- **P1:** seven missing quest giver identities, stale master metadata, and 85 NPC tree references.
- **P2:** repeated faction lore and quest acceptance actions; absent player-state responses.
- **P3:** individual voice variation and ambient civilian reactions.

## Limits

No dialogue runtime implementation was found in tracked app source; current import tooling stores JSON. State-aware conditions and flags therefore remain a proposal, not production fields. Great Fracture, Mox identity relationship, and the Meridian Compact label remain unresolved rather than invented.
"""
    write_text("01_dialogue_audit_report.md",report)
    write_text("22_dialogue_migration_log.md","# Dialogue Migration Log\n\n| Original | Changed / Decision | Reason | Affected IDs | Compatibility impact | Migration required? |\n|---|---|---|---|---|---|\n| `npc_concordium_officer` used for text introducing Commander Lirien Vale | Create distinct Commander Vale record; preserve Officer Valen | First-person identity conflicts with roster's distinct name and security role | `dialog_fq_conc_001` onward pending production update | Avoids changing existing Officer Valen ID | Yes, alias and dialogue reassignment |\n| Seven missing quest giver IDs | Canonical mappings documented in `02_npc_canonical_map.json` | Name evidence supports three aliases; Steele, Don Vercelli Mox, and Malakor require separate identities | faction quest dialogue IDs using those NPCs | Preserve old references as legacy aliases | Yes |\n| Master metadata 254/279 vs actual 701 + 31 | Mark stale; regenerate only after dialogue migration | Counts don't match source files | `dialog_tree_master.json` | Flatten legacy blocks carefully | Yes |\n| Multiple accept actions in each quest graph | Pilot convention: one final action after confirmation | Runtime idempotence is unverified | 701 quest dialogues | Retains same action name | Yes, after engine behavior review |\n| `Great Fracture` | Leave unresolved | Source does not define event | Old Man Kael dialogue | No canon change | No |\n| `Meridian Compact` | Flag as likely terminology error; no silent replacement | No evidence of historical organization | Concordium dialogue mentioning term | Avoids deleting possible lore | Author review before global edit |\n")

if __name__ == "__main__":
    main()
