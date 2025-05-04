import json
import time
import os
import logging
from settings import get_settings
import vertexai
from vertexai.vision_models import ImageGenerationModel

settings = get_settings()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

vertexai.init(project=settings.project_id, location=settings.location)


def generate_image(prompt: str, ImageName: str = "", storeImage: bool = True, storageLocation: str = ""):
    try:
        model = ImageGenerationModel.from_pretrained(
            settings.image_generation_model_name
        )

        images_Response = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            aspect_ratio="1:1",
        )

        if len(images_Response.images) == 0:
            logging.error("No images generated")
            return None


        if ImageName == "":
            # generate a random output file name with an extension being png
            import uuid
            ImageName = str(uuid.uuid4().hex) + ".png"
    
        output_file = f"./images/{storageLocation}/{ImageName}.png"

        images_Response.images[0].save(
            location=output_file, include_generation_parameters=False
        )

        # Optional. View the generated image in a notebook.
        # images[0].show()

        print(f"Created output image using {len(images_Response.images[0]._image_bytes)} bytes")
        # Example response: Created output image using 1234567 bytes
        return output_file
    except Exception as e:
        logging.error(f"Error generating image: {e}")
        return None


def generate_food_image(food):
    """Generates a image of the food based on the food[name], food[origin], food[preference]."""
    
    food_name, origin, preference = food["name"], food["origin"], food["preference"]
    prompt = f"Generate a ultra-realistic image of {food_name} describing its {origin} origin and which is {preference}"
    
    return generate_image(prompt, food_name, True, "food_images")

def add_images_to_json(input_file, output_file):
    """Loads JSON data, adds descriptions, and saves the updated data."""

    with open(input_file, "r") as f:
        food_options = json.load(f)

    # Load existing food data from output file, if it exists
    if os.path.exists(output_file):
        try:
            with open(output_file, "r") as of:
                food_options_covered = json.load(of)
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in output file.  Overwriting.")
            logging.warning(f"Invalid JSON in output file. Overwriting.")
            food_options_covered = []  # Ensure existing_foods is initialized
    else:
        print(f"Output file does not exist. Creating a new one.")
        food_options_covered = []

    # Create a set of food names from the output file for efficient checking.
    existing_foods = {entry["name"] for entry in food_options_covered}

    total_foods = len(food_options) - len(existing_foods)
    processed_count = 0
    new_foods_to_add = []  # List to store new foods
    batch_size = 10
    
    for food in food_options:
        if food["name"] not in existing_foods:
            if "\\" not in food["name"] and food["description"]!="Not a dish" and not food.get("photo_url", ""):

                print(f"\nProcessing: {processed_count+1}/{total_foods} - {food['name']}")
                start_time = time.time()  # Record start time

                #Generate a image of the food based on the food[name], food[origin], food[preference]
                generate_food_image(food)
                processed_count += 1
                
                end_time = time.time()  # Record end time
                time_taken = end_time - start_time
                logging.info(f"Processed: {processed_count}/{total_foods} - {food['name']} ({time_taken:.2f} seconds)")
                
                #Store the image in images
                image_url = f"https://raw.githubusercontent.com/URK20CS3026SHAWN/indie-foodie-buddy/refs/heads/main/images/food_images/+{food['name']}.png"
                food["photo_url"] = image_url
            
            else:
                processed_count += 1
                logging.info(f"Couldnt process: {processed_count}/{total_foods} - {food['name']}")
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



if __name__ == "__main__":
    # generate_image(prompt="Generate photo of Indian flag being unfurled")
    add_images_to_json("./data/foodOptions_with_descriptionsSmall.json", "./data/foodOptions_with_descriptions_ImagesTestSmall.json")
