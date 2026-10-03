# Blind data schema — beta.6

CSV inclusi nel pacchetto:

- `blind_sessions.csv`: session_id, group_id, date, build, scenario, num_players, gm_experience, group_experience, minutes_to_first_roll, minutes_character_setup, consultations_total, consultations_unresolved, interest_continue_yes, interest_continue_total, notes
- `blind_consultations.csv`: session_id, event_id, rule, page, seconds, found, applied_correctly, critical_ambiguity, notes
- `blind_risonanza.csv`: session_id, event_id, character, initial_band, two_valid_prices, price1_category, price2_category, accepted, accepted_category, seconds_to_offer, price_followed_up, notes
- `blind_combats.csv`: session_id, combat_id, rounds, pc_hp_lost_total, healing_total, enemy_significant_actions, resolution, num_players, notes
- `blind_rule_cases.csv`: session_id, case_id, correct, seconds, interpretation, notes
- `blind_issues.csv`: issue_id, session_id, severity, type, page_section, description, interpretation_used, recurring, proposed_fix

Usare un solo `session_id` per ogni sessione reale. Non duplicare lo stesso evento fra file diversi salvo le chiavi necessarie al collegamento.
