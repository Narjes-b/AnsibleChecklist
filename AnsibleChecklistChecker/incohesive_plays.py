import csv
import spacy
from detect_large_play import calculate_metrics_play
import yaml
import pandas as pd
from nltk.stem import WordNetLemmatizer

# Initialisation du lemmatiseur et du modèle Spacy
lemmatizer = WordNetLemmatizer()
nlp = spacy.load('en_core_web_lg')
def read_thresholds():
    thresholds = {}
    with open('/Users/narjes/Documents/Research/Contrib_AnsibleSmells/AnsibleCodeSmells-master/CodeSmellsTool/thresholds.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  # sauter l'en-tête
        for row in reader:
            if len(row) < 2:
                print(f"Ligne ignorée car elle est incomplète : {row}")
                continue
            key, value = row[0], float(row[1])  
            thresholds[key] = value
    return thresholds





def calculate_similarity(file_path):
    metrics = calculate_metrics_play(file_path)
    incohesive=0
    thresholds = read_thresholds()
    if metrics:
        for i, play_metrics in enumerate(metrics['Plays']):
            df = pd.DataFrame([play_metrics])
            sum_similarity = 0
            num_pairs = 0
            

            playname= df['Play_name'].values[0] if 'Play_name' in df.columns else 'Unknown Play'
            tasks_in_play = df['num_tasks_in_play'].values[0] if 'num_tasks_in_play' in df.columns else 0
            name_tasks_inplay = df['tasks_names'].values[0] if 'tasks_names' in df.columns else []
            #print(f"DataFrame pour le Play {i + 1}:")
            #print(playname)
            #print(tasks_in_play)
            #print(name_tasks_inplay)

         
            preprocessed_task_names = [lemmatizer.lemmatize(name.lower()) for name in name_tasks_inplay]

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
                average_similarity = 1  # Si aucun pair n'est trouvé, mettre la similarité à 1
            
            #print(f"Le Play {i} a une similarité sémantique de {average_similarity:.2f}.")
            threshold = thresholds.get('similarityPlays', 0)
            if average_similarity < threshold:
                    #print(f"Le Play {i} a une similarité sémantique de {average_similarity:.2f}, ce qui est inférieur au seuil de {threshold}.")
                    incohesive += 1
            
    else:
        print('Pas de métriques disponibles.')


    return incohesive     
# Tester la fonction
if __name__ == '__main__':
    file_path = '/Users/narjes/Documents/Research/Contrib_AnsibleSmells/data/projects/adriagalin/ansible.motd/tasks/main.yml'  
    
    
    numincohesive=calculate_similarity(file_path)
    if numincohesive > 0:
        print(f"Nombre de plays incohérents : {numincohesive}")
    else:
        print("Aucun play incohérent trouvé.")