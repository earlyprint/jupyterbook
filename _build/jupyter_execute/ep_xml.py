#!/usr/bin/env python
# coding: utf-8

# # Parsing *EarlyPrint* XML Texts in Python
# 
# by [John R. Ladd](https://jrladd.com)
# 
# [Download this notebook!](https://earlyprint.org/assets/jupyter/ep_xml.ipynb)
# 
# ## Introduction
# 
# In this tutorial, you'll learn how to take advantage of the XML markup in *EarlyPrint* texts to subdivide and **parse** a single text or group of texts (that is, to use the formal encoding provided by XML to select textual features in which you’re especially interested).
# 
# *EarlyPrint* uses [TEI simplePrint](https://tei-c.org/release/doc/tei-p5-exemplars/html/tei_simplePrint.doc.html), an encoding standard derived from the [Text Encoding Initiative](https://tei-c.org/) guidelines and designed specifically for early modern and modern printed books. The standard includes many ways of marking up the structure of books, and we'll take advantage of a text's various TEI tags and attributes to transform it a number of useful ways.
# 
# For more on XML (which stands for eXtensible Markup Language), its long history, and the ways it has been used with early modern texts, consult [our introductory post on EEBO-TCP](https://earlyprint.org/intros/intro-to-eebo-tcp.html) which includes a helpful glossary and set of links at the bottom.
# 
# ## Tools
# 
# Like the other tutorials in this series, this post presumes some basic knowledge of Python. However, you need not write any code yourself. You can simply [download this notebook](https://earlyprint.org/assets/jupyter/ep_xml.ipynb) and modify it to run on your own *EarlyPrint* texts.
# 
# For this notebook to work, you will need to have Python3 installed as well as the following libraries:
# 
# - [Jupyter Notebook](https://jupyter.org/install) (for running and reading the notebook)
# - [lxml](https://lxml.de/) (for parsing the XML)
# - [pandas](https://pandas.pydata.org/) (for aggregating information and exporting as a CSV)
# 
# As an example text, I've chosen the original 1667 publication of *Paradise Lost* (ID A50919) which you can [find and download here](https://earlyprint.org/download/).
# 
# Now let's get started!
# 
# ## Step 1: Import Libraries
# 
# Once you've installed the necessary libraries, you need to **import** them into the current script. Often you don't need to import the whole library, just specific commands **from** that library. Your imports should look like this:

# In[1]:


from lxml import etree # This is the only part of lxml we need
import pandas as pd # You won't need pandas until the very end of this tutorial
from collections import Counter # A built-in tool for counting items


# ## Step 2: Read a Text and Create an "etree" object
# 
# In order for lxml to understand the entire tree structure of your XML text, you'll need to load all of the text in a special `etree` object (abbreviated from Element Tree). When a computer reads an XML text, it's called "parsing," and so you'll be using lxml's `parse()` function. Once you do, you can query the object for specific XML tags.
# 
# ***For the examples in this notebook to run as expected, you’ll need to place the file you want to explore in the same directory as the notebook.***  You could place it elsewhere, but this would require an adjustment in the code.

# In[2]:


# First create a parser object. It will work faster if you tell it not to collect IDs.
parser = etree.XMLParser(collect_ids=False)

# Parse your XML file into a "tree" object
tree = etree.parse('A50919.xml', parser)

# Get the XML from the tree object
paradiselost = tree.getroot()


