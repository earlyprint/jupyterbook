#!/usr/bin/env python
# coding: utf-8

# # Text Similarity
# 
# *EarlyPrint*'s [Discovery Engine](https://earlyprint.org/lab/tool_discovery_engine.html?which_to_do=find_texts&eebo_tcp_id=A43441&n_results=35&tfidf_weight=6&mallet_weight=6&tag_weight=6) allows you to find a set of texts similar to any text in our corpus. It does this by using some basic measures of text similarity, and it's easy to use if you're interested in finding similar texts across the entire early modern corpus.
# 
# But you might be interested in finding similarity across a smaller subset of the corpus. In this tutorial, we'll calculate similarity across the same set of 1666 texts that we used in the [TF-IDF tutorial](https://earlyprint.org/jupyterbook/tf_idf.html). You could easily do the same with any subset of texts that you've gathered using the [Metadata tutorial](https://earlyprint.org/jupyterbook/metadata.html).
# 
# This tutorial is meant as a companion to an explanation of text similarity that I wrote for *The Programming Historian*:
# 
# > [Understanding and Using Common Similarity Measures for Text Analysis](https://programminghistorian.org/en/lessons/common-similarity-measures)
# 
# The article uses the same 1666 corpus as its example, but here we'll work directly with the *EarlyPrint* XML instead of with plaintext files. For full explanations of the different similarity measures and how they're used, please use that piece as a guide.
# 
# First, we'll import necessary libraries. [n.b. In the *Programming Historian* tutorial, I use `scipy`'s implementation of pairwise distances. For simplicity's sake, here we're using Sci-kit Learn's built-in distance function.]

# In[1]:


import glob
import pandas as pd
from lxml import etree
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics import pairwise_distances
from collections import Counter


# Next we use `glob` to get our list of files and isolate the filekeys to use later. This is the complete list of texts we're working with in this example. You may have a different directory or filepath for your own files.

# In[2]:


# Use the glob library to create a list of file names
filenames = glob.glob("1666_texts/*.xml")
# Parse those filenames to create a list of file keys (ID numbers)
# You'll use these later on.
filekeys = [f.split('/')[-1].split('.')[0] for f in filenames]
print(filekeys)


# ## Get Features
# 
# In order to measure similarity between texts, you need features of those texts to measure. The [Discovery Engine](https://earlyprint.org/lab/tool_discovery_engine.html?which_to_do=find_texts&eebo_tcp_id=A43441&n_results=35&tfidf_weight=6&mallet_weight=6&tag_weight=6) calculates similarity across three distinct sets of features for the same texts: TF-IDF weights for word counts, LDA Topic Modeling results, and XML tag structures. As our example here, we'll use TF-IDF.
# 
# The code below is taken directly from the [TF-IDF Tutorial](https://earlyprint.org/jupyterbook/tf_idf.html), where you'll find a full explanation of what it does. We loop through each text, extract words, count them, and convert those counts to TF-IDF values. 
# 
# n.b. There are two key differences between the TF-IDF tutorial and this one. Below I am getting counts of **lemmas**, dictionary headwords, rather than simply regularized forms of the word. This allows us to group plurals or verb forms into a single term. Also, here we'll use [L2 normalization](https://en.wikipedia.org/wiki/Norm_(mathematics)#Euclidean_norm) on our TF-IDF transformation. Normalizing values helps us account for very long or very short texts that may skew our similarity results.

# In[3]:


# Create an empty lists to put all our texts into
all_tokenized = []

# Then you can loop through the files
for f in filenames:
    parser = etree.XMLParser(collect_ids=False) # Create a parse object that skips XML IDs (in this case they just slow things down)
    tree = etree.parse(f, parser) # Parse each file into an XML tree
    xml = tree.getroot() # Get the XML from that tree
    
    # Now we can use lxml to find all the w tags       
    word_tags = xml.findall(".//{*}w")
    # In this next line you'll do several things at once to create a list of words for each text
    # 1. Loop through each word: for word in word_tags
    # 2. Make sure the tag has a word at all: if word.text != None
    # 3. Get the lemmatized form of the word: word.get('reg', word.text)
    # 4. Make sure all the words are in lowercase: .lower()
    words = [word.get('lemma', word.text).lower() for word in word_tags if word.text != None]
    # Then we add these results to a master list
    all_tokenized.append(words)
    
# We can count all the words in each text in one line of code
all_counted = [Counter(a) for a in all_tokenized]

