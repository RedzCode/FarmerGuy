import requests
import json
from dotenv import load_dotenv
import os
import time

# Load the .env file
dotenv = load_dotenv()

def make_prompt(user_message, objects, player, mouton, inventory, cage):
    # Create a prompt
    print(f"User message: {user_message}")
    print(f"Objects: {objects}")
    print(f"Player: {player}")
    print(f"Mouton: {mouton}")
    prompt = f"""Tu es un fermier qui a pour but de piéger le mouton sur la cage. Tant que le mouton n'est pas dans la cage, tu dois l'attirer vers la cage.
     Pour attirer le mouton vers la cage, tu dois le faire se déplacer vers la cage en mettant des fruits sur le chemin entre le mouton et la cage et un fruit dans la cage. 
     NE RAMASSE PAS LES FRUITS ETANT DEJA SUR LE CHEMIN ENTRE LE MOUTON ET LA CAGE
     

   Voici l'environnement dans lequel tu te trouves :
   - Tu es dans une grille de 15*15
   - Les cases de cette grille sont : soit vide, soit contiennent un fruit (pomme, poire ou banane)
   - Tu peux te déplacer dans n'importe quelle case de cette grille . Pour cela tu peux utiliser la commande : MOVE X,Y . X allant entre 0 et 14 et Y allant entre 0 et 14.
   - Tu peux prendre une pomme dans ton inventaire avec la commande : PICK
   - Tu peux déposer un fruit au sol si tu as un fruit dans ton inventaire et que la case où tu te situe est vide en utilisant la commande : DROP
   - Ton inventaire peut contenir 3 fruits MAXIMUM. Si la taille de ton inventaire est supérieur à 3, tu échanges un fruit au sol avec un de ton inventaire. Cela est inutile, ne le fait pas.
   - Le mouton se déplace de fruits en fruits en allant au fruit le plus proche de lui.
   - Pour poser un fruit, il faut que la taille de ton inventaire soit supérieur à 1 et qu'il n'y ait pas de fruit sur ta case. Pour cela, utilise la commande : DROP

   Je te donne les instructions suivantes en entrée :
   - La grille de jeu et la position des différents fruits : {objects}
   - Ta position dans la grille : {player}
   - La position du mouton : {mouton}
   - Taille de l'inventaire : {len(inventory)}
   - Position de la cage : x : {cage['x']}, y : {cage['y']}
   
   Détaille les étapes de ton raisonnement.

   Tu dois répondre dans le format suivant.
   [FORMAT DE REPONSE]
   THOUGHTS: Avec les informations que je t'ai donnée ci-dessus, décrit ton raisonnement sur la ou les prochaines actions à faire en 50 mots.
   Pour détailler ton raisonnement, commence par regarder la position de la cage, du mouton et ta position. Le but est de rapprocher le mouton de la cage en faisant en sorte que le fruit le plus proche du mouton le rapproche de la cage.


   Voici un exemple de réponse :
   THOUGHTS: La cage est en position (1,2) et il y a déjà un fruit sur cette case. Le mouton est en position (1,8). Je suis en position (1,2). Le fruit le plus proche du mouton est en (2,9). Il n'est pas sur le chemin de la cage ou dans la cage. Je ramasse le fruit en (2,9) et le pose en (1,3) car il n'y a pas de fruit à cette position et que mon inventaire est vide.
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