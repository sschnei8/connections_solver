#%%
import scrape
import transform
import create_db

 # Write Twelve Months of Connections data to text file 
for i in range(1, 13):
    scrape.scrape_connections(i)

# Remove Duplicate lines 
transform.remove_dupes()

#Write to CSV
transform.export_csv()

# DuckDB DB creationa and load table
create_db.db_and_table()

# Delete from table where my Extract/Transform logic sucked *Shrug* [Removes 9 days of 335]
create_db.clean_table()


# %%
