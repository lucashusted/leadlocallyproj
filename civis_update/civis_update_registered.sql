WITH voters AS (
  SELECT intp_id
    , vb_tsmart_state as state_abbrev
    , vb_tsmart_county_code as fips -- instead of vb_tsmart_county_name just pull the code
    , CASE WHEN vb_voterbase_registration_status = 'Registered' THEN 1 ELSE 0 END AS registered
    , CASE WHEN vb_voterbase_age >= 18 AND vb_voterbase_age < 35 THEN '18-34'
           WHEN vb_voterbase_age >= 35 AND vb_voterbase_age < 64 THEN '35-64'
           WHEN vb_voterbase_age>=65 THEN '65+' END AS age_group
    , vb_voterbase_race AS race
    , ROW_NUMBER() OVER (PARTITION BY intp_id ORDER BY vb_vf_registration_date DESC) AS row_num
    , ts_tsmart_local_voter_score AS Local_Voter_Score
    , ts_tsmart_partisan_score AS Partisan_Score
    , ts_tsmart_presidential_general_turnout_score AS P_Turnout_Score
    , ts_tsmart_midterm_general_turnout_score AS M_Turnout_Score
    , ts_tsmart_offyear_general_turnout_score AS Offyear_M_Turnout_Score
    , ts_tsmart_presidential_primary_turnout_score AS PP_Turnout_Score
    , ts_tsmart_non_presidential_primary_turnout_score AS NonPP_Turnout_Score
    , ts_tsmart_climate_change_score AS Climate_Score
    , ts_tsmart_yale_climate_alarmed_score AS Yale_Score
    , ts_tsmart_biden_support_score AS Biden_Support_Score
  FROM ts.ntl_current
  WHERE intp_id IS NOT NULL
    AND age_group IS NOT NULL
    AND race IS NOT NULL
  )
  SELECT state_abbrev
    , fips
    , age_group
    , race
    , SUM(registered) AS registered
  FROM voters
  WHERE row_num = 1
  GROUP BY 1,2,3,4;