# To prepare this data for Tf-Idf Transformation, we need to put into a different form, a DataFrame, using pandas.
df = pd.DataFrame(all_counted, index=filekeys).fillna(0)

# First we need to create an "instance" of the transformer, with the proper settings.
# Normalization is set to 'l2'
tfidf = TfidfTransformer(norm='l2', sublinear_tf=True)
# I am choosing to turn on sublinear term frequency scaling, which takes the log of
# term frequencies and can help to de-emphasize function words like pronouns and articles. 
# You might make a different choice depending on your corpus.

# Once we've created the instance, we can "transform" our counts
results = tfidf.fit_transform(df)

# Make results readable using Pandas
readable_results = pd.DataFrame(results.toarray(), index=df.index, columns=df.columns) # Convert information back to a DataFrame
readable_results


# ## Calculate Distance
# 
# Below we'll calculate three different distance metrics---euclidean distance, "cityblock" distance, and cosine distance---and create DataFrames for each one. For explanations of each metric, and for a discussion of the difference between similarity and distance, you can refer to [The Programming Historian tutorial](https://programminghistorian.org/en/lessons/common-similarity-measures) which goes into these topics in detail.
# 
# Euclidean distance is first, because it's the default in `sklearn`:

# In[55]:


euclidean = pairwise_distances(results)
euclidean_df = pd.DataFrame(euclidean, index=df.index, columns=df.index)
euclidean_df


# Next is cityblock distance:

# In[56]:


cityblock = pairwise_distances(results, metric='cityblock')
cityblock_df = pd.DataFrame(cityblock, index=df.index, columns=df.index)
cityblock_df


# And finally cosine distance, which is usually (but not always) preferrable for text similarity:

# In[57]:


cosine = pairwise_distances(results, metric='cosine')
cosine_df = pd.DataFrame(cosine, index=df.index, columns=df.index)
cosine_df


# ## Reading Results
# 
# Now that we have DataFrames of all our distance results, we can easily look at the texts that are most similar (i.e. closest in distance) to a text of our choice. We'll use the same example as in the TF-IDF tutorial: Margaret Cavendish's *The Blazing World*.

# In[58]:


top5_cosine = cosine_df.nsmallest(6, 'A53049')['A53049'][1:]
print(top5_cosine)


# We now have a list of text IDs and their cosine similarities, but this list is hard to interpret without more information. We can use the techniques from the [Metadata tutorial](https://earlyprint.org/jupyterbook/metadata.html) to get a DataFrame of metadata for all the 1666 texts:

# In[59]:


# Get the full list of metadata files
# (You'll change this line based on where the files are on your computer)
metadata_files = glob.glob("../../epmetadata/header/*.xml")
nsmap={'tei': 'http://www.tei-c.org/ns/1.0'}

all_metadata = [] # Empty list for data
index = [] # Empty list for TCP IDs
for f in metadata_files: # Loop through each file
    tcp_id = f.split("/")[-1].split("_")[0] # Get TCP ID from filename
    if tcp_id in filekeys:
        metadata = etree.parse(f, parser) # Create lxml tree for metadata
        title = metadata.find(".//tei:sourceDesc//tei:title", namespaces=nsmap).text # Get title

        # Get author (if there is one)
        try:
            author = metadata.find(".//tei:sourceDesc//tei:author", namespaces=nsmap).text
        except AttributeError:
            author = None

        # Get date (if there is one that isn't a range)
        try:
            date = metadata.find(".//tei:sourceDesc//tei:date", namespaces=nsmap).get("when")
        except AttributeError:
            date = None

        # Add dictionary of data to data list
        all_metadata.append({'title':title,'author':author,'date':date})

        # Add TCP ID to index list
        index.append(tcp_id)


# Create DataFrame with data and indices
metadata_df = pd.DataFrame(all_metadata, index=index)
metadata_df


# And we can combine this with our cosine distance results to see the metadata for the texts most similar to *The Blazing World*:

# In[60]:


metadata_df.loc[top5_cosine.index, ['author','title','date']]


# You now have all the tools you need to creat your own mini [Discovery Engine](https://earlyprint.org/lab/tool_discovery_engine.html?which_to_do=find_texts&eebo_tcp_id=A43441&n_results=35&tfidf_weight=6&mallet_weight=6&tag_weight=6), one focused on exactly the texts you care most about. For more on how to interpret these results and things to watch out for when calculating similarity, refer again to [The Programming Historian](https://programminghistorian.org/en/lessons/common-similarity-measures).

