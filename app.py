from turtle import color
import streamlit as st
import pandas as pd
from gensim.models import Word2Vec
from greek_normalisation.normalise import Normaliser, Norm
import random
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import math
plt.set_cmap('hot')
# cm = sns.light_palette("purple", as_cmap=True)

@st.experimental_singleton
def load_model():
	loaded_model = Word2Vec.load("gensim-model-word2vec-August")
	# st.write("Cache miss!")
	return loaded_model

@st.experimental_singleton
def start_normaliser():
	normaliser = Normaliser().normalise
	return normaliser

@st.experimental_singleton
def load_glosses():
	defs = pd.read_csv("normalised_glosses.tsv", sep="\t")
	return defs

def get_gloss(lemma):
    try:
        y = glosses.loc[glosses["lemma"] == lemma].iloc[0]["def"]
        return y
    except IndexError:
        return "-"

def random_search():
	search = vocab[random.randrange(0, len(vocab))]

def update_search(new_search):
	st.session_state.search_updated = True
	st.session_state.search_default = new_search

normalise = start_normaliser()
glosses = load_glosses()
	
model = load_model()
vocab = model.wv.index_to_key
if "search_updated" not in st.session_state:
	st.session_state["search_updated"] = False
if "search_default" not in st.session_state:
	st.session_state["search_default"] = "λέγω"

if st.session_state.search_updated is True:
	search = st.multiselect("Word?", vocab, default=st.session_state.search_default)#, index=random.randrange(0, len(vocab)))
else:
	search = st.multiselect("Word?", vocab, default="λέγω")#, index=random.randrange(0, len(vocab)))


if st.checkbox("Do you want to add a negative search term?"):
	antisearch = st.multiselect("Negative word?", vocab)
else:
	antisearch = None

if st.button("Random"):
	seeking = True
	while seeking == True:
		rand_word = vocab[random.randrange(0, len(vocab))]
		if get_gloss(rand_word) != "-":
			seeking = False
	search = [rand_word]

if len(search) is not 0:
	sim = model.wv.most_similar(positive=search, negative=antisearch, topn=50)
	results = [(res[0], get_gloss(normalise(res[0])[0]), res[1], vocab.index(res[0])+1) for res in sim]
	df = pd.DataFrame.from_records(results, columns=("Related Words", "Gloss", "Relatedness", "Word Frequency"))

	st.subheader("You searched for words related to:")
	cols = st.columns(len(search))
	for search_term, col in zip(search, cols):
		with col:
			search_gloss = get_gloss(normalise(search_term)[0])
			st.metric(search_gloss, search_term, f"Frequency Rank: {vocab.index(search_term)+1}")

	if antisearch is not None and len(antisearch) is not 0:
		st.subheader("And unrelated to:")
		anticols = st.columns(len(antisearch))
		for search_term, col in zip(antisearch, anticols):
			with col:
				search_gloss = get_gloss(normalise(search_term)[0])
				st.metric(search_gloss, search_term, f"Frequency Rank: {vocab.index(search_term)+1}")

	# st.table(df.style.hide().background_gradient(subset="Word Frequency", gmap=[1/x for x in df["Word Frequency"]]))

	header_cols = st.columns(4)
	with header_cols[0]:
		st.subheader("Related Words")
	with header_cols[1]:
				st.subheader("Gloss")
	with header_cols[2]:
				st.subheader("Relatedness")
	with header_cols[3]:
				st.subheader("Frequency")

	for related_word, gloss, relatedness, frequency in results:
		result_cols = st.columns(4)
		with result_cols[0]:
			st.button(related_word, on_click=update_search, kwargs={"new_search": related_word})
		with result_cols[1]:
			if gloss is not "-":
				st.write(f"[{gloss}](https://logeion.uchicago.edu/{related_word})")
			else:
				st.write(f"[\[No short definition found\]](https://logeion.uchicago.edu/{related_word})")
		with result_cols[2]:
			# num = [relatedness]
			# hovertemp = f"{relatedness}"

			# fig = px.bar(x=num, range_x = [0, 1], width=300, height=200)
			# fig.update_traces(hovertemplate=hovertemp)
			# fig.update_layout(showlegend=False)
			# fig.update_xaxes(visible=False)
			# fig.update_yaxes(visible=False)



			num = [relatedness]
			word = ["Relatedness"]
			fig = plt.figure()
			fig.set_size_inches(1,.15)
			ax = plt.Axes(fig, [0., 0., 1., 1.])
			ax.set_xlim(0,2)
			ax.set_axis_off()
			ax.get_xaxis().set_visible(False)
			ax.get_yaxis().set_visible(False)
			fig.add_axes(ax)
			hbar = ax.barh(word, num, color="grey")
			label = [float(str(num[0])[:4])]
			ax.bar_label(hbar, label, label_type="edge", padding=6, fontsize=6)
			st.pyplot(fig, bbox_inches=0, transparent=False)
		with result_cols[3]:
			pass
			num = [math.exp(-0.0002*frequency)]
			word = ["Frequency"]
			plt.autoscale()
			fig2 = plt.figure()
			fig2.set_size_inches(1, .15)
			ax2 = plt.Axes(fig2, [0., 0., 1., 1.])
			ax2.set_xlim(0,2)
			ax2.set_axis_off()
			ax2.get_xaxis().set_visible(False)
			ax2.get_yaxis().set_visible(False)
			fig2.add_axes(ax2)
			my_cmap=plt.get_cmap("cool")
			hbar = ax2.barh(word, num, color=my_cmap(num))
			label2 = [frequency]
			ax2.bar_label(hbar, label2, label_type="edge", fontsize=6, padding=6)
			st.pyplot(fig2, bbox_inches=0, transparent=False)





# for search_term in search:
# 	search_gloss = get_gloss(normalise(search_term)[0])
# 	st.metric(search_gloss, search_term, f"Frequency Rank: {vocab.index(search_term)+1}")

# st.write(f"{vocab.index(search)+1} {search} {search_gloss}")
# st.metric(search_gloss, search[0], f"Frequency Rank: {vocab.index(search[0])+1}")
# st.write(get_gloss(normalise(search)[0]))
# search = "ὀπτάω"
# antisearch = None#"Ζεύς"#
# sim = wv.most_similar(positive=search, negative=antisearch, topn=50)
# print(f"results for {search} : {get_gloss(normalise(search)[0])}")
# print()
# for result in sim:
#     norm = normalise(result[0])[0]
#     print(result[0], "\t", get_gloss(norm))


# df = pd.DataFrame({
#   'first column': [1, 2, 3, 4],
#   'second column': [10, 20, 30, 40]
# })

# df
