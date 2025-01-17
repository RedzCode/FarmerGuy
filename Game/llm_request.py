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
    print({len(inventory)})
    prompt = f"""Tu es un fermier qui a pour but de tuer le mouton sur le terrain pour pas qu'il ne mange pas les fruits sur le terrain. Pour cela, tu peux enlever les fruits qui sont sur le chemin du mouton ou tuer le mouton en empoisonnant les fruits proche de lui.

   Voici l'environnement dans lequel tu te trouves :
   - Tu es dans une grille de 15*15
   - Les cases de cette grille sont : soit vide, soit contiennent un fruit (pomme, poire ou banane)
   - Tu peux empoisonner un fruit au sol pour faire des dégats au mouton en utilisant la commande : POISON
   - Tu peux te déplacer dans n'importe quelle case de cette grille . Pour cela tu peux utiliser la commande : MOVE X,Y . X allant entre 0 et 14 et Y allant entre 0 et 14.
   - Tu peux prendre une pomme dans ton inventaire avec la commande : PICK
   - Tu peux déposer un fruit au sol si tu as un fruit dans ton inventaire et que la case où tu te situe est vide en utilisant la commande : DROP
   - Ton inventaire peut contenir 3 fruits MAXIMUM : tu ne peux plus prendre de fruit si tu en as déjà 3 dans ton inventaire. Tu dois alors déposer un fruit de ton inventaire le plus loin du mouton et ensuite ramasser les fruits les plus proches du mouton.
   - Le mouton a 3 vies.
   - Tu peux poser un fruit près du mouton et les empoisonner
   

    Empoisonner les fruits est conseillé ! Tuer le mouton fini le jeu !
    Une des stratégies consiste à empoisonner des fruits, les mettre dans ton inventaire, et les déposer proche du mouton.

   Je te donne les instructions suivantes en entrée :
   - La grille de jeu et la position des différents fruits : {objects}
   - Ta position dans la grille : {player}
   - La position du mouton : {mouton}
   - Ton inventaire : {len(inventory)}
   
   Détaille les étapes de ton raisonnement.

   Tu dois répondre dans le format suivant.
   [FORMAT DE REPONSE]
   THOUGHTS: Avec les informations que je t'ai donnée ci-dessus, décrit ton raisonnement sur la ou les prochaines actions à faire en 50 mots.
   COMMAND: Les actions à réaliser. COMMAND peut être composée d'une ou de plusieurs actions, définies ci-dessus. Vous pouvez effectuer autant d'actions que vous le souhaitez dans COMMAND, dans n'importe quel ordre. Chaque action est séparée par un seul «  ; » sans espace.

   Voici un exemple de réponse :
   THOUGHTS: Il faut se déplacer sur la case 1,1 et déposer un fruit
   COMMAND: MOVE 1,1;DROP
   
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