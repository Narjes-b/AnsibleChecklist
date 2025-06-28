import yaml
import nltk
import spacy
import pandas as pd
from nltk.stem import WordNetLemmatizer


lemmatizer = WordNetLemmatizer()
nlp = spacy.load('en_core_web_lg')

def calculate_similarity(file_path):
    try:
        with open(file_path, 'r', encoding='latin1') as f:
            yaml_data = yaml.load(f, Loader=yaml.Loader)
           

            if not yaml_data or not isinstance(yaml_data, list):
                print("File is not a valid YAML or is empty.")
                return None
        
            sum_similarity = 0
            num_pairs = 0
            
            # plays names without unnamed plays
            play_names = [play['name'] for play in yaml_data if 'name' in play and play['name'] is not None]
            #play_names = [play['name'] for play in yaml_data if 'name' in play]
            #print(play_names)

            preprocessed_play_names = [lemmatizer.lemmatize(name.lower()) for name in play_names]

            for i in range(len(preprocessed_play_names)):
                #for j in range(i + 1, len(preprocessed_play_names)):

                    doc_i = nlp(preprocessed_play_names[i])
                    if not doc_i.has_vector:
                        continue  # Skip if no vector
                    
                    for j in range(i + 1, len(preprocessed_play_names)):
                        doc_j = nlp(preprocessed_play_names[j])
                        if not doc_j.has_vector:
                            continue  # Skip if no vector
                        
                        similarity_p = doc_i.similarity(doc_j)

                    #similarity = nlp(preprocessed_play_names[i]).similarity(nlp(preprocessed_play_names[j]))
                        sum_similarity += similarity_p
                        num_pairs += 1
            # tasks names without unnamed tasks
            tasks = [task for play in yaml_data if 'tasks' in play for task in play['tasks']]
            task_names = [task['name'] for task in tasks if 'name' in task and task['name'] is not None]
            #print(task_names)
            preprocessed_task_names = [lemmatizer.lemmatize(name.lower()) for name in task_names]

            for i in range(len(preprocessed_task_names)):
                doc_i = nlp(preprocessed_task_names[i])
                if not doc_i.has_vector:
                    continue  # Skip if no vector
                
                for j in range(i + 1, len(preprocessed_task_names)):
                    doc_j = nlp(preprocessed_task_names[j])
                    if not doc_j.has_vector:
                        continue  # Skip if no vector
                    
                    similarity_t = doc_i.similarity(doc_j)
                    sum_similarity += similarity_t
                    num_pairs += 1

            if num_pairs > 0:
                average_similarity = sum_similarity / num_pairs
            else:
                average_similarity = 1  

            return average_similarity
            
    except Exception as e:
        print(f"Impossible to read {file_path}. Error: {e}")
        return None

# Tester la fonction
if __name__ == '__main__':
    file_path = '/Users/narjes/Documents/Research/Contrib_AnsibleSmells/data/projects/adriagalin/ansible.motd/tasks/main.yml'  
    average_similarity = calculate_similarity(file_path)
    
    if average_similarity is not None:
        print(f'La similarité moyenne est : {average_similarity}')
    else:
        print('Pas de métriques disponibles.')
