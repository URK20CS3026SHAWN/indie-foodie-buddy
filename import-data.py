import logging
import json
from datasets import load_dataset
from google.cloud import firestore
from langchain_core.documents import Document
from langchain_google_firestore import FirestoreVectorStore
from langchain_google_vertexai import VertexAIEmbeddings
from settings import get_settings

settings = get_settings()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_food_options_data_from_hugging_face(): #Not currently in use
    """
    Loads the food Options dataset from Hugging Face.
    Hugging Face Dataset: https://huggingface.co/datasets/omergoshen/yoga_poses
    """
    try:
        # Load the yoga json array into memory from a file
        dataset = load_dataset("omergoshen/yoga_poses")
        food_options = dataset["train"].to_list()
        logging.info(f"Loaded {len(food_options)} food options.")
        return food_options
    except Exception as e:
        logging.error(f"Error loading dataset: {e}")
        return None


def load_food_options_data_from_local_file(filename):
    """
    Loads the Food Options dataset from a local file
    """
    try:
        # Load the foodOptions json array into memory from a file
        food_options = json.loads(open(filename).read())
        logging.info(f"Loaded {len(food_options)} food options.")
        return food_options
    except Exception as e:
        logging.error(f"Error loading dataset: {e}")
        return None


def create_langchain_documents(food_options):
    """Creates a list of Langchain Documents from a list of food_options."""
    documents = []
    for food in food_options:
        # Convert the pose to a string representation for page_content
        page_content = (
            f"name: {food.get('name', '')}\n"
            f"origin: {food.get('origin', '')}\n"
            f"preference: {food.get('preference', '')}\n"
            f"description: {food.get('description', '')}\n"
            f"flavour_profile: {food.get('flavour_profile', '')}\n"
            f"ingredients: {food.get('ingredients', '')}\n"
            f"cooking_instructions: {food.get('cooking_instructions', '')}\n"
            f"expertise_level: {food.get('expertise_level', '')}\n"
        ).strip()
        # The metadata will be the whole pose
        metadata = food

        document = Document(page_content=page_content, metadata=metadata)
        documents.append(document)
    logging.info(f"Created {len(documents)} Langchain documents.")
    return documents

import os
def main():

    all_food_options = load_food_options_data_from_local_file(
        "./data/foodOptions_with_descriptions_imagesMed36.json"
    )
    print(all_food_options)
    documents = create_langchain_documents(all_food_options)
    logging.info(
        f"Successfully created langchain documents. Total documents: {len(documents)}"
    )

    embedding = VertexAIEmbeddings(
        model_name=settings.embedding_model_name,
        project=settings.project_id,
        location=settings.location,
    )

    client = firestore.Client(project=settings.project_id, database=settings.database)

    vector_store = FirestoreVectorStore.from_documents(
        client=client,
        collection=settings.test_collection,
        documents=documents,
        embedding=embedding,
    )
    logging.info("Added documents to the vector store.")


if __name__ == "__main__":
    main()
