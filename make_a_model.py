import pandas as pd
import os
import betacode.conv as beta
import gensim.models

class MyCorpus:
    """An iterator that yields sentences (lists of str)."""
    
    def __iter__(self):
        for root, dirs, files in os.walk("DiorisisCorpus1.51//"):
            for name in files:
                temp_df = pd.read_json(os.path.join(root, name))
                for sentence in temp_df["sentences"]:
                    lemmata = []
                    for word in sentence["tokens"]:  
                        try:
                            lemmata.append(beta.beta_to_uni(word["lemma"]["entry"]))
                        except KeyError:
                            continue
                    yield lemmata

sentences = MyCorpus()
model = gensim.models.Word2Vec(sentences=sentences, workers=8)


