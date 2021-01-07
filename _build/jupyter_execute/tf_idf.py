#!/usr/bin/env python
# coding: utf-8

# # Exploring Vocabulary in *EarlyPrint* using Tf-Idf
# 
# by [John R. Ladd](https://jrladd.com)
# 
# ## Introduction
# 
# In this tutorial, you'll learn how to examine the vocabulary in *EarlyPrint* texts using Tf-Idf: Term Frequency–Inverse Document Frequency. This technique weights words according to how many times they are used in one text relative to how often they're used across an entire corpus.
# 
# Let's say, for example, that the word "temperance" appears about 18 times in the *The Faerie Queene*. Is that a lot or a little? How can we understand this wordcount not only in the context of Spenser's usage, but in the context of the word's appearance across a contemporary corpus? To understand whether this frequency is out of the ordinary, we need to know a word's **term frequency** (how many times does "temperance" appear in *The Faerie Queene*) as well as its **document frequency** (how many documents does "temperance" appear in at all). No doubt the word "the" appears in *The Faerie Queene* many many times (even in the title!), but it also appears in every single other English text. The fact that Spenser uses "the" a lot may not tell us much, but the fact that he uses "temperance" a lot could tell us something. Tf-Idf combines term frequency and document frequency into a score that can show us what words to pay attention to. It allows us to look at the frequencies of all the words in a single text highlighted against their presence or absence in a set of texts.
# 
# Because Tf-Idf gives us more information than raw term frequency, it's a common ingredient in machine learning, natural language processing, and text classification tasks. *EarlyPrint*'s own [Discovery Engine](https://earlyprint.org/lab/tool_discovery_engine.html) uses Tf-Idf as one of several measures for determining text similarity in our corpus. For much more information on what Tf-Idf is and how to use it, please refer to [Matt Lavin's *Programming Historian* tutorial on Tf-Idf](https://programminghistorian.org/en/lessons/analyzing-documents-with-tfidf), which was part of the inspiration for this post. However, it's important to remember that Tf-Idf is a heuristic, not a statistic. It's a simple, interpretable weighting system that gives a first sense of a word's relative importance or uniqueness. As Lavin and many others have suggested, Tf-Idf should therefore primarily be used as a first step in a research investigation, a way to ask new and interesting questions, rather than as a source of definitive claims. For more on the range of statistical techniques that can be used to investigate a word's relative prominence, start with this [blog post by Ted Underwood](https://tedunderwood.com/2011/11/09/identifying-the-terms-that-characterize-an-author-or-genre-why-dunnings-may-not-be-the-best-method/).
# 
# While Lavin's tutorial will get you very far with most modern texts, early modern printed texts have irregular spellings and other inconsistencies that may throw off word counts (i.e. We need the computer to know that "dog" and "dogge" are the same word). In this tutorial, you'll learn how to use *EarlyPrint*'s linguistically annotated texts to deal with those irregularities and produce more reliable Tf-Idf results.
# 
# ## Tools
# 
# Like the other tutorials in this series, this post presumes some introductory knowledge of Python. However, you need not write any code yourself. You can simply download this notebook and modify it to run on your own subcorpus of *EarlyPrint* texts.
# 
# For this notebook to work, you will need to have Python3 installed as well as the following libraries:
# 
# - [Jupyter Notebook](https://jupyter.org/install) (for running and reading the notebook)
# - [lxml](https://lxml.de/) (for parsing the XML)
# - [pandas](https://pandas.pydata.org/) (for organizing and displaying data)
# - [scikit-learn](https://scikit-learn.org/stable/) (for running Tf-Idf)
# 
# Now let's get started!
# 
# ## Step 1: Import Libraries
# 
# Once you've installed the necessary libraries, you need to **import** them into our current script. Often you don't need to import the whole library, just specific commands **from** that library. Our imports look like this:

# In[1]:


# These first two libraries are built in to Python, so we didn't need to install them
import glob
from collections import Counter
from lxml import etree # This is the only part of lxml we need
import pandas as pd # Import the entire pandas library, but use 'pd' as its nickname
from sklearn.feature_extraction.text import TfidfTransformer # Import only the Tf-Idf tool from scikit-learn


# ## Step 2: Open some *EarlyPrint* texts and get all the regularized tokens
# 
# As a sample, I've selected all the *EarlyPrint* texts available that were published in the year 1666. I did this because I'd like to find out about the distinctive vocabulary used in Margaret Cavendish's *Observations upon Experimental Philosophy* with *The Blazing World*, published in that year. But this method would work just as well for any grouping of texts.
# 
# In the current *EarlyPrint* repository of freely downloadable texts, there are 143 documents that were published in 1666. Using that set of texts, this script ran on a standard laptop in just three or four minutes. We recommend that you start with a corpus of similar size to get used to the process, at a max of, say, 250 texts. This code *will* run on thousands or tens of thousands of texts at a time, though it may take a very long time on your average laptop.
# 
# Here's the wonderful part: *EarlyPrint* texts are already tokenized (split up into individual words) and regularized (marked up with modernized spellings). So for our purposes here we simply need to open a file, get all its `<w>` tags for individual words, look to see if there is a regularized spelling, and put all of those words into a list. That may sound complicated, but the truth is that much of the hard work has already been done for us!
# 
# I've collected my subcorpus in a folder called `1666_texts`. So I can process every file in that folder, like so:

# In[2]:


# First you need a list of all files in your directory
files = glob.glob("1666_texts/*.xml") # THIS IS THE LINE YOU SHOULD MODIFY TO POINT AT THE TEXTS ON YOUR COMPUTER