# ## Step 3: Individual Words
# 
# There are many ways to parse XML documents. The most common and robust is a query language called [XPath](https://www.w3schools.com/xml/xpath_intro.asp), which allows you to create various *expressions* to select parts of an XML document.
# 
# `lxml` uses a simplified version of XPath called [ElementPath](https://effbot.org/zone/element-xpath.htm), which we recommend for beginners. Most of the expressions you see from here forward use `lxml`'s default ElementPath expressions. Keep in mind that if you want to construct very complex queries of a document, you may want to switch to XPath at some point down the road.
# 
# The easiest thing to do with an *EarlyPrint* document is to tokenize it into a list of words. *EarlyPrint* texts wrap every word in a `<w>` tag, and it keeps all the punctuation separate in `<pc>` tags. To get all the words in *Paradise Lost*, you simply use ElementPath to ask for the contents of all the `<w>` tags.
# 
# An ElementPath query usually begins with `.//`: the dot refers to your current location in the XML tree, and the two slashes indicate that you'd like to search anywhere below that in the tree. Often, as with `<w>` tags, you want to start at the highest level of the document, the *root* of the element tree, and search anywhere within the document.
# 
# You also need to account for a [namespace](https://en.wikipedia.org/wiki/XML_namespace), usually enclosed within brackets in an ElementPath query. Every *EarlyPrint* document has a namespace, and it will almost always be the default TEI namespace: <https://tei-c.org/ns/1.0/>. You could write your ElementPath query as `".//{https://tei-c.org/ns/1.0/}w"`, but that could get tedious to type each time. To make your code more readable and easier to type, you can create a dictionary (usually named `nsmap`) that refers to all the namespaces you want to use in your document. Then you can refer to `nsmap` within any lxml method, as you'll see below.
# 
# Finally, after the namespace you can include the notation for the tag you want. In this case, you simply want all `w` tags. Your code will look like this:

# In[3]:


# Create your nsmap for the 'tei' namespace
# You only need to do this once in your script,
# but you'll refer back to this variable throughout
# the rest of this notebook.
nsmap={'tei': 'http://www.tei-c.org/ns/1.0'}


# Use the findall() method to get a list of all possible matches
# A similar method, find(), will only return the first match
all_word_tags = paradiselost.findall(".//tei:w", namespaces=nsmap)

# Once you have all the tags, you can get the text inside them with the .text attribute

all_words = [w.text for w in all_word_tags]
print(all_words[:100]) # This will print the first 100 words


# Voila! A list of the first 100 words in *Paradise Lost*! (`all_words` includes *all* the words, and you can display all of them simply by removing `[:100]` from the `print()` function.)
# 
# But *EarlyPrint* documents contain much more information than just the words themselves. For each `<w>` tag, *EarlyPrint* includes XML attributes for part of speech, lemma (dictionary headword), and sometimes a regularized spelling. 
# 
# Once we have the tags for each word, you can access attributes in two ways. You can treat an attribute as if it were a dictionary key, and type `tag_name.attrib['attribute_name']`. Or you can use the `get()` method: `tag_name.get('attribute_name')`.
# 
# If you wanted only regularized spellings, you could obtain them by capturing the `'reg'` attribute with either of these methods. But because not every tag includes a `'reg'` attribute, we want to be sure to get the original word, i.e. `w.text`, when there is no regularized spelling available. To do this, `get()` is preferred because it allows you to pass a second argument as a default value. When you run `tag_name.get('attribute_name', tag_name.text)`, if there is no `'attribute_name'`, the function will simply return the text content of the element.
# 
# This allows you to write a simple script to get all regularized spellings:

# In[4]:


all_regularized = [w.get('reg', w.text) for w in all_word_tags]
print(all_regularized[:100])


# Now you have the same list, but words like "Heav'nly" have been regularized to "heavenly." This is very useful if you're looking for accurate word counts. (Full disclosure: our regularization routine, from [MorphAdorner](http://morphadorner.northwestern.edu/morphadorner/), was solid but not infallible: very infrequently the regularizations — and, thence, the lemmatizations -- are mistaken, so treat them with slight caution.)
# 
# Let's take a step back to better understand how this works by concentrating on that word, "Heav'nly." From the list above you can tell it's the 96th word in the list, which means you can access its tag at index 95:

# In[5]:


heavenly_tag = all_word_tags[95]

# You can print out the entire tag using the .tostring() method:

print(etree.tostring(heavenly_tag))


# The printout above shows the full `w` element for the word "Heav'nly," with all its attributes. You can see the namespace in `xmlns`, and the id number in `xml:id`. But the main attributes a researcher will care about are `lemma`, `pos`, and `reg`, which contain the relevant linguistic markup.
# 
# As you saw above, you can get an element's text content by accessing `element.text` and the content of an attribute by accessing `element.attrib["attribute"]` or `element.get("attribute")`. You can use this syntax get all the relevant information for "Heav'nly":

# In[6]:


print(heavenly_tag.text, heavenly_tag.attrib["reg"], heavenly_tag.attrib["lemma"], heavenly_tag.attrib["pos"])


