import json

def remove_duplicate_names(input_filename="input.json", output_filename="output.json"):
    """
    Reads a JSON file, removes duplicate entries based on the 'name' field,
    and writes the unique entries to a new JSON file.

    Args:
        input_filename (str, optional): The name of the input JSON file.
                                         Defaults to "input.json".
        output_filename (str, optional): The name of the output JSON file.
                                          Defaults to "output.json".
    """
    try:
        with open(input_filename, 'r') as infile:
            data = json.load(infile)
    except FileNotFoundError:
        print(f"Error: Input file '{input_filename}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{input_filename}'.")
        return

    seen_names = set()
    unique_entries = []

    for entry in data:
        if "name" in entry:
            if entry["name"] not in seen_names:
                unique_entries.append(entry)
                seen_names.add(entry["name"])
        else:
            print("Warning: Entry found without a 'name' field and was not included in the output.")

    try:
        with open(output_filename, 'w') as outfile:
            json.dump(unique_entries, outfile, indent=2)
        print(f"Successfully processed '{input_filename}' and wrote unique entries to '{output_filename}'.")
    except IOError:
        print(f"Error: Could not write to output file '{output_filename}'.")

def count_entries_in_json(filename):
    """
    Counts the number of entries (top-level elements) in a JSON file.  Handles
    potential errors like file not found and invalid JSON.

    Args:
        filename (str): The name of the JSON file to read.

    Returns:
        int: The number of entries in the JSON file, or 0 if an error occurs.
             Returns 0 and prints an error message to the console if the file
             does not exist or contains invalid JSON.
    """
    try:
        with open(filename, 'r') as f:
            data = json.load(f)  # Load the entire JSON content
            if isinstance(data, list):
                return len(data) # Returns the number of top-level elements if JSON is a list
            elif isinstance(data, dict):
                return len(data) # Returns the number of top-level elements if JSON is a dict
            else:
                print(f"Error: JSON file '{filename}' does not contain a list or dictionary at the top level.")
                return 0

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return 0
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file '{filename}'.")
        return 0
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return 0

# def change_preference_attribute(filename="output.json"):  # Added filename argument with default value
#     """
#     Changes the 'Preference' attribute to 'preference' in the JSON data
#     within the specified file.  Handles potential file errors.

#     Args:
#         filename (str): The name of the JSON file to modify.
#                         Defaults to "your_file.json".
#     """
#     try:
#         with open(filename, 'r') as file:
#             data = json.load(file)  # Load the JSON data
#     except FileNotFoundError:
#         print(f"Error: File not found at {filename}")
#         return  # Exit the function if the file doesn't exist
#     except json.JSONDecodeError:
#         print(f"Error: Invalid JSON format in {filename}")
#         return  # Exit if the JSON is invalid

#     # Check if the file contains a list of dictionaries or a single dictionary
#     if isinstance(data, list):
#         for item in data:
#             if "Preference" in item:
#                 item["preference"] = item.pop("Preference")  # Rename the key
#     elif isinstance(data, dict):
#         if "Preference" in data:
#             data["preference"] = data.pop("Preference")  # Rename the key
#     else:
#         print(f"Error: The JSON file should contain either a list of dictionaries or a dictionary, found {type(data)}.")
#         return

#     try:
#         with open(filename, 'w') as file:
#             json.dump(data, file, indent=4)  # Write the modified JSON back with indent
#         print(f"Successfully changed 'Preference' to 'preference' in {filename}")
#     except Exception as e:
#         print(f"Error writing to {filename}: {e}")


if __name__ == "__main__":
    remove_duplicate_names(input_filename="./data/foodOptions_with_descriptionsAll.json", output_filename="./data/foodOptions_with_descriptionsWithoutDuplicates.json")
    count_entries = count_entries_in_json("./data/foodOptions_with_descriptionsWithoutDuplicates.json")
    print(count_entries)
    
