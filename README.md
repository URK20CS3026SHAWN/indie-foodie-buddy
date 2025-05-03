# Food Exploration Recommender for Tourists/Food Fanatics
A Flask Web Application that demonstrates how to do Vector Search on a Yoga Poses database in Firestore. 
You can check out the latest Edition of this App [here](https://indie-foodie-buddy-444738326331.us-central1.run.app)

The application is a step by step demonstration of the following:
1. Utilize an Food-Options Dataset of Food Options (JSON format). You can download it/find it in data folder from this Github Repo.
2. Enhance the dataset with an additional field `description, ingredients, cooking instructions, flavours and so on` that uses Gemini to generate details for each of the foods.
3. Use Langchain to create a Document, use Firestore Langchain integration to create the collection in Firestore.
4. Create a composite index in Firestore to allow for Vector search.
5. Utilize the Vector Search in a Flask Application that brings everything together as shown below:

<img title="a title" alt="Alt text" src="/images/screenshot.png">

## Technologies used:
1. Python + Flask Framework
2. Google Cloud : Firestore, Cloud Run, Gemini in Vertex AI
3. Langchain Python framework

## Codelab
You can also check out this codelab to understand this application with this link that provides step by step instructions to run/deploy a similar Yoga Pose Recommender (that I had used as reference to build this app): [codelab](https://codelabs.developers.google.com/yoga-pose-firestore-vectorsearch-python?hl=en#0).