# From the above you can see that the original spelling of the word is "Heav'nly," its regularized spelling is "heavenly," its lemma is also "heavenly," and its part of speech is "j" for adjective.
# 
# You can now extrapolate from this to get all the linguistic information for the first ten words of *Paradise Lost*. But this time you can use `.get()` instead of `.attrib`:

# In[7]:


# Every w element will have a lemma and pos attribute
# But not every one will have a reg attribute!
# Don't forget to add a default value for "reg" to avoid
# any errors.

all_word_info = [(w.text, w.attrib.get("reg", w.text), w.attrib.get("lemma"), w.attrib.get("pos")) for w in all_word_tags[:10]]
print(all_word_info)


# Now that you've done a little more investigation into the structure of `<w>` elements, you can use them to get only a specific type of word. For example, you could use the *EarlyPrint* part of speech tagging to get all the nouns in *Paradise Lost*:
# 
# [n.b. *EarlyPrint* uses the [NUPOS](https://earlyprint.org/intros/intro-to-nupos.html) tagset, which uses helpfully fine-grained part-of-speech tags. To find all the nouns, you can simply look for all tags that begin with the letter "n."]

# In[8]:


all_nouns = [w.text for w in all_word_tags if w.get('pos').startswith('n')]
print(all_nouns[:100])


# Note that the first 100 words in this list skip over all the other parts of speech to give only the nouns. You could combine this with the regularized word capture above to get only regularized nouns, or only lemmatized verbs, etc.
# 
# You can also aggregate all nouns by their frequency with Python's built-in Counter (which you imported above) and output a list of the top 10 most frequent nouns (but keep in mind that the spellings are *not* regularized):

# In[9]:


Counter(all_nouns).most_common()[:10]


# ## Step 4: Lines, Stanzas, and Sentences
# 
# But what if you want chunks larger than a single word? What if you wanted to examine *Paradise Lost* by its lines or sentences?
# 
# If you're examining verse, lines and stanzas are particularly easy. Lines are marked with `<l>` tags and stanzas are marked with `<lg>` tags (for line group). But be careful with `<lg>` tags: not every group of lines constitutes a stanza! In the case of *Paradise Lost*, `<lg>` elements refer to Milton's long verse paragraphs.
# 
# Begin by breaking *Paradise Lost* into lines, using `<l>` tags instead of the `<w>`'s (as well as the same namespace we used above):

# In[10]:


all_line_tags = paradiselost.findall(".//tei:l", namespaces=nsmap)

# Now that we have the lines, we can find each word in each line

words_by_line = [[w.text for w in l.findall(".//tei:w", namespaces=nsmap)] for l in all_line_tags]
print(words_by_line[:20]) # Print only the first 20 lines


# The code above yields a *list of lists*, where each line is represented as a list of words. This could be very useful for certain kinds of line-level analysis. But if you wanted to look at the lines as *strings* instead, you could join them:

# In[11]:


for line in all_line_tags[:20]: #Only the first 20 lines
    print(' '.join([w.text for w in line.findall(".//tei:w", namespaces=nsmap)]))


# Those strange symbols you see are **gaps**, places where the TCP transcribers couldn't confirm the correct character or word. The [*EarlyPrint* Library site](https://texts.earlyprint.org/exist/apps/shc/home.html) is set up to enable public-spirited scholars to repair these defects on behalf of the research community: visit anytime if you'd like to correct gaps like these!
# 
# You'll also notice that, with the exception of apostrophes, there is no punctuation in the above passage. That's because you only asked for `<w>` tags, and the punctuation is all in `<pc>` tags. An easy way to remedy this is to ask lxml to return all *child* elements of the line, those tags—like those for words *or* punctuation—that are directly below it in the element tree. Since lxml treats an element as a list, this is as simple as omitting the second `findall()` method:

# In[12]:


for line in all_line_tags[:20]: #Only the first 20 lines
    print(' '.join([child.text for child in line])) # Without findall(), lxml returns every child of l


# Now all the punctuation is back! Our simple `join()` method is putting in unnecessary spaces, but you can always fix that with some custom logic. You'd need to write a rule that only adds a space after a word if the next element is *not* a punctuation mark.
# 
# By extending what you've done above, you can also capture text by line group or stanza. For example, you can find all the words in the first line group—that is, the first verse paragraph:

