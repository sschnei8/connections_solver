# %%
import duckdb

# Now we can derive some summary stats about historical conenctions
conn = duckdb.connect("connections.db")

############################################################################################################
# Taking the modulo of the count we see some words like YO-YO and FLIP-FLOP have been split into two lines
# There's ~5 instances, so manually removing and recreating table in connections.db
############################################################################################################
print(conn.execute(
"""
SELECT GAME_DATE
     , CATEGORY
     , COUNT(1) / 4::FLOAT AS CNT -- BECASUE THERE WILL BE 4 ROWS FOR EACH INSTANCE
FROM CONNECTIONS_DATA
GROUP BY 1,2
HAVING CNT % 1 <> 0
ORDER BY CNT DESC
"""
).df()
)
# %%
# Now we can derive some summary stats about historical conenctions
conn = duckdb.connect("connections.db")

def query(sqltext:str):
    print(conn.execute(sqltext).df())


##################################################################
# A Few summary stats describing the table
# 5360 words, 1340 connections, and 335 days of data
##################################################################
#query(
"""
SELECT COUNT(1) AS TOTAL_WORDS
     , COUNT(1) / 4::FLOAT AS TOTAL_DISTINCT_CONNECTIONS
     , COUNT(1) / 16::FLOAT AS TOTAL_DISTINCT_DAYS
FROM CONNECTIONS_DATA
"""
#)


###################################################################################################
# 2023-08-30 AND 2024-05-30 had the same influence connection
# 2024-01-11, 2023-07-25, and 2023-08-15 had the same states of matter connection
# Because in the scrape I remove duplicate lines these were removed because they are dupes 
###################################################################################################
query(
"""
SELECT GAME_DATE
     , COUNT(1) CNT
FROM CONNECTIONS_DATA
GROUP BY 1
HAVING CNT % 16 <> 0
"""
)


#####################################################################################################################
# Most repeating words
# 8 words have appeared > 7 times with RING & BALL occuring the most at 10 times 
# RING:10,  BALL:10,  COPY:9,  LEAD:9,  WING:8,  JACK:8,   CUT:8, HEART:8    
# Of the 3508 distinct words, 1069 have occurred more than once 
#####################################################################################################################
#query(
"""
SELECT WORD
     , COUNT(1) CNT
FROM CONNECTIONS_DATA
GROUP BY 1
HAVING CNT > 1
ORDER BY CNT DESC
"""
#)

#####################################################################################################################
# Most Common Length of words
# 1. Check against all words including repeats 
# 2. Remove repeat words and group by length 
# 4 and 5 letter words most common making up > 50% of all words 
# Longest "Word" was PEPPERMINT PATTY (16 letters) on 2023-09-16
# Some other long 13 letter words: ROLLING STONE, CONCENTRATION, MASHED POTATO, and HORSEFEATHERS
# Some "words" are single letters like "X" representing Kiss
# Fairly rarely do the words have spaces < 30 occurences
# Word length is steady across all difficulties at ~ 5.1 letters per word
#####################################################################################################################
#query(
"""
SELECT WORD
     , LENGTH(WORD) WORD_LENGTH
     , COUNT(1) CNT
FROM CONNECTIONS_DATA
WHERE WORD_LENGTH = 13
GROUP BY 1,2
ORDER BY CNT DESC
"""
#)

#query(
"""
WITH WORD_CNT AS (
SELECT WORD
     , LENGTH(WORD) WORD_LENGTH
FROM CONNECTIONS_DATA
GROUP BY 1,2
)

SELECT WORD_LENGTH
     , COUNT(1) CNT
FROM WORD_CNT
GROUP BY 1
ORDER BY CNT DESC
"""
#)

#query(
"""
SELECT COUNT(1) CNT
FROM CONNECTIONS_DATA
WHERE WORD ILIKE '% %'
"""
#)

#query(
"""
SELECT DIFFICULTY
     , LENGTH(WORD) WORD_LENGTH
     , COUNT(1) CNT
FROM CONNECTIONS_DATA
GROUP BY 1,2
ORDER BY DIFFICULTY, CNT DESC
"""
#)

#query(
"""
WITH DIFF_CNT AS (
SELECT DIFFICULTY
     , LENGTH(WORD) WORD_LENGTH
     , COUNT(1) CNT
FROM CONNECTIONS_DATA
GROUP BY 1,2
)

SELECT DIFFICULTY
     , SUM(WORD_LENGTH * CNT) / NULLIF(SUM(CNT)::FLOAT, 0) AS AVG_LENGTH  
FROM DIFF_CNT
GROUP BY 1
"""
#)

