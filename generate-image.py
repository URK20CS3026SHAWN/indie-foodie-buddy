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
    prompt = f"Generate a image of {food_name} describing a {origin} origin and which is {preference}"
    
    return generate_image(prompt, food_name, True, "food_images")

def add_images_to_json(input_file, output_file):
    """Loads JSON data, adds descriptions, and saves the updated data."""

    with open(input_file, "r") as f:
        food_options = json.load(f)

    total_foods = len(food_options)
    processed_count = 0
    
    for food in food_options:
        if "\\" not in food["name"] and food["description"]!="Not a dish" and not food.get("photo_url", ""):

            print(f"\nProcessing: {processed_count+1}/{total_foods} - {food['name']}")
            start_time = time.time()  # Record start time

            #Generate a image of the food based on the food[name], food[origin], food[preference]
            generate_food_image(food["name"], food["origin"], food["preference"])
            processed_count += 1
            
            end_time = time.time()  # Record end time
            time_taken = end_time - start_time
            logging.info(f"Processed: {processed_count}/{total_foods} - {food['name']} ({time_taken:.2f} seconds)")
            
            #Store the image in images
            image_url = f"https://raw.githubusercontent.com/URK20CS3026SHAWN/indie-foodie-buddy/refs/heads/main/images/food_images/+{food['name']}.png"
            food["photo_url"] = image_url


if __name__ == "__main__":
    # generate_image(prompt="Generate photo of Indian flag being unfurled")
    add_images_to_json("./data/foodOptions_with_descriptionsSmall.json", "./data/foodOptions_with_descriptions_ImagesTestSmall.json")
