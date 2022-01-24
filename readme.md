# OC_P10_Poullain_Arthur

API Django Rest sécurisée (Python 3.8)

# Installation guide :
* Clone the Repository : ```$ git clone https://github.com/Barbecuecitron/OC_P10_Poullain_Arthur ```

# Prepare the Venv 
* Create a new environment ``` $python -m venv MyEnv ```
* Activate the env with ``` $MyEnv\Scripts\Activate ```
* Install the required libraries in the env ``` $pip install -r \path\to\repository\requirements.txt ```
--
# How to use ?
* Run ``` $MyEnv\Scripts\Activate ``` to activate the venv
* Go to the softdesk_api directory ``` $cd softdesk_api```
* Run the app : ``` $python manage.py runserver```
* The main url address is the following :``` http://localhost:8000/api/ ```
* Follow the instructions of the POSTMAN documentation to register / sign in
* Be sure to match the required fields and formats from the documentation before sending anything in PUT / POST requests or you might get errors.
* The db will be located in the softdesk_api folder under the name of db.sqlite3