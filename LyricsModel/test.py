import stanfordnlp
nlp = stanfordnlp.Pipeline(models_dir='/Users/hangjiezheng/Desktop/CSCI534')
a = nlp("i'm a student.")
for sent in a.sentences:
    for word in sent.words:
        print(word.lemma)
