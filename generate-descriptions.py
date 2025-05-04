import json
import time
import logging
import vertexai
from langchain_google_vertexai import VertexAI
from tenacity import retry, stop_after_attempt, wait_exponential
from settings import get_settings

settings = get_settings()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
# Initialize Vertex AI SDK
vertexai.init(project=settings.project_id, location=settings.location)
logging.info("Done Initializing Vertex AI SDK")

#Methods Needed
# 1. validate Food Options(Food Name) 
# 2. generate a image/video clip and store in folder/bucket and provide access link.
# 3. generate food description (include the types/variations based on preference).
# 4. generate flavour profile map
# 5. generate Cooking instructions
# 6. generate expertise level

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
def generate_details(food_name, origin, preference):
    """Generates a description, flavour map, cooking instructions, and expertise level for a food option using the Gemini API.
    Trying to reduce costs by getting the details in a single call."""

    prompt = f"""
    Check if {food_name} is a food dish and is not a common ingredient or a incorrect name.
    If {food_name} is not a dish, return "Not a dish".
    Else:
    return a json with the following details generated for the food: {food_name}, with origin from: {origin} and based on preference: {preference}:
    [
        "description": "generate a concise description (max 100 words) Also include key highlights (any history or speciality is optional) and benefits of the food as well as cues for any potential side effects.",
        "flavour_profile": "generate a flavour profile map with strongest flavours first",
        "ingredients": "ingredients map like "milk":"Essential", "Sugar":"Optional""
        "cooking_instructions": "generate Cooking instructions in format step number: instruction",
        "expertise_level": "generate expertise level required to cook the food"
    ]
    """
    try:
        model = VertexAI(model_name=settings.gemini_model_name, verbose=True)
        response = model.invoke(prompt)
        return response
    except Exception as e:
        logging.info(f"Error generating description for {pose_name}: {e}")
        return ""


def add_descriptions_to_json(input_file, output_file):
    """
    Processes food options from an input file, checks for existing entries in the output file,
    and processes only the new food items.

    Args:
        input_file (str): The path to the input JSON file.
        output_file (str): The path to the output JSON file.
    """
    try:
        with open(input_file, "r") as f:
            food_options = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in input file {input_file}")
        return

    try:
        with open(output_file, "r") as of:
            food_options_covered = json.load(of)
    except FileNotFoundError:
        print(f"Output file not found at {output_file}. Creating a new one.")
        food_options_covered = []
    except json.JSONDecodeError:
        print(f"Warning: Invalid JSON in output file {output_file}. Overwriting it.")
        food_options_covered = []

    # Create a set of food names from the output file for efficient checking.
    existing_dishes = {entry["name"] for entry in food_options_covered}

    total_foods = len(food_options) - len(existing_dishes)
    processed_count = 0
    new_foods_to_add = []  # List to store new foods
    batch_size = 100  # Number of foods to process before appending to the output file


    for food in food_options:
        if food["name"] not in existing_dishes:
            if "\\" not in food["name"] and food.get("description", "")=="":
                print(f"\nProcessing: {processed_count+1}/{total_foods} - {food['name']}")
                start_time = time.time()  # Record start time
                full_details = generate_details(
                    food["name"],
                    food["origin"],
                    food["preference"], #food["preference"]
                )
                if full_details == "Not a dish":
                    print(f"Not a dish: {food['name']}")
                    processed_count += 1
                    continue

                print(full_details+"\n")
                details = parse_food_details_string(full_details)
                if details is not None:
                    if food["name"] in details:
                        details = details[food["name"]]
                    if "details" in details:
                        details = details["details"]
                    if type(details) == list and len(details) == 1:
                        details = details[0]
                    if type(details) == dict:
                        food["description"] = details.get("description", "")
                        if not food["description"]:
                            print(f"Error parsing description for {food['name']}")

                        food["flavour_profile"] = details.get("flavour_profile", "")
                        if not food["flavour_profile"]:
                            print(f"Error parsing flavour profile for {food['name']}")

                        food["ingredients"] = details.get("ingredients", {})
                        if not food["ingredients"]:
                            print(f"Error parsing ingredients for {food['name']}")

                        food["cooking_instructions"] = details.get("cooking_instructions", "")
                        if not food["cooking_instructions"]:
                            print(f"Error parsing cooking instructions for {food['name']}")

                        food["expertise_level"] = details.get("expertise_level", "")
                        if not food["expertise_level"]:
                            print(f"Error parsing expertise level for {food['name']}")
                    else:
                        print(f"Error parsing details for {food['name']}")
                        print(details)
                        continue

                processed_count += 1
                end_time = time.time()  # Record end time
                time_taken = end_time - start_time
                logging.info(
                    f"Processed: {processed_count}/{total_foods} - {food['name']} ({time_taken:.2f} seconds)"
                )

            else:
                food["description"] = ""
                processed_count += 1
                logging.info(
                    f"Couldnt process: {processed_count}/{total_foods} - {food['name']}"
                )
            new_foods_to_add.append(food)  # Keep the original food data
            # Adding a delay to avoid rate limit
            time.sleep(1)
        

        if (processed_count + 1) % batch_size == 0 or (processed_count + 1) == total_foods:
            # Append the batch of new foods to the output file
            food_options_covered.extend(new_foods_to_add)
            try:
                with open(output_file, "w") as of:
                    json.dump(food_options_covered, of, indent=4)
                print(f"Appended {len(new_foods_to_add)} foods to {output_file}")
            except Exception as e:
                print(f"Error writing to output file {output_file}: {e}")
                return
            new_foods_to_add = []  # Clear the list for the next batch



def parse_food_details_string(json_string):
  """
  Parses a JSON string containing food details into a Python dictionary.
  Args:
    json_string: A string containing JSON data.
  Returns:
    A Python dictionary representing the parsed JSON data, or None if parsing fails.
  """
  try:
    delimiters = [json_string.find('{'), json_string.rfind('}')]
    json_string = json_string[delimiters[0]:delimiters[1]+1]
    data = json.loads(json_string)
    #print("Parsed Details:\n",data,"\n")
    return data
  except json.JSONDecodeError as e:
    print(f"Error decoding JSON string: {e}")
    return None

def main():
    # File paths
    input_file = "./data/foodOptions-all.json"
    output_file = "./data/foodOptions_with_descriptionsAll.json"

    # Add descriptions and save the updated JSON
    add_descriptions_to_json(input_file, output_file)


if __name__ == "__main__":
    main()