# In[13]:


# Since you’re seeking only the first line group, we can use find() instead of findall()
first_line_group = paradiselost.find(".//tei:lg", namespaces=nsmap)

lg_words = [w.text for w in first_line_group.findall(".//tei:w", namespaces=nsmap)]
print(lg_words)


# But how do you find sentences instead of lines or stanzas? Because sentences typically end with punctuation, *EarlyPrint* texts mark sentence boundaries as *attributes* on `<pc>` (i.e., punctuation) tags. To find the end of all sentences, you must look for `<pc>` elements that have an attribute "unit" whose value is "sentence." In the XML, that might look like:
# 
# ```
# <pc unit="sentence">.</pc>
# ```
# 
# To get sentences, you must find these markers and all the words in between them. And to do that, you first need to find a list of all `<w>` tags and all `<pc>` tags in order.
# 
# This is where you'll run into the limitations of ElementPath, which doesn't easily allow you to search for two types of tags at once. Luckily, you can use [XPath](https://www.w3schools.com/xml/xpath_intro.asp) to search for both at the same time. The syntax for XPath is very similar to the ElementPath queries above. You should omit the `.` before `//`, and you can use the pipe `|` symbol to combine two queries. You can use the same `nsmap` dictionary you used above to account for the `tei` namespace.
# 
# Once you've run the XPath query, you can loop through every tag and and put its contents into a list for each sentence. And when you reach the tag with the `unit='sentence'` attribute, you'll know to start over with a fresh list. Here's the example code:

# In[14]:


# An XPath query to find all <w> and <pc> tags, with
# special handling of the XML namespace.
w_and_pc = paradiselost.xpath("//tei:w|//tei:pc", namespaces=nsmap)

all_sentences = [] # A master list to hold all sentences
new_sentence = [] # An empty list for the first sentence

# Loop through every tag (for the sample, I've done just the first 500 tags)
for tag in w_and_pc[:500]:
    # Test to see if a tag has a "unit" attribute and
    # if the value of that attribute is "sentence."
    # This will be the end of your sentence.
    if 'unit' in tag.attrib and tag.get('unit') == 'sentence':
        if tag.text != None: # Sometimes these tags are empty, but other times they contain a period
            # If there is a punctuation mark, add it to the sentence list
            new_sentence.append(tag.text)
        # Add the whole sentence to the master list
        all_sentences.append(new_sentence)
        # Start over with a fresh list for a new sentence
        new_sentence = []
    # If the tag is not at the end of a sentence, we can simply add its contents to the list
    else:
        new_sentence.append(tag.text)
        
print(all_sentences)


# There you have it! A bit more complex than the other examples, but just as successful. You'll notice the first few "sentences" are actually from the book's front matter, but then it gets going with the first few sentences in the poem. *EarlyPrint* texts will attempt to segment all text into sentences, even when there aren't complete sentences to be had, such as on title pages.
# 
# ## Other Divisions
# 
# You've now divided up the poem using various linguistic categories: words, parts of speech, lines, sentences. But what about other divisions in books? Most books have title pages, some have dedications and prefaces, and others have many subsections or contain multiple texts.
# 
# *EarlyPrint* texts use `<div>` tags to account for these kinds of divisions. `<div>` tags usually have a `type` that tells you what kind of division you're working with. Some divisions, as you're about to see, are numbered with an `n` attribute. You can easily find all the divisions in a text and list their attributes:

# In[15]:


all_divs = paradiselost.findall(".//tei:div", namespaces=nsmap) # Find all the divs

for div in all_divs: # Loop through each div
    print(div.attrib) # Print out a dictionary of its attributes


# From the above we can see that *Paradise Lost* has 11 div elements. All of those elements have a `type` attribute and an `id` attribute (with a special namespace). You can ignore the `id` attribute for now.
# 
# One of those `<div>` elements is the title page. You can get all the words on the title page by zeroing in on that specific `type` using ElementPath syntax for attributes. That notation uses brackets and the `@` symbol before the attribute name and encloses its values in single quotes, like this: `[@type='title_page']`. You can add this to an ElementPath query to find the title page:

# In[16]:


title_page = paradiselost.find(".//tei:div[@type='title_page']", namespaces=nsmap)

