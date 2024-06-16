from dotenv import load_dotenv
from dateutil.parser import parse
import re
import os

# Manually Removed June 2024 connections as the formatting got a bit messed up from the scrape 
# Manually Removed APRIL 1, 2024 because it was april fools so it was done in Emojis

#Remove a few duplicate rows that were pulled in from the web scrape 
def remove_dupes():

    # Load environment variables from .env file
    load_dotenv()
    # Get the file paths from environment variables
    raw_data_location = os.getenv('raw_data_path')
    clean_data_location = os.getenv('clean_data_path')

    # Read the contents of the existing file
    with open(raw_data_location, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Create a list to store unique lines
    unique_lines = []
    separator = "--------------------"

    # Loop through the lines and add unique lines to the unique_lines list
    for line in lines:
        if line.strip() == separator:
            # Separator line, add it to unique_lines
            unique_lines.append(line)
        elif line not in unique_lines:
            # Unique line, add it to unique_lines
            unique_lines.append(line)

    # Write the unique lines to a new file
    with open(clean_data_location, "w", encoding="utf-8") as file:
        file.writelines(unique_lines)

    print(f"Data with no duplicates written to {clean_data_location}")

# Converts the deduped text file into a clean csv 
# Each line contains Date, Difficulty, Category, Word
# Each connections date will be comprised of 16 lines
def export_csv():
    # Load environment variables from .env file
    load_dotenv()
    data_file = os.getenv('clean_data_path')
    output_file = os.getenv('clean_csv')

    # Define regular expressions for parsing
    date_pattern = re.compile(r"Date: (\w+\s\d+,\s\d+)")
    category_pattern = re.compile(r"(🟡|🟢|🔵|🟣)\s(.*?):")
    word_pattern = re.compile(r"([\w\s']+)")

    # Open the input and output files
    with open(data_file, "r", encoding="utf-8") as input_file, open(output_file, "w", encoding="utf-8", newline="") as output_file:
        # Write the CSV header
        output_file.write("Date,Difficulty,Category,Word\n")

        # Process each entry in the input file
        for line in input_file:
            line = line.strip()

            # Check if the line is a date
            date_match = date_pattern.match(line)
            if date_match:
                # Parse the date and convert it to the desired format yyyy-mm-dd to be interpretted by duckdb
                date_str = date_match.group(1).replace(",", "")
                date_obj = parse(date_str)
                date = date_obj.strftime("%Y-%m-%d")

            # Check if the line is a category
            category_match = category_pattern.match(line)
            if category_match:
                difficulty = category_match.group(1)
                category = category_match.group(2).replace(",", "")
                words = word_pattern.findall(line.split(":")[1])
                # Strip words to remove any excess spaces
                for word in words:
                    if difficulty == "🟡":
                        output_file.write(f"{date},Easiest,{category},{word.strip()}\n")
                    elif difficulty == "🟢":
                        output_file.write(f"{date},Easy,{category},{word.strip()}\n")
                    elif difficulty == "🔵":
                        output_file.write(f"{date},Medium,{category},{word.strip()}\n")
                    elif difficulty == "🟣":
                        output_file.write(f"{date},Hard,{category},{word.strip()}\n")