# ## Visualizing Results
# 
# Now that we've calculated similarity among all the 1666 texts, it's helpful to explore further by visualizing those results in different ways. The first thing we need to do is import some simple graphing libraries.

# In[61]:


from matplotlib import pyplot as plt
import seaborn as sns


# ### Visualizing Words
# 
# In our results above, we found the text most similar to Cavendish's *Blazing World*: Boyle's *The Origin of Forms and Qualities*. (We know this similarity makes sense because Cavendish's *Blazing World* also includes a scientific treatise: *Observations upon Experimental Philosophy*.)
# 
# We might want to know which features---in this case individual words---"drive" the similarity between these two texts. We can do this by graphing all the words that appear in both texts according to their TF-IDF values.
# 
# Luckily, `pandas` lets us do so easily by selecting for the IDs of each text:

# In[62]:


# We need to "transpose" our results so that the texts are the columns and the words are the rows.
transformed_results = readable_results.T 

# Then we can graph by selecting our two texts
transformed_results.plot.scatter('A53049','A29017')


# You can see there are lots of words along the x- and y-axes that only appear in one text or the other. But there are plenty of words that appear in both, with varying TF-IDF scores.
# 
# The words we're interested in will have high TF-IDF scores in both texts---those are the words that most account for the high similarity score between these two books. We'd like to label those words on this graph.
# 
# First, we can subselect a set of words based on their TF-IDF scores in the two columns we care about. This will create a new, much smaller DataFrame:

# In[63]:


filtered_results = transformed_results[((transformed_results['A53049'] > 0.04) & (transformed_results['A29017'] > 0.005)) | ((transformed_results['A29017'] > 0.04) & (transformed_results['A53049'] > 0.005)) | ((transformed_results['A29017'] > 0.03) & (transformed_results['A53049'] > 0.03))] 
filtered_results


# These are the 26 words that drive the similarity between Cavendish and Boyle. You could adjust the threshold values in the above filter to get a bigger or smaller list of words.
# 
# And we can add these words as labels to our graph in order to see their relative TF-IDF weights:

# In[64]:


ax = transformed_results.plot.scatter('A53049','A29017')
for txt in filtered_results.index:
    x = transformed_results.A53049.loc[txt]
    y = transformed_results.A29017.loc[txt]
    ax.annotate(txt, (x,y))
plt.show()


# This graph tells us quite a bit about the similarity between these two texts. Words like "texture" and "corpuscles" have very high TF-IDF scores in Boyle and somewhat high scores in Cavendish. Words like "perception" and "sensitive" have very high scores in Cavendish and only somewhat high in Boyle. And a few select terms, like "microscope," "mineral," and "corporeal," have high scores in both texts. This scientific vocabulary is exactly what we might expect to see driving similarity between two early science texts.
# 
# ### Visualizing Texts
# 
# In addition to visualizing the words in just two texts, it can also be helpful to visualize all of our texts at once. We can create a visualization of our entire similarity matrix by making a heatmap: a chart where values are expressed as colors.
# 
# Using the [`seaborn`](https://seaborn.pydata.org/index.html) library, this is as easy as inputting our cosine distance DataFrame into a single function:

# In[65]:


f, ax = plt.subplots(figsize=(15, 10)) # This line just makes our heatmap a little bigger
sns.heatmap(cosine_df, cmap='coolwarm_r') # This function creates the heatmap


# Like the word-based visualization above, this heatmap of texts is also showing us a lot that we couldn't see just by looking at a table of numbers.
# 
# Mainly, we can see that most of the texts are not all that similar! Most of the values are showing up as blue, on the coolest end of our heatmap spectrum. [Look at the key on the right, and remember that when measuring distance higher values mean that two texts are farther apart.] This makes sense, as a group of texts published in just one year won't necessarily use much of the same vocabulary.
# 
# Down the center diagonal of our heatmap is a solid red line. This is where a text matches with itself in our matrix, and texts are always perfectly similar to themselves.
# 
# But all is not lost: notice that some of the points are much lighter blue. These texts are more similar than the dark blue intersections, so there is some variation in our graph. And a few points that are not along the diagonal are dark red, indicating quite low distance, i.e. very high similarity. You would need to use the metadata techniques we learned above to get more information, but it's possible that these very similar texts were written by the same author or are about the same topics.
# 
# Visualization doesn't answer all our questions, but it allows us to view similarity measures in a few different ways. And by seeing our data anew, we can generate more research questions that require further digging: a generative cycle.
