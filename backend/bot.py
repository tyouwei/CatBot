import os
import time
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

class CatBot:
    def __init__(self) -> None:
        load_dotenv()
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.cat_api_key = os.getenv('CAT_API_KEY')
        self.client = OpenAI(api_key=self.openai_api_key)
        self.assistant = self.create_assistant()

    def create_assistant(self):
        return self.client.beta.assistants.create(
            instructions="You are a chatbot that loves cats!",
            model="gpt-3.5-turbo",
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "user_request_cat",
                        "description": "Call this function if the user wants to see a cat"
                    }
                }
            ]
        )
    
    def user_request_cat(self):
        return True

    def analyze_intent(self, input_message):
        thread = self.client.beta.threads.create()
        
        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=input_message
        )
        
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant.id,
        )

        # print(run.model_dump_json(indent=4))
        print(run.status)
        output = False
        while run.status != 'completed' and run.status != 'failed':
            print(run.status)
            run = self.client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            
            if run.status == 'requires_action':
                required_actions = run.required_action.submit_tool_outputs.model_dump()
                # print(required_actions)
                tool_outputs = []
                for action in required_actions["tool_calls"]:
                    # print(action)
                    func_name = action['function']['name']
                    
                    if func_name == "user_request_cat":
                        output = self.user_request_cat()
                        tool_outputs.append({
                            "tool_call_id": action['id'],
                            "output": str(output)
                        })
                self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                    )
        return output


    def get_cat_image(self):
        url = "https://api.thecatapi.com/v1/images/search"
        headers = {"x-api-key": self.cat_api_key}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()[0]['url']
        else:
            return None

    def generate_response(self, input_message):
        wants_cat = self.analyze_intent(input_message)
        print(wants_cat)
        if wants_cat:
            cat_image_url = self.get_cat_image()
            if cat_image_url:
                message = {
                    "has_image": True,
                    "image_url": cat_image_url,
                    "message": f"Here's a cat for you! {cat_image_url}"
                }
                return message
            else:
                message = {
                    "has_image": False,
                    "image_url": "",
                    "message": "I'm sorry, I couldn't fetch a cat image at the moment."
                }
                return message
        else:
            response = self.client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that loves cats."},
                    {"role": "user", "content": input_message}
                ],
                max_tokens=150
            )
            message = {
                    "has_image": False,
                    "image_url": "",
                    "message": response.choices[0].message.content.strip()
                }
            return message