words_on_title_page = [w.text for w in title_page.findall(".//tei:w", namespaces=nsmap)]
print(words_on_title_page)


# You can use this same logic for any kind of `<div>`!
# 
# There are 10 more `<div>` tags in this text, all with the type "book." That's because this first publication of *Paradise Lost* was divided into ten books, and the XML retains that structure. (The second publication of *Paradise Lost* was divided into 12 books, but that's a story for a different XML document.) You can easily find a specific book by searching for multiple attributes in one query:

# In[17]:


book2 = paradiselost.find(".//tei:div[@type='book'][@n='2']", namespaces=nsmap) #Find only Book 2

words_in_book2 = [w.text for w in book2.findall(".//tei:w", namespaces=nsmap)] # Get all the words in Book 2
print(words_in_book2[:100]) # Print just the first 100 words


# Or you can create a list of all books and categorize words by the book they appear in:

# In[18]:


all_books = paradiselost.findall(".//tei:div[@type='book']", namespaces=nsmap) # Find all of the books

# In each book, get all of the words as a list
words_by_book = [[w.text for w in book.findall(".//tei:w", namespaces=nsmap)] for book in all_books]

# Print the first 10 words in each book
for book in words_by_book:
    print(book[:10])


# ## Exporting and Sharing
# 
# Now that you know a little bit about how to parse *EarlyPrint* XML files, it's likely you'll want to export some of this information out of a Python environment into a format that can easily be shared. One simple way of exporting information is as a CSV, or comma-separated value file. CSVs can easily be read by most spreadsheet applications, like Excel or Google Sheets, and are therefore useful for sharing information easily. There are many ways to work with CSV files in Python, but the [Pandas](https://pandas.pydata.org/) data science library provides one of the simplest interfaces. You already imported pandas at the beginning of this tutorial and named it `pd` for short.
# 
# In this next bit of code, you'll combine what you've learned from the previous examples to get a CSV file of the counts for every noun in each book of *Paradise Lost*.

# In[19]:


# Begin by getting all regularized nouns in every book as a list
nouns_by_book = [[w.get("reg", w.text) for w in book.findall(".//tei:w", namespaces=nsmap) if w.get("pos").startswith("n")] for book in all_books]

# Count each book's wordlist
noun_counts_by_book = [Counter(noun_list) for noun_list in nouns_by_book]

# Create a list of Book names to use as labels
book_names = [f"Book {number}" for number in range(1,11)]

# Create a Pandas DataFrame
# Set the index to the list of book_names
# Fill any empty "cells" with 0 (if a word appears in some books but not others)
noun_counts_df = pd.DataFrame(noun_counts_by_book, index=book_names).fillna(0)

# "Transpose" your DataFrame so that words are rows and books are columns
noun_counts_df = noun_counts_df.T

# Export your DataFrame to a CSV file.
noun_counts_df.to_csv("pl_noun_counts_by_book.csv")


# The code above will save a CSV file to the same directory where this notebook resides. You can now take that CSV and use it any way you choose. You might start by loading it into Excel or Google Sheets and sorting it by column to see the most frequent nouns in each book.

# ## Conclusion
# 
# You've now run through some of the basic ways to subdivide *EarlyPrint* XML documents. If you have worked through the tutorial on [TF-IDF](https://earlyprint.org/notebooks/tf_idf.html), you will have noted that *Observations on Experimental Philosophy* and *The Blazing World* were contained in the same physical book, and therefore were both part of the same XML file. Now you have some tools and approaches with which to subdivide and analyze the two texts separately.
# 
# And there are many more ways to subdivide texts according to the principles you've just learned. In the book divisions above, the word lists include headings that say, for example "PARADISE LOST BOOK I." Those words are from headers and aren't part of the main text of the poem. They're contained in `<head>` tags, which you're now better equipped to find and avoid, if you so choose.
# 
# If you want to try some of these investigative routines on a different text—say, Aphra Behn's *Oroonoko* or Thomas Hobbes's *Leviathan*—you can find them by searching [the *EarlyPrint* download page](https://earlyprint.org/download/).
# 
# XML documents can be complex, but we hope the TEI simplePrint markup in *EarlyPrint* will make it easier for you to find and analyze exactly the parts of the texts that interest you.