#####################################################################################################################
# To actually view the number of occurences we can parse any catagory containing the string
# Now we see the true occurences, 16x for Homophones and 4x for Anagrams
# When these occur they are nearly always the Hard connection grouping  
#####################################################################################################################
#query(
"""
SELECT DIFFICULTY
     , SUM(CASE WHEN CATEGORY ILIKE '%HOMOPHONE%' THEN 1 ELSE 0 END) / 4::FLOAT AS HOMOPHONE_CNT 
     , SUM(CASE WHEN CATEGORY ILIKE '%ANAGRAM%' THEN 1 ELSE 0 END) / 4::FLOAT AS ANAGRAM_CNT 
FROM CONNECTIONS_DATA
WHERE CATEGORY ILIKE '%HOMOPHONE%' OR CATEGORY ILIKE '%ANAGRAM%'
GROUP BY 1
"""
#)

###############################################################################################################################
# Another common connection is grouping based on prefix or suffix 
# In the data set, they are mostly denoted by several dunders, EX: PLAY ___ and rarely by explicitely stating suffix or prefix
# This should work to pick up the dunders: LIKE '%\\___%', but it doesnt in duckdb... so using some length logic to parse them
# Out of 1340 connections obviously 25% of them are hard (335 instances). Of those 335, 134 are either our dunderscores or prefixes
# It will be critical to note when solving the hardest connections problems that over 40% of the time they are this prefix/suffix pattern
# There are 140 total occurences of dunder, prefix, and suffix with nearly all of them occuring in the hardest grouping
# There are another 9 additional occurences of words MINUS just their last letter, these are always hard
# Another common hard grouping involves "WITH", Example: WORDS WITH “HILL” -> CAPITOL these occur 63 times and are mostly hard ~65% but sometimes easy
# PARTS shows up across the easiest to the hardest with categories like FOOT PARTS being easiest and GUITAR PARTS being HARD
# THINGS Shows up a lot these are nearly always Hard or Medium and involve: THINGS WITH SLOTS -> ATM, THINGS THAT MIGHT STINK -> CHEESE
###############################################################################################################################
#query(
"""
SELECT Difficulty
     , SUM(CASE WHEN LENGTH(CATEGORY) - LENGTH(REPLACE(CATEGORY, '_', '')) >= 2 THEN 1 ELSE 0 END) / 4::FLOAT AS DUNDERSCORES
     , SUM(CASE WHEN CATEGORY ILIKE '%PREFIX%' THEN 1 ELSE 0 END) / 4::FLOAT AS PREFIX_STRING
     , SUM(CASE WHEN CATEGORY ILIKE '%SUFFIX%' THEN 1 ELSE 0 END) / 4::FLOAT AS SUFFIX_STRING
     , SUM(CASE WHEN CATEGORY ILIKE '%MINUS%' THEN 1 ELSE 0 END) / 4::FLOAT AS MINUS
     , SUM(CASE WHEN CATEGORY ILIKE '%ADDED%' OR CATEGORY ILIKE '% PLUS%' THEN 1 ELSE 0 END) / 4::FLOAT AS ADDED_PLUS     
     , SUM(CASE WHEN CATEGORY ILIKE '%WITH%' THEN 1 ELSE 0 END) / 4::FLOAT AS WITH     
     , SUM(CASE WHEN CATEGORY ILIKE '%PARTS%' THEN 1 ELSE 0 END) / 4::FLOAT AS PARTS     
     , SUM(CASE WHEN CATEGORY ILIKE '%THINGS%' THEN 1 ELSE 0 END) / 4::FLOAT AS THINGS    
     , SUM(CASE WHEN CATEGORY ILIKE '%HOMOPHONE%' THEN 1 ELSE 0 END) / 4::FLOAT AS HOMOPHONE_CNT 
     , SUM(CASE WHEN CATEGORY ILIKE '%ANAGRAM%' THEN 1 ELSE 0 END) / 4::FLOAT AS ANAGRAM_CNT 
FROM CONNECTIONS_DATA
WHERE LENGTH(CATEGORY) - LENGTH(REPLACE(CATEGORY, '_', '')) >= 2 
  OR CATEGORY ILIKE '%PREFIX%' 
  OR CATEGORY ILIKE '%SUFFIX%'
  OR CATEGORY ILIKE '%MINUS%'
  OR CATEGORY ILIKE '%ADDED%'
  OR CATEGORY ILIKE '% PLUS%'
  OR CATEGORY ILIKE '%WITH%'
  OR CATEGORY ILIKE '%PARTS%'
  OR CATEGORY ILIKE '%THINGS%'
  OR CATEGORY ILIKE '%HOMOPHONE%'
  OR CATEGORY ILIKE '%ANAGRAM%'
GROUP BY 1
"""
#)


# %%
