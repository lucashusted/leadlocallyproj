Here are the steps to update the data:
1. Go to https://platform.civisanalytics.com and run the SQL query to pull any new CIVIS data on the number of registered voters by county. Save output as civis_data.csv  Two notes:
	- You should go to Data>Scripts (Under Exports) to get the output as a .csv file
	- You should use Safari or Chrome (Firefox leads to errors)

2. Run two files in the dialog box:
	- civis_update_registered.sql updates the number of registered voters per county
	- civis_update_countyscores.sql updates the scores by county along the various dimensions.

3. Put the files in here, name them respectively:
	- civis_registered.csv
	- civis_scores.csv

4. Run clean_civis.py, it will spit out:
	- civis_scores_cleaned.csv
	- civis_registration_totals.csv

