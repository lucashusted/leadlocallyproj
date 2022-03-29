SELECT vb_tsmart_state as State,
    vb_tsmart_county_code as Fips, -- instead of vb_tsmart_county_name just pull the code
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' THEN 1 ELSE 0 END) as Civis_Registered_Count,
    sum(CASE WHEN vb_voterbase_registration_status = 'Unregistered' THEN 1 ELSE 0 END) as Civis_Unregistered_Count,

    count(vb_vf_g2020) as Total_G2020_Count,
    count(vb_vf_m2020) as Total_M2020_Count,

    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_p2020_party = 'D' THEN 1 ELSE 0 END) as Dem_P20_Voter_Count,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_p2020_party = 'R' THEN 1 ELSE 0 END) as Rep_P20_Voter_Count,
    sum(CASE WHEN vb_vf_p2020_party IS NULL THEN 1 ELSE 0 END) as P20_No_Party_Data,

    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_pp2020_party = 'D' THEN 1 ELSE 0 END) as Dem_PP20_Voter_Count,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_pp2020_party = 'R' THEN 1 ELSE 0 END) as Rep_PP20_Voter_Count,
    sum(CASE WHEN vb_vf_pp2020_party IS NULL THEN 1 ELSE 0 END) as PP20_No_Party_Data,

    count(vb_vf_g2019) as Total_G2019_Count,
    count(vb_vf_m2019) as Total_M2019_Count,

    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_p2019_party = 'D' THEN 1 ELSE 0 END) as Dem_P19_Voter_Count,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_p2019_party = 'R' THEN 1 ELSE 0 END) as Rep_P19_Voter_Count,
    sum(CASE WHEN vb_vf_p2019_party IS NULL THEN 1 ELSE 0 END) as P19_No_Party_Data,

    count(vb_vf_g2018) as Total_G2018_Count,
    count(vb_vf_m2018) as Total_M2018_Count,

    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_p2018_party = 'D' THEN 1 ELSE 0 END) as Dem_P18_Voter_Count,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_p2018_party = 'R' THEN 1 ELSE 0 END) as Rep_P18_Voter_Count,
    sum(CASE WHEN vb_vf_p2018_party IS NULL THEN 1 ELSE 0 END) as P18_No_Party_Data,

    count(vb_vf_g2017) as Total_M2017_Count,
    count(vb_vf_m2017) as Total_M2017_Count,

    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_p2017_party = 'D' THEN 1 ELSE 0 END) as Dem_P17_Voter_Count,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_p2017_party = 'R' THEN 1 ELSE 0 END) as Rep_P17_Voter_Count,
    sum(CASE WHEN vb_vf_p2017_party IS NULL THEN 1 ELSE 0 END) as P17_No_Party_Data,

    count(vb_vf_g2016) as Total_G2016_Count,
    count(vb_vf_m2016) as Total_M2016_Count,

    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_p2016_party = 'D' THEN 1 ELSE 0 END) as Dem_P16_Voter_Count,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_p2016_party = 'R' THEN 1 ELSE 0 END) as Rep_P16_Voter_Count,
    sum(CASE WHEN vb_vf_p2016_party IS NULL THEN 1 ELSE 0 END) as P16_No_Party_Data,

    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_pp2016_party = 'D' THEN 1 ELSE 0 END) as Dem_PP16_Voter_Count,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_pp2016_party = 'R' THEN 1 ELSE 0 END) as Rep_PP16_Voter_Count,
    sum(CASE WHEN vb_vf_pp2016_party IS NULL THEN 1 ELSE 0 END) as PP16_No_Party_Data,

    count(vb_vf_g2015) as Total_G2015_Count,
    count(vb_vf_m2015) as Total_M2015_Count,

    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_p2015_party = 'D' THEN 1 ELSE 0 END) as Dem_P15_Voter_Count,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_p2015_party = 'R' THEN 1 ELSE 0 END) as Rep_P15_Voter_Count,
    sum(CASE WHEN vb_vf_p2015_party IS NULL THEN 1 ELSE 0 END) as P15_No_Party_Data,

    count(vb_vf_g2014) as Total_G2014_Count,
    count(vb_vf_m2014) as Total_M2014_Count,

    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_p2014_party = 'D' THEN 1 ELSE 0 END) as Dem_P14_Voter_Count,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_p2014_party = 'R' THEN 1 ELSE 0 END) as Rep_P14_Voter_Count,
    sum(CASE WHEN vb_vf_p2014_party IS NULL THEN 1 ELSE 0 END) as P14_No_Party_Data,

    count(vb_vf_g2013) as Total_G2013_Count,
    count(vb_vf_m2013) as Total_M2013_Count,

    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_p2013_party = 'D' THEN 1 ELSE 0 END) as Dem_P13_Voter_Count,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_p2013_party = 'R' THEN 1 ELSE 0 END) as Rep_P13_Voter_Count,
    sum(CASE WHEN vb_vf_p2013_party IS NULL THEN 1 ELSE 0 END) as P13_No_Party_Data,

    count(vb_vf_g2012) as Total_G2012_Count,
    count(vb_vf_m2012) as Total_M2012_Count,

    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_pp2012_party = 'D' THEN 1 ELSE 0 END) as Dem_P12_Voter_Count,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_pp2012_party = 'R' THEN 1 ELSE 0 END) as Rep_P12_Voter_Count,
    sum(CASE WHEN vb_vf_pp2012_party IS NULL THEN 1 ELSE 0 END) as P12_No_Party_Data,

    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_p2012_party = 'D' THEN 1 ELSE 0 END) as Dem_PP12_Voter_Count,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_p2012_party = 'R' THEN 1 ELSE 0 END) as Rep_PP12_Voter_Count,
    sum(CASE WHEN vb_vf_p2012_party IS NULL THEN 1 ELSE 0 END) as PP12_No_Party_Data,

    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_p2012_party = 'D' THEN 1 ELSE 0 END) as Dem_PP12_Voter_Count,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_vf_p2012_party = 'R' THEN 1 ELSE 0 END) as Rep_PP12_Voter_Count,
    sum(CASE WHEN vb_vf_p2012_party IS NULL THEN 1 ELSE 0 END) as PP12_No_Party_Data,

    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_voterbase_age >= 18 AND vb_voterbase_age < 35 AND vb_voterbase_race = 'African-American' THEN 1 ELSE 0 END) as Registered_African_Americans_18_34,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_voterbase_age >= 35 AND vb_voterbase_age < 65 AND vb_voterbase_race = 'African-American' THEN 1 ELSE 0 END) as Registered_African_Americans_35_64,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_voterbase_age >= 65 AND vb_voterbase_race = 'African-American' THEN 1 ELSE 0 END) as Registered_African_Americans_65,
    Registered_African_Americans_18_34+Registered_African_Americans_35_64+Registered_African_Americans_65 as Registered_African_Americans_Total,

    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_voterbase_age >= 18 AND vb_voterbase_age < 35 AND vb_voterbase_race = 'Asian' THEN 1 ELSE 0 END) as Registered_Asians_18_34,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_voterbase_age >= 35 AND vb_voterbase_age < 65 AND vb_voterbase_race = 'Asian' THEN 1 ELSE 0 END) as Registered_Asians_35_64,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_voterbase_age >= 65 AND vb_voterbase_race = 'Asian' THEN 1 ELSE 0 END) as Registered_Asians_65,
    Registered_Asians_18_34+Registered_Asians_35_64+Registered_Asians_65 as Registered_Asians_Total,

    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_voterbase_age >= 18 AND vb_voterbase_age < 35 AND vb_voterbase_race = 'Caucasian' THEN 1 ELSE 0 END) as Registered_CaucAsians_18_34,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_voterbase_age >= 35 AND vb_voterbase_age < 65 AND vb_voterbase_race = 'Caucasian' THEN 1 ELSE 0 END) as Registered_CaucAsians_35_64,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_voterbase_age >= 65 AND vb_voterbase_race = 'Caucasian' THEN 1 ELSE 0 END) as Registered_CaucAsians_65,
    Registered_CaucAsians_18_34+Registered_CaucAsians_35_64+Registered_CaucAsians_65 as Registered_CaucAsians_Total,

    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_voterbase_age >= 18 AND vb_voterbase_age < 35 AND vb_voterbase_race = 'Hispanic' THEN 1 ELSE 0 END) as Registered_Hispanics_18_34,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_voterbase_age >= 35 AND vb_voterbase_age < 65 AND vb_voterbase_race = 'Hispanic' THEN 1 ELSE 0 END) as Registered_Hispanics_35_64,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_voterbase_age >= 65 AND vb_voterbase_race = 'Hispanic' THEN 1 ELSE 0 END) as Registered_Hispanics_65,
    Registered_Hispanics_18_34 +Registered_Hispanics_35_64+Registered_Hispanics_65 as Registered_Hispanics_Total,

    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_voterbase_age >= 18 AND vb_voterbase_age < 35 AND vb_voterbase_race = 'Native American' THEN 1 ELSE 0 END) as Registered_Native_Americans_18_34,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_voterbase_age >= 35 AND vb_voterbase_age < 65 AND vb_voterbase_race = 'Native American' THEN 1 ELSE 0 END) as Registered_Native_Americans_35_64,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_voterbase_age >= 65 AND vb_voterbase_race = 'Native American' THEN 1 ELSE 0 END) as Registered_Native_Americans_65,
    Registered_Native_Americans_18_34+Registered_Native_Americans_35_64+Registered_Native_Americans_65 as Registered_Native_Americans_Total,

    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_voterbase_age >= 18 AND vb_voterbase_age < 35 AND vb_voterbase_race = 'Other' THEN 1 ELSE 0 END) as Registered_Other_Race_18_34,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_voterbase_age >= 35 AND vb_voterbase_age < 65 AND vb_voterbase_race = 'Other' THEN 1 ELSE 0 END) as Registered_Other_Race_35_64,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_voterbase_age >= 65 AND vb_voterbase_race = 'Other' THEN 1 ELSE 0 END) as Registered_Other_Race_65,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_voterbase_age >= 18 AND vb_voterbase_age < 35 AND vb_voterbase_race = 'Uncoded' THEN 1 ELSE 0 END) as Registered_Uncoded_Race_18_34,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_voterbase_age >= 35 AND vb_voterbase_age < 65 AND vb_voterbase_race = 'Uncoded' THEN 1 ELSE 0 END) as Registered_Uncoded_Race_35_64,
    sum(CASE WHEN vb_voterbase_registration_status = 'Registered' AND vb_voterbase_age >= 65 AND vb_voterbase_race = 'Uncoded' THEN 1 ELSE 0 END) as Registered_Uncoded_Race_65,

    Registered_Other_Race_18_34+Registered_Uncoded_Race_18_34 as registered_other_and_uncoded_race_18_34,
    Registered_Other_Race_35_64+Registered_Uncoded_Race_35_64 as registered_other_and_uncoded_race_35_64,
    Registered_Other_Race_65+Registered_Uncoded_Race_65 as registered_other_and_uncoded_race_65,
    registered_other_and_uncoded_race_18_34+registered_other_and_uncoded_race_35_64+registered_other_and_uncoded_race_65 as Registered_Other_and_Uncoded_Race_Total,

    Registered_African_Americans_18_34+Registered_Asians_18_34+Registered_CaucAsians_18_34+Registered_Hispanics_18_34+Registered_Native_Americans_18_34+Registered_Other_Race_18_34+Registered_Uncoded_Race_18_34 as Registered_18_34_Total,
    Registered_African_Americans_35_64+Registered_Asians_35_64+Registered_CaucAsians_35_64+Registered_Hispanics_35_64+Registered_Native_Americans_35_64+Registered_Other_Race_35_64+Registered_Uncoded_Race_35_64 as Registered_35_64_Total,
    Registered_African_Americans_65+Registered_Asians_65+Registered_CaucAsians_65+Registered_Hispanics_65+Registered_Native_Americans_65+Registered_Other_Race_65+Registered_Uncoded_Race_65 as Registered_65_Total,

    avg(ts_tsmart_local_voter_score) as Avg_Local_Voter_Score,
    avg(ts_tsmart_partisan_score) as Avg_Partisan_Score,
    avg(ts_tsmart_presidential_general_turnout_score) as Avg_P_Turnout_Score,
    avg(ts_tsmart_midterm_general_turnout_score) as Avg_M_Turnout_Score,
    avg(ts_tsmart_offyear_general_turnout_score) as Avg_Offyear_M_Turnout_Score,
    avg(ts_tsmart_presidential_primary_turnout_score) as Avg_PP_Turnout_Score,
    avg(ts_tsmart_non_presidential_primary_turnout_score) as Avg_NonPP_Turnout_Score,
    avg(ts_tsmart_climate_change_score) as Avg_Climate_Score,
    avg(ts_tsmart_yale_climate_alarmed_score) as Avg_Yale_Score,
    avg(ts_tsmart_biden_support_score) as Avg_Biden_Support_Score

FROM ts.ntl_current
GROUP BY 1,2
ORDER BY 1,2
