import requests
import json
from dotenv import load_dotenv
import os
import time

# Load the .env file
dotenv = load_dotenv()

def make_prompt(user_message, objects, player, mouton, inventory):
    # Create a prompt
    print(f"User message: {user_message}")
    print(f"Objects: {objects}")
    print(f"Player: {player}")
    print(f"Mouton: {mouton}")
    prompt = f"""Tu es un fermier qui a pour but d'empêcher le mouton de manger les fruits sur le terrain. Pour cela, tu peux enlever les fruits qui sont sur le chemin du mouton.

   Voici l'environnement dans lequel tu te trouves :
   - Tu es dans une grille de 15*15
   - Les cases de cette grille sont : soit vide, soit contiennent un fruit (pomme, poire ou banane)
   - Tu peux te déplacer dans n'importe quelle case de cette grille . Pour cela tu peux utiliser la commande : MOVE X,Y . X allant entre 0 et 14 et Y allant entre 0 et 14.
   - Tu peux prendre une pomme dans ton inventaire avec la commande : PICK
   - Tu peux déposer un fruit au sol si tu as un fruit dans ton inventaire et que la case où tu te situe est vide en utilisant la commande : DROP
   - Ton inventaire peut contenir 3 fruits MAXIMUM, si tu prends un fruit alors que tu en as 3 dans ton inventaire, tu vas ramasser un fruit et en déposer un de ton inventaire

   Je te donne les instructions suivantes en entrée :
   - La grille de jeu et la position des différents fruits : {objects}
   - Ta position dans la grille : {player}
   - La position du mouton : {mouton}
   - Ton inventaire : {inventory}
   
   Détaille les étapes de ton raisonnement.

   Tu dois répondre dans le format suivant.
   [FORMAT DE REPONSE]
   THOUGHTS : Avec les informations que je t'ai donnée ci-dessus, décrit ton raisonnement sur la ou les prochaines actions à faire en 50 mots.
   COMMAND : Les actions à réaliser.


   Voici un exemple de réponse :
   THOUGHTS: Il faut se déplacer sur la case 1,1 et déposer un fruit
   COMMAND: The next COMMAND. A COMMAND can be composed of one or multiple actions, which are defined above. You can do as many actions as you want in a COMMAND, in any order. Split every action by a single ";" and no space.
   """

    return prompt

# Function to extract the thoughts and command from the text
def extract_thoughts_and_command(text):
    # Initialiser les variables pour stocker les thoughts et la commande
    thoughts = None
    action = None

    # Extraire les thoughts
    if "THOUGHTS:" in text:
        start_thoughts = text.index("THOUGHTS:") + len("THOUGHTS:")
        end_thoughts = text.index("COMMAND:")
        thoughts = text[start_thoughts:end_thoughts].strip()

    # Extraire la commande
    if "COMMAND:" in text:
        command_part = text.split("COMMAND:")[1].strip()
        action = command_part

    return thoughts, action

# Function to make a request to the API
def make_request(prompt):

    def send_request():
        # Make a request to the API
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('API_KEY')}",
            },
            data=json.dumps({
                "model": "deepseek/deepseek-chat", # Optional
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        return response.json()

    
    # Send request 
    response = send_request()
    # print(response)

    # Check if the rate limit was reached
    while('error' in response and response['error']['code'] == 429): 
        # Wait for 30 seconds and try again
        print('Rate limit reached, waiting for 30 seconds')
        time.sleep(30)
        response = send_request()

    # Check if the request was successful
    if 'error' in response:
        raise Exception(f"Failed to make the request: {response}")

    # Get the answer from the response
    answer = response['choices'][0]['message']['content']
    return answer