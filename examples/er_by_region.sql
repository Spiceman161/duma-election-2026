-- Ordinary party-list ballots only; geographic coverage is not a filter.
SELECT p.region_name,
       SUM(r.votes) AS er_votes,
       SUM(p.valid_ballots + p.invalid_ballots) AS ballots,
       100.0 * SUM(r.votes) /
       NULLIF(SUM(p.valid_ballots + p.invalid_ballots), 0) AS er_percent
FROM protocols AS p
JOIN party_results AS r USING (protocol_key)
WHERE p.dataset = 'uik'
  AND p.ballot_type = 'party_list'
  AND r.party_id LIKE '%edinaya-rossiya%'
GROUP BY p.region_name;