# Create an empty lists to put all our texts into
all_tokenized = []

# Then you can loop through the files
for f in files:
    parser = etree.XMLParser(collect_ids=False) # Create a parse object that skips XML IDs (in this case they just slow things down)
    tree = etree.parse(f, parser) # Parse each file into an XML tree
    xml = tree.getroot() # Get the XML from that tree
    
    # Now we can use lxml to find all the w tags       
    word_tags = xml.findall(".//{*}w")
    # In this next line you'll do several things at once to create a list of words for each text
    # 1. Loop through each word: for word in word_tags
    # 2. Make sure the tag has a word at all: if word.text != None
    # 3. Get the regularized form of the word: word.get('reg', word.text)
    # 4. Make sure all the words are in lowercase: .lower()
    words = [word.get('reg', word.text).lower() for word in word_tags if word.text != None]
    # Then we add these results to a master list
    all_tokenized.append(words)


# Because of the affordances of the annotated *EarlyPrint* texts, we were able to skip a bunch of steps above. Accurate tokenization is handled by the `<w>` tags, and because there is a separate `<pc>` tag for punctuation, we don't have to worry about filtering that out either. By accessing the `<w>` tags directly and extracting the available regularized forms, we're now ready to move on to counting words.
# 
# ## Step 3: Counting Words
# 
# In [Lavin's tutorial](https://programminghistorian.org/en/lessons/analyzing-documents-with-tfidf), he uses the TfIdfVectorizer tool to tokenize and count words all together. Because our words are pretokenized, we can't combine these two steps. Instead, we need to make our own counts. We do this using a built-in method called `Counter()`.

# In[3]:


# We can count all the words in each text in one line of code
all_counted = [Counter(a) for a in all_tokenized]

# To prepare this data for Tf-Idf Transformation, we need to put into a different form, a DataFrame, using pandas.
df = pd.DataFrame(all_counted, index=[f.split("/")[1].split(".")[0] for f in files]).fillna(0)


# ## Step 4: Run Tf-Idf
# 
# Now that we have our word counts, we can use scikit-learn's `TfidfTransformer` function to run Tf-Idf across our entire corpus.

# In[4]:


# First we need to create an "instance" of the transformer, with the proper settings.
# We need to make sure that normalization is turned off
tfidf = TfidfTransformer(norm=None, sublinear_tf=True)
# I am choosing to turn on sublinear term frequency scaling, which takes the log of
# term frequencies and can help to de-emphasize function words like pronouns and articles. 
# You might make a different choice depending on your corpus.

# Once we've created the instance, we can "transform" our counts
results = tfidf.fit_transform(df)

# Make results readable using Pandas
readable_results = pd.DataFrame(results.toarray(), index=df.index, columns=df.columns) # Convert information back to a DataFrame

# Make the DataFrame columns the texts, and sort the DataFrame by 
# the words with the highest TF-IDF scores in the Cavendish text
# Use .head(30) to show only the top 30 terms
readable_results.T.sort_values(by=["A53049"], ascending=False).head(30)


# ## What did we learn about *Observations Upon Experimental Philosophy* and *The Blazing World*?
# 
# As I said before, Tf-Idf is a great way to generate research questions. In the chart above we can get a sense of some of the words Cavendish is using that aren't popular in other texts published that year.
# 
# We would naturally expect that character names and other terms specific to this book would score high, and certainly we see "empress," "bird-men," "worm-men," and of course "blazing-world." It's exciting, however, that these aren't the words that score highest. This may be not *so* surprising since the characters and figures of *The Blazing World* are mixed in with the philosophical and scientific terminology from the rest of the text, but the resulting list nonetheless includes many interesting words.
# 
# The first thing these results make me want to do is look more into Cavendish's use of terms that begin with "self-". Does she use the terms "self-motion" and "self-knowledge" commonly in her other works? What other writers are using these terms in the Restoration? Are other writers using the same terms but without the hyphenation? Are these terms specific to philosophical or scientific texts? All of these are directions to move in for future research, on just a single group of terms.
# 
# I also want to note and investigate the paired terms that come up in this list, especially exterior and interior, corporeal and incorporeal, and animate and inanimate. My next approach might be to find a way to examine pairs of opposed terms together.
# 
# A possible complaint about my approach here may be that I've not separated the words in *Observations upon Experimental Philosophy* from the words in *The Blazing World*. It's true that I've chosen to treat the physical book as the main unit of analysis here, but thanks to the XML markup available in these texts, you could fairly easily subdivide books into various texts and analyze them separately.
# 
# Finally, it's perhaps unsurprising that Cavendish's interest in "perception" floats to the top of this list. However, we can note that different forms of the word, including "perceptions," appear here. We might want to treat all forms of a word as a single term, and we can do so through a process called **lemmatization**. If we want to lemmatize our words before running Tf-Idf, there's more good news: *EarlyPrint* provides lemmas for all words just as it provides regularized forms. We could refactor our code to use the "lemma" attribute if we chose to, and all the versions of "perception" would be counted as a single term. \[n.b. This will work for "perceptions" but not for "perceptive." Lemmas revert to something like a dictionary headword, and so they usually retain their part of speech.\]
# 
# ## Conclusion
# 
# I hope that this tutorial will not only help you to run Tf-Idf on texts you care about but that it will convince you of the usefulness of Tf-Idf as a technique. Texts derived from early modern printed books present unique challenges to linguistic analyses like Tf-Idf that rely on consistent spelling, but the regularized texts in *EarlyPrint* can assist in overcoming some of those challenges.
# 
# If you have any questions, feel free to [contact me](mailto:jrladd@northwestern.edu).

# In[ ]:




