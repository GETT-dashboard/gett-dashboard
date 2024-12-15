
# Stereotype Analysis Methodology

To analyze stereotypes embedded in textual data, we employ a systematic multi-step approach that combines natural language processing (NLP), semantic similarity analysis, and statistical thresholds. This methodology aims to provide a structured evaluation of potential patterns or biases in descriptive or occupational texts. Below is an outline of the steps used:

---

## **Step 1: Text Lemmatization**

Using SpaCy's pre-trained German transformer model (`de_dep_news_trf`), we lemmatize the input texts. Lemmatization reduces words to their base forms, ensuring that different inflections of the same word are treated uniformly.

### **Code Snippet**
```python
import spacy
nlp = spacy.load("de_dep_news_trf")
doc = nlp(text)
lemmatized_words = [x.lemma_ for x in doc]
```

---

## **Step 2: Stopword and Punctuation Removal**

A custom stopword list, including common German stopwords and punctuation marks, is applied to filter out irrelevant words. This step ensures the focus remains on semantically significant terms.

### **Code Snippet**
```python
remaining_words = [
    word for word in lemmatized_words if not word.lower() in stopwords
]
```

---

## **Step 3: Semantic Similarity Analysis**

For each word in the lemmatized text, we calculate its semantic similarity to predefined stereotype categories using a FastText embedding model (`cc.de.300.bin`).

- **Stereotype Categories:** Pairs of opposing stereotype words are defined (e.g., *Heim* vs. *Arbeit*, *Familie* vs. *Karriere*).
- **Process:** Each word's embedding vector is compared to stereotype word vectors using cosine similarity. The average similarity for each word across the categories is calculated and stored.

### **Code Snippet**
```python
import fasttext
fasttext.util.download_model("de", if_exists="ignore")
model = fasttext.load_model("cc.de.300.bin")

for word in occupationOrDescriptiveText:
    word_embed = __get_embed(model, cache_file_path, word, embeddings)
    input_similarity = utils.cos_sim(input_embed, word_embed)
    similarities += [input_similarity]

average = round(statistics.fmean(similarities), 3)
```

### Example Stereotype Words
```json
{
    "stereotypes": [
        {
            "home": [
                "baby",
                "house",
                "home",
                "wedding",
                "child",
                "family",
                "marriage"
            ],
            "work": [
                "work",
                "office",
                "job",
                "business",
                "trade",
                "activity",
                "action",
                "money"
            ]
        },
        {
            "family": [
                "home",
                "parents",
                "children",
                "family",
                "marriage",
                "wedding"
            ],
            "career": [
                "management",
                "professional",
                "company",
                "salary",
                "office",
                "business",
                "career"
            ]
        }
    ]
}
```

---

## **Step 4: Stereotype Scoring**

We identify words with an average similarity score exceeding **0.1** toward one of the stereotype categories. Each occurrence contributes to a cumulative score:

- **+1** for words associated with the first stereotype (e.g., home or family).
- **-1** for words associated with the opposing stereotype (e.g., work or career).

The final stereotype score is the sum of these values for each person.

---

## **Step 5: Threshold for Stereotype Inclusion**

We include only individuals with a cumulative stereotype score exceeding a threshold of **3** in stereotype visualization and analysis. The threshold value is currently being further investigated to ensure its robustness and relevance.
